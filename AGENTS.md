# Agent instructions

Notebook is a notebook-first interface to an ordinary GitHub repository. Preserve that premise aggressively.

## Product rules

- The repository is canonical. Do not create a second project data model.
- Pages are ordinary Markdown files. Do not introduce a proprietary notebook file format.
- Do not create planning, context, handoff, scratch, memory, or status files merely for agent convenience.
- Create a new durable page only when it represents a meaningful human-facing subject.
- Do not introduce separate chat and document object types.
- Keep source code, Git operations, CI details, and implementation machinery available but secondary in the UX.
- Prefer GitHub's existing objects instead of reproducing them: issues for work, PRs for proposed changes, Actions for computation, artifacts for outputs.
- Any repository used through Notebook must remain intelligible and useful after cloning without Notebook.
- Avoid configuration unless a feature truly cannot be inferred from ordinary repository structure.
- The bootstrap should stay small. Do not solve hypothetical enterprise collaboration, databases, block editors, or IDE functionality.

## Architecture

Notebook is one product with two intended surfaces:

- **ChatGPT-native:** a plugin/skill first, then an MCP Apps conceptual browser when the interaction model is proven. The ordinary ChatGPT conversation remains the conversation.
- **Desktop:** a standalone notebook surface backed by Codex app-server rather than direct metered model API calls.

Do not duplicate project state between these surfaces. Both operate on the same ordinary repository and should share the same conceptual interaction rules.

For the ChatGPT plugin, prefer a skills-only proof before adding an MCP server. When repository tools are already available to the model, compose with them rather than building another GitHub connector merely for Notebook.

For the desktop client, do not deepen the current direct OpenAI API integration. Treat it as bootstrap scaffolding until Codex app-server replaces the model/runtime boundary.

## Engineering rules

- Python 3.11+ for the existing standalone bootstrap.
- Use `uv` for Python environment, dependency, lockfile, and command execution. Do not introduce `pip install`, hand-managed virtualenv setup, or a second dependency manifest into the normal workflow.
- Keep `uv.lock` committed and CI locked to it.
- Development dependencies belong in the standard `[dependency-groups].dev` group.
- Keep dependencies modest.
- Use `ruff` and `pytest` in CI via `uv run`.
- Keep GitHub and model/runtime code behind small interfaces so they can be replaced.
- Never expose tokens or API keys to rendered pages or logs.
- Treat repository Markdown as untrusted for HTML rendering; raw HTML stays disabled.
- Prefer tests around pure transformations and API boundaries.
- Plugin packaging must remain ordinary files in the repository; do not introduce generated agent-memory files.

## Current milestone

Prove the architecture before broadening features:

1. install and exercise the skills-only Notebook plugin on real repositories;
2. verify that ChatGPT can apply the Notebook workflow while using repository capabilities already available to it;
3. add the smallest possible conceptual browser UI and test fullscreen + normal ChatGPT composer interaction on web;
4. determine the viable path from development testing to mobile availability;
5. separately prove Codex app-server as the standalone desktop runtime using ChatGPT authentication;
6. only then expand issues/PRs/Actions/artifacts UX.

The self-referential test remains important: `grantaj/notebook` and `notebook.md` should be among the first real projects used through both surfaces.
