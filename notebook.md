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

The first feasibility test is deliberately skills-only: package the Notebook interaction model as a plugin skill and test whether ChatGPT can combine it with repository capabilities already available to the model. This proves the conceptual inversion before adding a custom UI or another GitHub integration.

If that succeeds, add an MCP Apps UI that presents the conceptual page browser in ChatGPT. The UI should remain subordinate to the normal conversation: the ChatGPT composer remains the place where the user asks, directs, and continues the thread.

### Desktop surface

The standalone client remains useful on desktop, but it should not pay for ordinary OpenAI API inference when the user's ChatGPT subscription already includes Codex usage. The intended backend is Codex app-server, which is designed for custom clients and supplies authentication, conversation history, approvals, and streamed agent events.

The desktop application therefore becomes another Notebook presentation over Codex plus the local/repository environment, not an independent AI platform.

### Shared invariant

Neither surface owns project state. GitHub remains canonical. A clone must still make sense. Notebook-specific code may provide presentation, workflow guidance, caches, and runtime context assembly, but it must not introduce a hidden project database or proprietary page format.

## Self-reference

This repository should become the first worked example. Notebook should ultimately be usable to develop Notebook through both surfaces:

- the ChatGPT plugin should let a normal ChatGPT conversation treat `grantaj/notebook` as a conceptual notebook;
- the desktop client should be able to direct Codex against this repository while foregrounding the same pages and concepts.

The first self-reference threshold is now conceptual rather than implementation-specific: use the Notebook plugin to continue this project from `notebook.md`, then add the rich UI once that interaction proves natural.

## Next architectural question

The skills-only plugin is now good enough to test the central inversion: a normal ChatGPT conversation can treat this repository as a conceptual notebook while repository capabilities remain underneath it. The next architectural question is therefore narrower than "build the Notebook UI":

> What is the smallest ChatGPT-native conceptual browser that makes repository-backed pages feel present without moving the conversation, project state, or GitHub workflow into a second product model?

The answer should be an MCP Apps browser whose first job is orientation, not authoring infrastructure. It should expose ordinary Markdown pages by meaningful title, open the current page, and support switching between fullscreen page browsing and the normal ChatGPT composer. It should not introduce a notebook database, a separate chat object, a custom page format, a duplicate GitHub connector, or a desktop-style source tree.

The experiment should be judged by whether the user can stay in the notebook loop:

**Write. Ask. Run. Look.**

If the browser makes it easier to choose the current page and inspect the thread while still using ChatGPT as the conversation surface, it validates the next layer. If it mainly recreates an IDE sidebar, a document manager, or another chat client, it is the wrong abstraction.
