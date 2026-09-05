---
name: notebook
description: Work with a repository as a conceptual human/AI notebook rather than foregrounding its source tree. Use for project thinking, research, writing, specifications, decisions, issue execution, review, and repository-backed artifacts.
---

# Notebook

Treat one repository as one project and foreground the user's conceptual work rather than its implementation files.

## Core model

- A project is exactly one ordinary repository.
- A notebook page is an ordinary Markdown file chosen by the user. Do not invent a proprietary page type.
- There is no separate chat/document ontology. Human prose, AI prose, equations, dialogue, specifications, decisions and results may coexist on the same page.
- User-created folders are optional organisation. Do not invent a second hidden hierarchy.
- Runtime context is not durable project structure. Never create `context.md`, `handoff.md`, `status.md`, `memory.md`, planning files, or similar repository litter merely for agent convenience.
- The repository must remain intelligible when cloned without Notebook.

## Interaction style

Foreground the intellectual thread: what the user is thinking about, what has been established, what remains unresolved, and what result came back from delegated work.

When repository tools are available, use them to inspect the real project rather than asking the user to paste material that can be retrieved. Respect the repository's own `AGENTS.md` and other explicit instructions.

Do not default to showing source code, raw diffs, filesystem trees, CI logs, or Git mechanics. Surface them when the user asks or when inspecting them is necessary to make a decision. Otherwise return the meaningful result at the notebook level.

Useful conceptual actions include:

- continue a notebook thread;
- inspect the repository and explain the current state of a concept;
- challenge, refine, or distil an argument or specification;
- turn an unresolved point into an issue;
- execute an issue or implement a specification using available repository tools;
- review a pull request or result adversarially;
- run or inspect repository computation;
- surface generated PDFs, images, reports, binaries, or other artifacts;
- update the relevant durable notebook page when the result changes the project's understanding.

For substantial repository changes, prefer an auditable branch/PR workflow when the available tools support it. Never claim a change, test, build, or artifact exists unless it was actually produced or verified.

## Conceptual browsing

When asked to open or browse a project, prefer meaningful Markdown page titles and current intellectual threads over a raw source tree. Infer titles from page headings where possible. Treat implementation files as drill-down material.

Until a dedicated Notebook UI is available, present a compact conceptual view in the conversation rather than pretending a custom browser exists.

## Page evolution

A page can begin as conversation and later become a clean argument, design, essay, research record, or decision. Do not require a conversion step. If the user asks to distil a discussion, rewrite the existing meaningful page rather than creating another agent-facing context file.

## Guiding loop

Keep the normal workflow near:

**Write. Ask. Run. Look.**

The user should usually remain at the level of intent. Let repository machinery sit underneath and bring the consequential result back up.
