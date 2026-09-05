# Notebook

Notebook is a notebook-first usability layer over an ordinary GitHub repository.

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

## First real self-host

Notebook can now be used from its own browser interface without an OpenAI API key or a GitHub token.

The local host uses the current Git worktree as the repository and launches `codex app-server` as the AI runtime. Codex reuses the user's existing ChatGPT authentication. The browser is therefore the working surface; the Codex CLI is infrastructure underneath it.

Notebook is a uv project. From a clone of this repository on the self-host branch:

```bash
# Requires uv and an already authenticated `codex` CLI.
git switch agent/issue-6-self-host-ui
uv sync
uv run uvicorn notebook_app.app:app --reload
```

`uv` creates and manages `.venv` automatically using the Python version pinned in `.python-version`. Development tools such as `pytest` and `ruff` live in the standard `dev` dependency group and are installed by the normal `uv sync`.

Open <http://127.0.0.1:8000>.

Notebook detects the current Git worktree automatically and opens `notebook.md` when it exists. No `.env` file is required. The status under the composer should say `Codex · ChatGPT`.

Typing into **Write or ask…** does something consequential: Notebook sends the page and project instructions to Codex, appends the human/AI exchange to that same ordinary Markdown page, and makes a Git commit on the current branch. The collapsed **Source** panel is a direct-edit escape hatch and also commits the selected page.

For this first self-host, Codex is deliberately read-only with respect to the worktree. Notebook itself owns the page commit. Repository-directed agent work such as implementing an issue remains a later layer and should return through auditable GitHub work rather than being hidden inside the page conversation.

Optional local overrides are documented in `.env.example`. A GitHub API repository backend and metered OpenAI API backend remain available as fallbacks, but neither is the normal local path.

## Development

Use uv for dependency and command execution:

```bash
uv sync
uv run ruff check .
uv run pytest -q
```

The committed `uv.lock` is the reproducible dependency source for local development and CI.

## One component, two hosts

The notebook browser is being kept host-neutral rather than building separate desktop and ChatGPT products.

### Local / desktop

The FastAPI shell serves the component and supplies two adapters:

- a local Git worktree for Markdown pages and commits;
- Codex app-server for subscription-backed AI turns.

This is the development and desktop path and is enough to let Notebook develop itself from `notebook.md`.

### ChatGPT-native

The same component detects the ChatGPT Apps bridge when `window.openai` is available. In that host it is designed to:

- use ChatGPT tool output as the page/browser data source;
- request ChatGPT-native fullscreen rather than browser fullscreen;
- send **Discuss this page** / composer text into the surrounding real ChatGPT conversation with `sendFollowUpMessage`;
- leave the normal ChatGPT composer and conversation as the conversational authority.

The component already contains this host adaptation. The MCP tool/resource wiring is intentionally deferred until it can be tested in a supported ChatGPT developer environment or through publication; it is not required for the local self-host.

## Skills-only plugin

The Notebook interaction model is also packaged as a skills-only plugin under `plugins/notebook/`. This was the first feasibility test: Codex successfully used it to open this repository as a conceptual notebook rather than foregrounding the source tree.

The local development marketplace is `.agents/plugins/marketplace.json`.

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

## Architecture gates

The current sequence is deliberately empirical:

1. **Skills-only behavior:** proven locally with Codex.
2. **Self-hosted notebook surface:** use the browser UI + local Git + Codex app-server to continue this project from `notebook.md`.
3. **ChatGPT-hosted component:** wire the same UI as an MCP Apps resource and test the surrounding real ChatGPT conversation when account/developer access permits.
4. **Repository machinery:** surface issues, PRs, Actions, artifacts, and agent execution underneath pages without turning Notebook into an IDE.
5. **Mobile:** publish the ChatGPT-native plugin once the hosted interaction is worth using.

The application should resist features that turn it into an IDE, a database-oriented workspace, or an agent-memory filesystem.
