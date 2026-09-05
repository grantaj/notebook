from __future__ import annotations

import asyncio
from pathlib import Path


class CodexError(RuntimeError):
    pass


class CodexModel:
    """One-shot Codex CLI bridge for the first self-hosted Notebook milestone.

    Each turn is reconstructed from the durable notebook page rather than a hidden
    Codex session. `codex exec` reuses the user's existing CLI authentication and
    runs read-only; `--ephemeral` avoids creating rollout state that Notebook would
    then have to treat as another source of truth.
    """

    def __init__(self, cwd: Path | None = None) -> None:
        self.cwd = cwd

    async def close(self) -> None:
        return None

    async def reply(
        self,
        *,
        repo: str,
        path: str,
        page: str,
        user_text: str,
        instructions: str | None = None,
    ) -> str:
        prompt = self._prompt(repo, path, page, user_text, instructions)
        try:
            proc = await asyncio.create_subprocess_exec(
                *self._command(),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.cwd) if self.cwd else None,
            )
        except FileNotFoundError as exc:
            raise CodexError("Codex CLI is not installed or not on PATH") from exc

        stdout, stderr = await proc.communicate(prompt.encode())
        answer = stdout.decode(errors="replace").strip()
        diagnostics = stderr.decode(errors="replace").strip()

        if proc.returncode != 0:
            detail = diagnostics or answer or "no diagnostic output"
            if len(detail) > 4000:
                detail = detail[-4000:]
            raise CodexError(f"codex exec failed ({proc.returncode}): {detail}")
        if not answer:
            detail = diagnostics or "no output"
            raise CodexError(f"Codex completed without an assistant message: {detail}")
        return answer

    @staticmethod
    def _command() -> tuple[str, ...]:
        return ("codex", "exec", "--ephemeral", "--sandbox", "read-only", "-")

    @staticmethod
    def _prompt(
        repo: str,
        path: str,
        page: str,
        user_text: str,
        instructions: str | None,
    ) -> str:
        parts = [
            "You are continuing a repository-backed Notebook page.",
            (
                "Treat the page as the foreground intellectual object; repository mechanics "
                "are secondary."
            ),
            (
                "Answer the user's question directly in useful Markdown. Do not claim repository "
                "changes were made."
            ),
            f"Repository: {repo}",
            f"Current page: {path}",
        ]
        if instructions:
            parts.extend(["Repository instructions:", instructions])
        parts.extend(["Current page contents:", page, "User:", user_text])
        return "\n\n".join(parts)
