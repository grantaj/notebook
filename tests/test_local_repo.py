from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import pytest

from notebook_app.github import GitHubError
from notebook_app.local_repo import LocalRepo


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init")
    git(root, "config", "user.name", "Notebook Test")
    git(root, "config", "user.email", "notebook@example.invalid")
    (root / "notebook.md").write_text("# Building Notebook\n\nFirst thought.\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "design.md").write_text("# Parser architecture\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-m", "initial")
    return root


def test_local_repo_discovers_titles_and_commits_page(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    repo = LocalRepo(root)

    async def exercise() -> None:
        paths = await repo.markdown_paths()
        assert paths == ["notebook.md", "src/design.md"]

        page = await repo.get_page("notebook.md")
        updated = page.content + "\nSecond thought.\n"
        await repo.put_page("notebook.md", updated, "Notebook: continue Building Notebook", page.sha)
        assert (await repo.get_page("notebook.md")).content == updated

    asyncio.run(exercise())
    assert git(root, "log", "-1", "--format=%s").stdout.strip() == (
        "Notebook: continue Building Notebook"
    )
    assert git(root, "status", "--porcelain").stdout == ""


def test_local_repo_rejects_stale_page(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    repo = LocalRepo(root)

    async def exercise() -> None:
        page = await repo.get_page("notebook.md")
        (root / "notebook.md").write_text("# Changed elsewhere\n", encoding="utf-8")
        with pytest.raises(GitHubError, match="changed since it was opened"):
            await repo.put_page("notebook.md", "replacement", "Notebook: edit", page.sha)

    asyncio.run(exercise())


def test_local_repo_rejects_paths_outside_worktree(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    repo = LocalRepo(root)

    async def exercise() -> None:
        with pytest.raises(GitHubError, match="escapes the repository"):
            await repo.get_page("../outside.md")

    asyncio.run(exercise())
