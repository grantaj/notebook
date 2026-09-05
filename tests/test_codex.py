from __future__ import annotations

from notebook_app.codex import CodexModel


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


def test_codex_exec_is_ephemeral_read_only_and_uses_stdin() -> None:
    assert CodexModel._command() == (
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "-",
    )
