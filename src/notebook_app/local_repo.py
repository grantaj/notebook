from __future__ import annotations

import asyncio
import hashlib
import re
import subprocess
from pathlib import Path

from .github import GitHubError, GitHubPage


class LocalRepo:
    """Repository adapter for a normal local Git worktree."""

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        if not (self.root / ".git").exists():
            raise RuntimeError(f"{self.root} is not a Git worktree")
        self.repo = self._repo_name()
        self.branch = self._git("branch", "--show-current").strip() or "HEAD"

    async def close(self) -> None:
        return None

    async def markdown_paths(self) -> list[str]:
        return await asyncio.to_thread(self._markdown_paths)

    async def get_page(self, path: str) -> GitHubPage:
        return await asyncio.to_thread(self._get_page, path)

    async def put_page(
        self,
        path: str,
        content: str,
        message: str,
        sha: str | None = None,
    ) -> None:
        await asyncio.to_thread(self._put_page, path, content, message, sha)

    def _markdown_paths(self) -> list[str]:
        ignored = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache"}
        paths = []
        for candidate in self.root.rglob("*.md"):
            relative = candidate.relative_to(self.root)
            if any(part in ignored or part.startswith(".") for part in relative.parts[:-1]):
                continue
            paths.append(relative.as_posix())
        return sorted(paths, key=lambda p: (p.lower() != "readme.md", p.lower()))

    def _get_page(self, path: str) -> GitHubPage:
        target = self._target(path)
        if not target.is_file():
            raise GitHubError(f"{path} does not exist")
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise GitHubError(f"{path} is not a UTF-8 file") from exc
        return GitHubPage(path=path, content=content, sha=self._sha(content))

    def _put_page(self, path: str, content: str, message: str, sha: str | None) -> None:
        target = self._target(path)
        if target.exists() and sha is not None:
            current = target.read_text(encoding="utf-8")
            if self._sha(current) != sha:
                raise GitHubError(f"{path} changed since it was opened")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        relative = target.relative_to(self.root).as_posix()
        self._git("add", "--", relative)
        status = self._git("diff", "--cached", "--quiet", "--", relative, check=False)
        if status.returncode == 0:
            return
        result = self._git("commit", "-m", message, "--", relative, check=False)
        if result.returncode != 0:
            raise GitHubError(result.stderr.strip() or result.stdout.strip() or "git commit failed")

    def _target(self, path: str) -> Path:
        if not path.lower().endswith(".md"):
            raise GitHubError("Notebook pages must be Markdown files")
        target = (self.root / path).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise GitHubError("Page path escapes the repository") from exc
        return target

    def _repo_name(self) -> str:
        result = self._git("remote", "get-url", "origin", check=False)
        if result.returncode == 0:
            remote = result.stdout.strip()
            match = re.search(r"github\.com[/:]([^/]+/[^/]+?)(?:\.git)?$", remote)
            if match:
                return match.group(1)
        return self.root.name

    @staticmethod
    def _sha(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _git(self, *args: str, check: bool = True):
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "git command failed"
            raise RuntimeError(message)
        return result
