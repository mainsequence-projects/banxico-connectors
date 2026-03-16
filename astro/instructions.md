# General Instructions for Extensions, Documentation, Development, and Maintenance of the Project

You are working on this project and must always follow these instructions as persistent context.

## General Rules

- Keep all documentation clear, concise, and accurate.
- Correct inconsistencies as soon as you find them.
- Use strict code. Avoid defensive guards on the hot path. Fail fast, especially when updating `DataNodes`.
- Do not hide failures. Record them clearly and explain the cause.
- If a failure may be caused by the MainSequence library or SDK, state that explicitly and suggest how the SDK could be improved to prevent the issue.
- Before starting any work, upgrade to the latest MainSequence SDK version using the CLI.
- Before running validations, run `mainsequence project refresh_token`.
- Verify all relevant resources using the CLI: `DataNodes`, updates, stored data, jobs, dashboards, assets, portfolios, and related platform objects.
- For `DataNodes` that may contain a large amount of data, always test first in a test namespace and with a smaller time range before running a full update or backfill.
- Any new implementation must be compared against the documentation and verified to ensure nothing breaks.
- When an error appears, first check the journal to see whether the same issue already happened and whether a solution was already documented.

## Required Project Structure

Use a project root called:

`astro/`

These files must exist inside that root:

- `astro/journal.md`
- `astro/tasks.md`

Documentation must follow `MkDocs` and must live inside:

- `astro/docs/`

Be strict about creating these files and folders and about why they exist.

### `astro/journal.md`
Create this file as the historical record of the project.

Its purpose is to preserve:

- what was implemented
- what failed
- what may have failed because of the MainSequence SDK or library
- what improvements should be suggested to MainSequence
- what tasks existed at a given moment
- whether a known error had already been solved before

This file is historical. Do not overwrite history. Append and organize it clearly.

### `astro/tasks.md`
Create this file as the active task list for the current implementation state.

Its purpose is to contain only:

- tasks that still need to be performed
- open documentation fixes
- open validation work
- open SDK-related follow-ups
- open implementation tasks discovered during review

This file is not historical. Remove completed, obsolete, or superseded tasks.

Do not use `tasks.md` as a journal.

### `astro/docs/`
Create this folder as the documentation root for the project.

Its purpose is to contain the project documentation in a structure compatible with `MkDocs`.

Rules:

- All project documentation pages must be inside `astro/docs/`.
- The documentation structure must follow `MkDocs` conventions.
- The documentation navigation must be consistent with the actual file structure.
- The main project README must explain how the documentation is organized.
- Any new documented feature, workflow, or component must be added to the `MkDocs` documentation structure.

## Journal Requirements

Keep an ongoing journal in:

`astro/journal.md`

Organize it with these sections:

### Implemented
Record what was successfully implemented.

### Failed
Record what failed, including the exact step, command, or workflow.

### Failed Due to Possible MainSequence Issue
Record failures that may be caused by the MainSequence library or SDK.

For each such issue, include:

- what failed
- why it may be an SDK or library issue
- what should be improved in the MainSequence SDK to avoid this error in the future

### Current Tasks Snapshot
Record the current task list in the journal for historical tracking.

### Error Resolution Check
When a new error appears, record whether:

- the same error was already documented
- a solution was already present in the journal
- the previous solution worked
- a new solution or SDK improvement is needed

## Tasks File Requirements

Keep the active task list in:

`astro/tasks.md`

Rules for `tasks.md`:

- It must contain only the current tasks to perform.
- It must not be historical.
- Remove completed or obsolete tasks.
- Keep it synchronized with the current implementation state.
- The same tasks should also be recorded in the journal as a historical snapshot.
- Any inconsistencies, missing documentation, SDK usability issues, or project improvements discovered during review must be converted into actionable tasks in `astro/tasks.md`.

## Project Path Conventions

Do not hardcode machine-specific local paths such as:

`/Users/jose/mainsequence/main-sequence-workbench/projects/banxico-connectors-138`

Use a standard placeholder path instead, for example:

`<MAINSEQUENCE_WORKBENCH>/projects/banxico-connectors`

If this library depends on another local project, document that dependency using the same standard path convention and follow that project as a reference standard where relevant.

## Documentation Structure

All documentation must be written under `astro/docs/` and organized for `MkDocs`.

### 1. Introduction
Explain what the library does. This section should closely follow the main project README and summarize the purpose of the library clearly.

### 2. DataNodes
Explain:

- which `DataNodes` are created
- what each `DataNode` stores
- the type of data each one contains
- how updates are performed
- any important constraints, namespaces, or validation rules

Also include operational guidance for high-volume nodes:

- test first in a test namespace
- use a smaller time range before running a full update

### 3. Markets
Explain how the project interacts with the MainSequence platform, including:

- which assets are created
- which portfolios are created or used
- which market objects are registered or updated
- how those objects relate to the project workflow

### 4. Instruments
Explain how `mainsequence.instruments` is used, including:

- which instrument types are mapped
- how the mapping logic works
- how identifiers are resolved
- any transformation or normalization rules
- any assumptions or limitations in the mapping

### 5. Dashboards
Explain which dashboards are created, what they show, and how they relate to the underlying data and workflows.

### 6. Documentation Map
The main project README must explain how the documentation is organized.

The `MkDocs` structure must remain aligned with the actual documentation layout inside `astro/docs/`.

## Review of MainSequence Documentation

Review the MainSequence SDK documentation here:

`https://github.com/mainsequence-sdk/mainsequence-sdk/tree/main/docs`

Then identify any inconsistencies, missing explanations, unclear behavior, or possible improvements relevant to this project.

Do not create a separate improvement file. Instead:

- convert findings into actionable open tasks in `astro/tasks.md`
- record the review results and historical context in `astro/journal.md`

This review should include:

- inconsistencies between this project and MainSequence docs
- missing documentation in this project
- missing or unclear documentation in MainSequence
- SDK usability issues discovered while working on this project
- concrete suggestions to improve the MainSequence SDK or docs

## CLI Verification Requirements

Use the CLI to verify the actual state of the project, including at minimum:

- `DataNodes`
- `DataNode` updates
- data availability
- jobs
- dashboards
- assets
- portfolios
- related platform resources used by the project

Before verification:

1. Upgrade to the latest MainSequence SDK with the CLI.
2. Run `mainsequence project refresh_token`.

If live verification is not possible, state that clearly and provide the exact CLI commands that must be run.

## Expected Output Style

- Be concise but complete.
- Prefer explicit facts over vague statements.
- Do not use machine-specific assumptions.
- Surface failures early.
- When unsure, verify with the CLI.
- When something looks like an SDK problem, document it and propose a concrete improvement.