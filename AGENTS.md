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

## Engineering rules

- Python 3.11+.
- Keep dependencies modest.
- Use `ruff` and `pytest` in CI.
- Keep GitHub and model-provider code behind small interfaces so they can be replaced.
- Never expose tokens or API keys to rendered pages or logs.
- Treat repository Markdown as untrusted for HTML rendering; raw HTML stays disabled.
- Prefer tests around pure transformations and API boundaries.

## Current milestone

Make the self-hosting notebook loop pleasant before broadening scope:

1. open an ordinary repo;
2. browse its Markdown pages;
3. render Markdown/LaTeX;
4. edit a page;
5. ask AI on that page;
6. commit the combined page back to GitHub;
7. point Notebook at its own repository and continue development from `notebook.md`.
