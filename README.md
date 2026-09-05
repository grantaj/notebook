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

## Two surfaces, one product

Notebook is being developed as two thin interaction surfaces over the same repository model.

### ChatGPT-native

The preferred mobile surface is a ChatGPT plugin. A normal ChatGPT conversation remains the conversation; Notebook contributes the project-oriented workflow and, later, an interactive conceptual notebook browser inside ChatGPT. This preserves ChatGPT history and subscription-backed ChatGPT usage instead of moving the user's work into another chat silo.

The first plugin is intentionally skills-only and lives under `plugins/notebook/`. It exists to test the central proposition before adding custom infrastructure: can the Notebook interaction model combine naturally with repository capabilities already available to ChatGPT?

A local marketplace entry under `.agents/plugins/marketplace.json` makes that plugin installable for development in supported desktop surfaces.

### Desktop

The existing standalone bootstrap remains available while the desktop architecture is proven. Its intended long-term model backend is Codex app-server rather than direct metered OpenAI API calls. Codex app-server is designed for custom clients and provides authentication, conversation history, approvals, and streamed agent events while allowing ChatGPT sign-in for subscription-backed Codex access.

Both surfaces must preserve the same invariant: **GitHub is canonical; Notebook is presentation and interaction.**

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

## Current feasibility sequence

1. Install the skills-only Notebook plugin in a supported desktop ChatGPT/Codex surface.
2. Use it on `grantaj/notebook`, `grantaj/entropy`, and `grantaj/nanoc` and verify that conceptual project interaction feels natural.
3. Verify that the skill can compose with available repository capabilities rather than requiring a duplicate GitHub backend.
4. Add a minimal MCP Apps UI for a conceptual page browser and test it in ChatGPT web/developer tooling where account support permits.
5. Only after that proof, pursue mobile publication of the interactive plugin.
6. Separately replace the standalone bootstrap's direct OpenAI model adapter with Codex app-server for the desktop path.

## Existing standalone bootstrap

The original proof-of-concept can:

- open one configured GitHub repository;
- discover ordinary Markdown pages without converting the repo;
- render Markdown with browser-side MathJax for LaTeX;
- edit a page directly;
- ask an AI on a page;
- append the human and AI contribution to that same ordinary Markdown file;
- commit the resulting page back through the GitHub Contents API.

It remains useful as disposable scaffolding while the ChatGPT-native and Codex-backed architectures are validated. Do not invest heavily in its direct OpenAI API path.

To run it today:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
set -a; source .env; set +a
uvicorn notebook_app.app:app --reload
```

The application should resist features that turn it into an IDE, a database-oriented workspace, or an agent-memory filesystem.
