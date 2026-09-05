# Building Notebook

The starting observation was dissatisfaction with project work being split between a GitHub repository and chats imprisoned inside an AI client. In current agent-heavy software and research workflows, the chat window has become the primary place where the human actually works: ideas are developed, specifications emerge, arguments are tested, tasks are delegated, and results are reviewed. The source tree is increasingly something to inspect only when necessary.

Existing tools have the hierarchy backwards. An IDE foregrounds files and puts AI in a panel. Notebook should foreground the evolving human/AI intellectual thread and let files, issues, pull requests, Actions, and artifacts sit behind it.

## Product idea

A project is exactly one ordinary GitHub repository. The application is a magical notebook usability layer over that repository.

The main browser should be conceptual rather than a code-file browser. It should foreground pages such as:

- Parser architecture
- Tokenizer simplification
- Inclusion after containment
- Outer iteration
- Catalogue argument

A page is simply a Markdown file chosen and organised by the user. Folders remain ordinary repository folders. There are no separate note and chat objects. A page can contain human prose, AI prose, equations, images, handwritten material, dialogue, a distilled specification, implementation results, or all of them over time.

The system must not reward agents for generating a proliferation of context files. Runtime context is assembled from the current page, linked or selected pages, repository instructions, and relevant GitHub state. Durable pages exist because they are meaningful to the human, not because an agent needs a scratchpad.

## Interaction model

The basic page actions are deliberately close to:

**Write. Ask. Run. Look.**

Write directly in the notebook. Ask AI to think with or act on the project. Run repository computation through GitHub Actions. Look at the result: a page, PR summary, PDF, image, binary, report, test result, or code when desired.

The normal path should stay at the level of intent:

> Reconsider the parser architecture and implement the cleaner option.

or:

> Try as hard as possible to invalidate this theorem, then update our current understanding.

The AI can descend into the repository, modify code or LaTeX, invoke tests or builds, and return the meaningful result to the notebook.

## Two surfaces, one Notebook

The preferred architecture is now two thin clients over the same ordinary repository and the same Notebook interaction model.

### ChatGPT-native surface

On mobile, the ideal Notebook is a ChatGPT plugin rather than a replacement chat client. The normal ChatGPT conversation remains the place where the human and AI talk, so conversation history and subscription-backed ChatGPT usage stay in ChatGPT. Notebook supplies the project-oriented conceptual behaviour and, later, a fullscreen notebook browser inside ChatGPT.

The first feasibility test was deliberately skills-only. It succeeded: Codex loaded the Notebook skill and spontaneously presented this repository as a conceptual thread rather than a source tree. That is enough evidence to move on from prompt behaviour to the actual notebook surface.

The hosted component should remain subordinate to the normal conversation: ChatGPT supplies the model and chat history; Notebook supplies the conceptual browser and project affordances. Its composer can send a follow-up into the surrounding ChatGPT conversation rather than maintaining a second chat.

### Desktop surface

The standalone client should not pay for ordinary OpenAI API inference when the user's ChatGPT subscription already includes Codex usage. Its normal backend is therefore Codex app-server, which is designed for custom clients and supplies ChatGPT-backed authentication, conversation history, approvals, and streamed agent events.

The desktop application is another Notebook presentation over Codex plus the local repository environment, not an independent AI platform.

### Shared invariant

Neither surface owns project state. GitHub remains canonical. A clone must still make sense. Notebook-specific code may provide presentation, workflow guidance, caches, and runtime context assembly, but it must not introduce a hidden project database or proprietary page format.

## First real self-host

The first real self-host deliberately uses **one notebook component with two hosts**.

Locally, the browser opens the current Git worktree, treats `notebook.md` as the default page, and uses `codex app-server` underneath the **Write or ask…** composer. A turn is appended to the same Markdown page and committed by Notebook on the current branch. No OpenAI API key or GitHub token is required. Codex is infrastructure; the human works in Notebook.

Inside ChatGPT later, that same component switches host behavior: it consumes tool output supplied by ChatGPT, requests ChatGPT-native fullscreen, and sends composer text into the surrounding real ChatGPT conversation. The project model does not change when the host changes.

This is intentionally enough to continue developing Notebook from the Notebook interface before solving GitHub issues/PRs/Actions, agent execution, or mobile publication.

## Self-reference

This repository is the first worked example. The immediate test is no longer theoretical:

1. launch Notebook from this worktree;
2. open this page;
3. continue this thread through the Notebook composer;
4. confirm the exchange lands here as ordinary Markdown in an ordinary Git commit;
5. continue the next development decision from that interface.

If that feels natural, the application has crossed its first meaningful self-hosting threshold.

---

### You

is this thing on?

### AI

Yes.

This is landing in the Notebook flow: `notebook.md` is the foreground page, the repository is the backing project, and I’m treating your message as part of this conceptual thread rather than as a raw code task.

---

### You

That landed in the page, we have achieved self-host! My goal is to be able to build the rest of notebook inside notebook via this interface. The next thing we need is delegation into the repository. Design the smallest safe Run capability that lets me instruct the agent from this page to implement a change, run tests, and return the result here, keeping branches/commits/PRs issues etc auditable and avoiding hidden state.

### AI

## Smallest Safe Run

The smallest useful `Run` capability should be a **delegated repository turn** launched from a notebook page, with all durable state stored in ordinary Git/GitHub objects.

The user writes something like:

> Run: implement autosave debounce, update tests, and report back here.

Notebook turns that into one auditable work unit.

## Core Rule

A Run must never create hidden Notebook state.

Everything durable should be one of:

- the current Markdown page;
- a Git branch;
- commits;
- a GitHub issue, when useful;
- a pull request, when the change should be reviewed;
- GitHub Actions logs/artifacts;
- a final result appended back to the page.

Runtime logs, prompts, tool events, and temporary files can exist while the run is active, but they are not the project record.

## Minimal Workflow

1. **Start from the current page**

   The run receives:

   - repository instructions;
   - current page path, e.g. `notebook.md`;
   - selected page excerpt or whole page;
   - current branch and commit SHA;
   - the user’s instruction.

   The page is the specification unless the user links an issue or asks to create one.

2. **Create an auditable branch**

   Notebook creates a branch named from the page and request:

   ```text
   notebook/run-delegation-YYYYMMDD-HHMM
   ```

   The branch starts from the current checked-out commit. If the worktree is dirty, the Run should refuse or ask whether to commit/stash first. No silent mixing.

3. **Hand the task to Codex**

   Codex runs with a constrained instruction:

   ```text
   You are implementing a repository change requested from notebook.md.
   Preserve repository instructions.
   Make the smallest coherent change.
   Run relevant tests.
   Commit the result.
   Return a concise notebook-level report.
   ```

   The agent may inspect files, edit code, run tests, and commit. It should not update `notebook.md` directly unless the requested change is itself to the page.

4. **Commit every meaningful result**

   At minimum, the run should produce either:

   - one implementation commit;
   - one explicit no-op/report commit only if a durable investigation artifact is truly useful;
   - or no commit, with a clear failed/aborted result.

   Prefer commit messages like:

   ```text
   Implement Run delegation skeleton

   Requested-from: notebook.md
   Notebook-run: 2026-09-05T...
   ```

5. **Run tests through the normal repository path**

   Locally, for this repo, that means:

   ```text
   uv run ruff check
   uv run pytest
   ```

   Later, a Run can also trigger GitHub Actions, but the first version only needs local command execution plus captured summaries.

6. **Return the result to the page**

   Notebook appends a compact result block to the current page:

   ```markdown
   ### Run Result

   Request: implement autosave debounce, update tests, and report back here.

   Branch: `notebook/run-autosave-debounce-20260905-1430`
   Commit: `abc1234`
   Tests: `uv run ruff check` passed; `uv run pytest` passed

   Result:
   Implemented autosave debounce in the composer path and added regression coverage for rapid edits.

   Review:
   Open PR: <link>
   ```

   If it failed:

   ```markdown
   ### Run Result

   Request: ...

   Branch: `notebook/run-...`
   Status: failed before commit
   Tests: `uv run pytest` failed

   Result:
   The implementation reached X, but Y test failed because Z. No changes were committed.
   ```

## First-Version Product Shape

The UI only needs one new affordance:

```text
Write or ask...
[ Ask ] [ Run ]
```

`Ask` continues the page conversation.

`Run` means: “treat this message as delegated repository work.”

Before starting, show a small confirmation sheet:

```text
Run from notebook.md

Base: main @ abc1234
Branch: notebook/run-...
Mode: implement + test + report
PR: create draft PR when committed

[Start Run]
```

That is enough. Do not add dashboards, job databases, queues, or custom task objects yet.

## PR and Issue Policy

Use issues only when the user is defining durable work independent of the current run:

- “Turn this into an issue” creates an issue.
- “Run this” does not need an issue.
- “Implement issue #12” uses issue #12 as the spec.

Use PRs when there is a committed code change that should be reviewed. The first implementation can default to a draft PR after successful tests.

So the ordinary audit chain becomes:

```text
notebook.md request
  -> branch
  -> commits
  -> tests / Actions
  -> draft PR
  -> notebook.md result
```

## Safety Boundaries

The first safe Run should refuse or pause when:

- the worktree has uncommitted changes;
- the current branch is not pushable or has diverged;
- tests require missing secrets;
- the agent wants to modify files outside the repository;
- the requested task implies destructive Git operations;
- the task needs credentials not already available through approved tooling.

It should also enforce a simple invariant:

> A Run may modify repository files, but it may not silently modify the notebook page that launched it except to append the final result block.

## Smallest Implementation Target

Build this in three layers:

1. **Run envelope**

   A local object in memory only:

   ```text
   page_path
   user_instruction
   base_branch
   base_sha
   run_branch
   started_at
   ```

2. **Repository executor**

   Shells out to Git and Codex app-server, creates branch, runs the agent, runs tests, captures result.

3. **Notebook reporter**

   Appends the final Markdown result to the launching page and commits that page update separately, probably on the original branch after the PR exists.

The key design choice: the Run controller may have ephemeral process state, but the project history is just GitHub and Markdown. That keeps Notebook honest.

---

### You

we should not require the user to use a magic spell "run". I guess we have the usual IDE permission problem for working with agents. For now I think we should just do whatever the user asks, and if are unsure ask the user to clarify or approve. I think we keep the set of possible actions small and sage - code edits, github operations, running repo tests and code. How should we handle this safely?

### AI

## Safe Default: Intent First, Approval When Risk Changes

Yes: the user should not need a magic word like `Run`.

Notebook should treat every composer message as an intent, then choose the smallest safe action that satisfies it. The interface can still have modes internally, but the user-facing rule is simpler:

> Do what I appear to be asking. If the action has meaningful side effects, make the side effect visible before crossing the boundary.

## Practical Action Ladder

I would use a small graduated model:

| User intent | Default behavior |
|---|---|
| Think, explain, critique, summarize | Answer directly in the page thread |
| Inspect repository state | Read files, Git state, issues, PRs, logs as needed |
| Run read-only commands | Run tests, typechecks, builds, searches, previews |
| Edit code or pages | Make scoped edits when clearly requested |
| Commit / branch / PR / issue | Ask or infer only when the request clearly implies durable GitHub state |
| Destructive or ambiguous operations | Stop and ask |

So:

> “Why is the parser test failing?”

Can inspect files and run tests.

> “Fix the parser test failure.”

Can edit code and run tests.

> “Fix it and open a PR.”

Can branch, commit, push, and open a PR, subject to credentials and dirty-worktree checks.

> “Clean this up.”

Probably needs clarification unless context makes the target obvious.

## Permission Boundaries

The first version should have only a few side-effect classes:

1. **Read**
   - inspect files;
   - inspect Git state;
   - inspect issues/PRs;
   - read logs/artifacts.

2. **Run**
   - run repository-local commands;
   - run tests;
   - run formatters/linters;
   - run build commands.

3. **Edit**
   - modify ordinary repository files;
   - append or update the current notebook page when that is the requested foreground object.

4. **GitHub/Git**
   - create branch;
   - commit;
   - push;
   - create issue;
   - create PR;
   - comment on issue/PR.

That is enough for real work.

Avoid broader capabilities for now: arbitrary external integrations, background daemons, secret management, scheduled jobs, hidden queues, custom task databases.

## When To Ask

Notebook should ask before proceeding when any of these are true:

- the user’s intent is ambiguous;
- the worktree has uncommitted changes not caused by this turn;
- the agent would overwrite, delete, rename, or mass-format files;
- the agent needs network or credentials beyond the repo’s normal tooling;
- the change crosses from local edits into durable Git/GitHub state;
- tests fail and the next step is not obvious;
- the action would affect branches, releases, deployments, secrets, billing, or publication;
- the agent is about to modify the launching page in a way other than normal conversation/result appending.

## Better Than A Magic Spell

The composer can stay singular:

```text
Write or ask...
```

Then Notebook classifies intent behind the scenes:

- **Answer**: no side effects.
- **Inspect**: read-only repository work.
- **Work**: edits/runs/tests.
- **Publish**: branch/commit/PR/issue.

The UI can show a small pending-action chip when useful:

```text
Will edit code and run tests.
[Proceed] [Adjust]
```

But it should not force the user to learn command words.

## The Key Safety Rule

The core rule should be:

> The agent may act directly inside the repository when the user’s intent is clear, but every durable side effect must be ordinary, visible, and attributable.

That means no hidden Notebook task state. The audit trail is still:

```text
notebook page intent
-> repository reads / local commands
-> file edits
-> tests
-> branch / commit / PR when appropriate
-> result appended back to the page
```

This keeps the product natural: the user thinks in the notebook, the agent works in the repository, and the durable record remains Markdown plus Git/GitHub.
