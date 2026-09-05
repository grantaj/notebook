from __future__ import annotations

import asyncio

from notebook_app.codex import CodexModel, _Turn


def test_codex_prompt_keeps_notebook_page_foreground() -> None:
    prompt = CodexModel._prompt(
        "grantaj/notebook",
        "notebook.md",
        "# Building Notebook\n",
        "What should we do next?",
        "Do not foreground source code.",
    )
    assert "foreground intellectual object" in prompt
    assert "Repository: grantaj/notebook" in prompt
    assert "Current page: notebook.md" in prompt
    assert "# Building Notebook" in prompt
    assert "What should we do next?" in prompt
    assert "Do not foreground source code." in prompt


def test_completed_turn_sets_done() -> None:
    turn = _Turn()
    CodexModel._complete_turn(turn, {"status": "completed"})
    assert turn.done.is_set()
    assert turn.error is None


def test_failed_turn_surfaces_error() -> None:
    turn = _Turn()
    CodexModel._complete_turn(
        turn,
        {"status": "failed", "error": {"message": "agent failed"}},
    )
    assert turn.done.is_set()
    assert turn.error == "agent failed"


def test_turn_event_is_asyncio_compatible() -> None:
    async def exercise() -> None:
        turn = _Turn()
        turn.done.set()
        await turn.done.wait()

    asyncio.run(exercise())
