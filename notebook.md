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

## Self-reference

This repository should become the first worked example. The bootstrap application should be pointed at its own repository and this page should become the place where further design work continues.

If that feels natural, the abstraction is probably right.
