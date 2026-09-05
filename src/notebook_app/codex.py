from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class CodexError(RuntimeError):
    pass


@dataclass
class _Turn:
    done: asyncio.Event = field(default_factory=asyncio.Event)
    messages: list[str] = field(default_factory=list)
    error: str | None = None


class CodexModel:
    """Small async client for `codex app-server` over its default JSONL stdio transport."""

    def __init__(self, cwd: Path | None = None) -> None:
        self.cwd = cwd
        self._proc: asyncio.subprocess.Process | None = None
        self._reader: asyncio.Task[None] | None = None
        self._stderr: asyncio.Task[None] | None = None
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._turns: dict[str, _Turn] = {}
        self._completed_turns: dict[str, dict[str, Any]] = {}
        self._threads: dict[str, str] = {}
        self._next_id = 1
        self._write_lock = asyncio.Lock()

    async def start(self) -> None:
        if self._proc is not None:
            return
        try:
            self._proc = await asyncio.create_subprocess_exec(
                "codex",
                "app-server",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.cwd) if self.cwd else None,
            )
        except FileNotFoundError as exc:
            raise CodexError("Codex CLI is not installed or not on PATH") from exc

        self._reader = asyncio.create_task(self._read_stdout())
        self._stderr = asyncio.create_task(self._drain_stderr())
        await self._request(
            "initialize",
            {
                "clientInfo": {
                    "name": "notebook",
                    "title": "Notebook",
                    "version": "0.1.0",
                }
            },
        )
        await self._notify("initialized", {})

    async def close(self) -> None:
        proc = self._proc
        self._proc = None
        if proc is not None and proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), 2)
            except TimeoutError:
                proc.kill()
                await proc.wait()
        for task in (self._reader, self._stderr):
            if task is not None:
                task.cancel()
        self._reader = None
        self._stderr = None

    async def reply(
        self,
        *,
        repo: str,
        path: str,
        page: str,
        user_text: str,
        instructions: str | None = None,
    ) -> str:
        await self.start()
        thread_id = await self._thread_for(path)
        prompt = self._prompt(repo, path, page, user_text, instructions)
        result = await self._request(
            "turn/start",
            {
                "threadId": thread_id,
                "input": [{"type": "text", "text": prompt}],
                "approvalPolicy": "never",
                "sandboxPolicy": {"type": "readOnly"},
            },
        )
        turn_id = result.get("turn", {}).get("id")
        if not turn_id:
            raise CodexError("Codex did not return a turn id")

        turn = self._turns.setdefault(turn_id, _Turn())
        completed = self._completed_turns.pop(turn_id, None)
        if completed is not None:
            self._complete_turn(turn, completed)
        await turn.done.wait()
        self._turns.pop(turn_id, None)
        if turn.error:
            raise CodexError(turn.error)
        answer = "\n\n".join(part.strip() for part in turn.messages if part.strip()).strip()
        if not answer:
            raise CodexError("Codex completed without an assistant message")
        return answer

    async def _thread_for(self, path: str) -> str:
        existing = self._threads.get(path)
        if existing:
            return existing
        params: dict[str, Any] = {
            "approvalPolicy": "never",
            "sandbox": "readOnly",
            "serviceName": "notebook",
        }
        if self.cwd:
            params["cwd"] = str(self.cwd)
        result = await self._request("thread/start", params)
        thread_id = result.get("thread", {}).get("id")
        if not thread_id:
            raise CodexError("Codex did not return a thread id")
        self._threads[path] = thread_id
        return thread_id

    async def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        loop = asyncio.get_running_loop()
        future: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending[request_id] = future
        await self._send({"method": method, "id": request_id, "params": params})
        try:
            return await future
        finally:
            self._pending.pop(request_id, None)

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        await self._send({"method": method, "params": params})

    async def _send(self, message: dict[str, Any]) -> None:
        proc = self._proc
        if proc is None or proc.stdin is None:
            raise CodexError("Codex app-server is not running")
        raw = json.dumps(message, separators=(",", ":")) + "\n"
        async with self._write_lock:
            proc.stdin.write(raw.encode())
            await proc.stdin.drain()

    async def _read_stdout(self) -> None:
        assert self._proc is not None and self._proc.stdout is not None
        try:
            while line := await self._proc.stdout.readline():
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "id" in message and "method" not in message:
                    future = self._pending.get(message["id"])
                    if future is not None and not future.done():
                        if "error" in message:
                            future.set_exception(CodexError(str(message["error"])))
                        else:
                            future.set_result(message.get("result") or {})
                    continue
                method = message.get("method")
                params = message.get("params") or {}
                if method == "item/completed":
                    item = params.get("item") or {}
                    if item.get("type") == "agentMessage" and item.get("text"):
                        turn_id = params.get("turnId")
                        if turn_id:
                            self._turns.setdefault(turn_id, _Turn()).messages.append(item["text"])
                elif method == "turn/completed":
                    turn_data = params.get("turn") or {}
                    turn_id = turn_data.get("id")
                    if turn_id in self._turns:
                        self._complete_turn(self._turns[turn_id], turn_data)
                    elif turn_id:
                        self._completed_turns[turn_id] = turn_data
        except asyncio.CancelledError:
            raise
        finally:
            error = CodexError("Codex app-server stopped unexpectedly")
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(error)
            for turn in self._turns.values():
                if not turn.done.is_set():
                    turn.error = str(error)
                    turn.done.set()

    @staticmethod
    def _complete_turn(turn: _Turn, turn_data: dict[str, Any]) -> None:
        status = turn_data.get("status")
        if status != "completed":
            error = turn_data.get("error") or {}
            turn.error = error.get("message") or f"Codex turn ended with status {status}"
        turn.done.set()

    async def _drain_stderr(self) -> None:
        assert self._proc is not None and self._proc.stderr is not None
        try:
            while await self._proc.stderr.readline():
                pass
        except asyncio.CancelledError:
            raise

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
            "Treat the page as the foreground intellectual object; repository mechanics "
            "are secondary.",
            "Answer the user's question directly in useful Markdown. Do not claim repository "
            "changes were made.",
            f"Repository: {repo}",
            f"Current page: {path}",
        ]
        if instructions:
            parts.extend(["Repository instructions:", instructions])
        parts.extend(["Current page contents:", page, "User:", user_text])
        return "\n\n".join(parts)
