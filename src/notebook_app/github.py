from __future__ import annotations

import base64
from dataclasses import dataclass
from urllib.parse import quote

import httpx


class GitHubError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitHubPage:
    path: str
    content: str
    sha: str


class GitHubRepo:
    def __init__(self, token: str, repo: str, branch: str = "main") -> None:
        self.repo = repo
        self.branch = branch
        self._client = httpx.AsyncClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def markdown_paths(self) -> list[str]:
        response = await self._client.get(
            f"/repos/{self.repo}/git/trees/{quote(self.branch, safe='')}",
            params={"recursive": "1"},
        )
        self._check(response)
        data = response.json()
        paths = [
            item["path"]
            for item in data.get("tree", [])
            if item.get("type") == "blob" and item.get("path", "").lower().endswith(".md")
        ]
        return sorted(paths, key=lambda p: (p.lower() != "readme.md", p.lower()))

    async def get_page(self, path: str) -> GitHubPage:
        response = await self._client.get(
            f"/repos/{self.repo}/contents/{quote(path, safe='/')}",
            params={"ref": self.branch},
        )
        self._check(response)
        data = response.json()
        if data.get("type") != "file" or data.get("encoding") != "base64":
            raise GitHubError(f"{path} is not a UTF-8 file")
        raw = base64.b64decode(data["content"])
        return GitHubPage(path=path, content=raw.decode("utf-8"), sha=data["sha"])

    async def put_page(self, path: str, content: str, message: str, sha: str | None = None) -> None:
        payload: dict[str, str] = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        if sha is not None:
            payload["sha"] = sha
        response = await self._client.put(
            f"/repos/{self.repo}/contents/{quote(path, safe='/')}", json=payload
        )
        self._check(response)

    @staticmethod
    def _check(response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            detail = response.json().get("message", response.text)
        except ValueError:
            detail = response.text
        raise GitHubError(f"GitHub {response.status_code}: {detail}")
