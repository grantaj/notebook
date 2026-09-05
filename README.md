# Notebook

Notebook is a thin, notebook-first usability layer over an ordinary GitHub repository.

The repository remains the project. Markdown and LaTeX are ordinary files. Source code is ordinary source code. GitHub Issues, pull requests, Actions, artifacts, commits, branches, and permissions remain GitHub's. Notebook adds a conceptual foreground for the part of modern work that increasingly matters most: the evolving conversation between a human and an AI, the specifications and arguments that emerge from it, and the results brought back from repository work.

The governing inversion is simple:

> In an IDE, files are the work and chat assists the files. In Notebook, the human/AI notebook is the work and repository files are the machinery underneath it.

Notebook is not an IDE and not a Notion clone. It should remain useful for software, mathematical research, writing, and other repository-backed intellectual work without inventing a proprietary project model.

## Constitutional constraints

1. **A project is a repository.** There is no second canonical project database.
2. **A page is a Markdown file.** A page may be prose, equations, images, handwriting, conversation, specification, decision record, or any mixture of them.
3. **There is no chat/document distinction.** A page can begin conversationally and become polished without conversion to another object type.
4. **The repo must make sense when cloned.** Notebook may cache or index, but no durable meaning may depend on hidden application state.
5. **Context is runtime state, not repo litter.** Agents must not create `context.md`, `handoff.md`, `status.md`, or similar files merely for their own memory.
6. **Code is available but not foregrounded.** Agents may generate and edit code; humans can inspect it when useful, but the primary interface is the conceptual notebook.
7. **GitHub supplies the machinery.** Issues represent work, PRs represent proposed changes, Actions supply computation, and artifacts supply outputs.
8. **AI is a replaceable collaborator.** Notebook should not make one vendor's assistant the project owner.

## The basic loop

```text
think / write / ask
        |
        v
   notebook page
        |
        v
 direct repository work
        |
        +--> issues / PRs / code
        +--> GitHub Actions
        +--> generated artifacts
        |
        v
 result returns to page
        |
        v
     continue
```

A user should normally live at the top of this loop. Opening a source file, CI log, or diff is an escape hatch, not the default mode of work.

## Bootstrap milestone

The first version is deliberately primitive. It can:

- open one configured GitHub repository;
- discover ordinary Markdown pages without converting the repo;
- render Markdown with browser-side MathJax for LaTeX;
- edit a page directly;
- ask an AI on a page;
- append the human and AI contribution to that same ordinary Markdown file;
- commit the resulting page back through the GitHub Contents API.

This is enough for the first self-referential test: point Notebook at its own repository, open `notebook.md`, and continue designing Notebook from inside Notebook.

Authentication is intentionally deferred in the bootstrap. The server reads a GitHub token and model key from environment variables. OAuth, richer context selection, issues/PRs/Actions/artifacts, and agentic repository execution come after the self-hosting loop works.

## Run the bootstrap

Python 3.11+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
# edit .env, then:
set -a; source .env; set +a
uvicorn notebook_app.app:app --reload
```

Open <http://127.0.0.1:8000>.

For self-hosting, set:

```text
GITHUB_REPO=grantaj/notebook
GITHUB_BRANCH=main
```

and open `notebook.md` in the app.

## What comes next

The next tranche should preserve the same inversion rather than expand sideways:

- repository picker and GitHub OAuth;
- conceptual/recent page browser rather than a source-code tree;
- visible context selection;
- issues and PRs as related work beneath pages;
- GitHub Actions as runnable computation;
- artifact viewing, especially PDF/image/text outputs;
- an agent action path for instructions such as `execute #31`, with changes returning as summaries/results rather than forcing the user into code;
- installable/mobile PWA polish.

The application should resist features that turn it into an IDE, a database-oriented workspace, or an agent-memory filesystem.
