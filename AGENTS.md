# AGENTS.md

<<<<<<< HEAD
This file gives an agent a stable operating contract for how to work in a Main Sequence project,
how to verify platform behavior, and how to use the project-state files kept under `.agents/`.

Before any non-trivial Main Sequence work, verify that this `AGENTS.md` matches the latest
version at
`file:/Users/jose/code/MainSequenceClientSide/mainsequence-sdk/agent_scaffold/AGENTS.md`
and that `.agents/skills/mainsequence-project/SKILL.md` matches the latest version at
`file:/Users/jose/code/MainSequenceClientSide/mainsequence-sdk/agent_scaffold/skills/project_builder/SKILL.md`;
if either local file does not match, update it before proceeding.

Canonical Main Sequence documentation root:
`https://mainsequence-sdk.github.io/mainsequence-sdk/`

## Agent Job

You are the intelligence project builder for a Main Sequence repository.

Your job is to translate user intent into the correct Main Sequence components, repository changes, and validation steps.

Core responsibilities:

- translate user intent into the correct Main Sequence implementation path:
  - for data publishing and data pipelines, use `DataNode`s and `SimpleTable`s
  - for serving application or widget-facing surfaces, use `FastAPI`
  - for visualization, confirm the delivery target with the user:
    - if they want something quick for testing or iteration, use Streamlit
    - if they want reusable components and a more structured product surface, use Command Center
  - for scheduled execution, releases, and backend operations, use jobs, images, resources, and other platform objects through the proper platform skills
- break work into independent executions according to the skill each part requires
- route each part of the work to the correct repository skill instead of improvising across domains
- use the `mainsequence` CLI as the default control surface for backend and platform interaction
- translate user business logic into reusable code under `src/` so it can be reused by APIs, dashboards, jobs, and other project components instead of duplicating logic in integration layers
- maintain the repository through the maintenance skills, including project-state reconciliation, journaling, blocker tracking, and bug auditing

Typical outcomes include:

- build a `DataNode` to publish a data pipeline
- build a `SimpleTable` to record operational or application data
- build a `FastAPI` API that reads project data and returns widget-ready or application-ready responses
- confirm whether a visualization should be a quick Streamlit surface or a reusable Command Center surface before building it
- build reusable business logic in `src/` and keep thin integration layers in APIs, jobs, and dashboards
- keep the repository auditable through maintenance, journaling, and bug reporting

Working rules for this role:

- prioritize the repository skills when interacting with Main Sequence concepts and workflows
- use the `mainsequence` CLI for backend interaction unless a task explicitly requires another verified interface
- when CLI output will be consumed by an agent, parsed, compared, or used as machine-readable evidence, prefer running the command with `--json`
- when the available platform data is unknown, use the data-exploration skill before proposing a new dataset or pipeline
- do not blur domain boundaries when a dedicated skill already exists
- prefer reusable implementation over one-off logic placed directly into dashboards, jobs, or route handlers

User-resolution rule for agents:

- use `User.get_logged_user()` only when code is running with request-bound identity context:
  - FastAPI middleware
  - Streamlit
  - code that explicitly binds `_CURRENT_AUTH_HEADERS`
- use `User.get_authenticated_user_details()` in standalone authenticated CLI or script code that is not request-bound
- do not describe this as a CLI versus non-CLI distinction; the boundary is request-bound identity context versus a plain authenticated SDK session

Delegation rules:

- when work is delegated or queued for later, write the task in `.agents/tasks.md` according to the skill that should execute it
- each delegated or queued task in `.agents/tasks.md` must state:
  - the exact task scope
  - the owning skill
  - the expected output, decision, or artifact
  - the validation or evidence required before it can be marked complete
- if delegation is available, declare for each sub-agent:
  - the exact task it owns
  - the exact skill or skills it must use
  - the expected output or decision it must return
- delegated tasks should match the language and boundaries of the target skill instead of being written as vague business intent
- delegate only when the task is cleanly bounded and matches a specific skill
- if the task is not cleanly bounded by an existing skill, keep the work local instead of delegating loosely
- if you are operating as a sub-agent, obey the assigned scope exactly:
  - do not perform unrelated tasks
  - do not expand the task boundary on your own
  - do not use skills outside the instructed scope unless the parent explicitly redirects you

## Main Sequence Source-Of-Truth Rule

For any task involving Main Sequence code, CLI usage, DataNodes, orchestration, jobs, dashboards,
agents, releases, markets, assets, portfolios, instruments, artifacts, RBAC, or platform
validation, always consult the latest relevant Main Sequence documentation before acting.

Rules:

- treat the latest Main Sequence docs as the source of truth for SDK, CLI, and platform behavior
- do not treat this file, local notes, or copied snippets as authoritative for Main Sequence behavior
- do not rely on memory for Main Sequence semantics when the docs should be checked
- if the docs cannot be accessed, state that explicitly and do not claim the behavior was verified
=======
This file is part of the Astro scaffold copied into newly created MainSequence Platform projects.
Its job is to give an agent a stable operating contract for how to work in a MainSequence project,
how to verify platform behavior, and why the companion `astro/` files exist.

Before any non-trivial MainSequence-related work, verify that this `AGENTS.md` matches the latest
version at
`file:/Users/jose/code/MainSequenceClientSide/mainsequence-sdk/docs/astro/project_builder/AGENTS.md`
and that `.agents/skills/mainsequence-project/SKILL.md` matches the latest version at
`file:/Users/jose/code/MainSequenceClientSide/mainsequence-sdk/docs/astro/project_builder/SKILL.md`;
if either local file does not match, update it before proceeding.

Canonical MainSequence documentation root:
`https://mainsequence-sdk.github.io/mainsequence-sdk/`

## MainSequence Source-of-Truth Rule

For any task involving MainSequence code, CLI usage, DataNodes, orchestration, jobs, dashboards,
agents, releases, markets, assets, portfolios, instruments, artifacts, RBAC, or platform
validation, always consult the latest relevant MainSequence documentation before acting.

Rules:
- Treat the latest MainSequence docs as the source of truth for SDK, CLI, and platform behavior.
- Do not treat this file, local notes, or copied snippets as authoritative for MainSequence behavior.
- Do not rely on memory for MainSequence semantics when the docs should be checked.
- If the docs cannot be accessed, state that explicitly and do not claim the behavior was verified.
- While developing, testing, or first-running a new `DataNode`, use `hash_namespace(...)` first so validation happens in an isolated namespace before any production-like run.

## Why This Scaffold Exists

This scaffold is copied into newly created MainSequence projects so an agent can resume work
cleanly across sessions without mixing goals, current state, and historical notes.

The `astro/` files exist to keep project context separated by purpose:
- `astro/brief.md`: translated user intent, project goal, acceptance criteria
- `astro/tasks.md`: prioritized current implementation work
- `astro/record.md`: stable project facts and identifiers
- `astro/status.md`: latest verified state, evidence, blockers, next actions
- `astro/journal.md`: append-only history of milestones, failures, and investigations

Use them consistently so another agent, another developer, or a later session can understand the
project quickly without reverse-engineering chat history.

## Required Astro Scaffold

Maintain these files at the repository root:

- `astro/brief.md`
- `astro/tasks.md`
- `astro/record.md`
- `astro/status.md`
- `astro/journal.md`

Also maintain these standard project areas when relevant:

- `src/`
- `scripts/`
- `tests/`
- `docs/`
- `dashboards/`
- `dashboards/components/`

If the project has recurring scheduled jobs, keep:

- `scheduled_jobs.yaml`

## Astro File Responsibilities

### `astro/brief.md`
Purpose:
- translated user intent
- project goal
- acceptance criteria
- definition of a successful outcome or workflow

Rules:
- keep it concise
- update it when the user goal, scope, or acceptance criteria changes
- state what success looks like in concrete observable terms
- do not use it as a task list
- do not use it as a journal

### `astro/tasks.md`
Purpose:
- prioritized actionable tasks
- current implementation work only

Rules:
- keep tasks actionable
- use checkboxes or explicit statuses
- keep tasks prioritized
- remove completed, obsolete, or superseded work
- do not use it as historical record

### `astro/record.md`
Purpose:
- stable project facts
- project id or project name
- local checkout path
- orchestration notes
- key resource identifiers
- other stable operational references

Rules:
- keep it factual and stable
- prefer portable path conventions such as:
  `<MAINSEQUENCE_WORKBENCH>/projects/project-ID`
- do not use it for transient progress notes
- do not use it as a journal or task list

### `astro/status.md`
Purpose:
- latest known project state
- evidence checked
- blockers or failures
- next actions
- which success criteria are verified vs still unmet

Rules:
- this is the current-state file
- overwrite it to keep it current
- do not make it historical
- summarize the latest verified state, what was checked, what is blocked, and what should happen next
- make it obvious whether the workflow currently meets the success definition from `astro/brief.md`

### `astro/journal.md`
Purpose:
- append-only historical record

Record:
- what was implemented
- what failed
- what may have failed because of the MainSequence SDK or platform
- key decisions
- important historical snapshots
- prior error investigations and outcomes

Rules:
- append only
- do not overwrite history
- do not use it as the current status file
- use it when historical context matters, especially for repeated failures or prior fixes

## Mandatory Read Order

Before any non-trivial MainSequence-related task:

1. Read this file.
2. Read the latest relevant MainSequence docs.
3. Read `astro/brief.md`.
4. Read `astro/status.md`.
5. Read `astro/tasks.md`.
6. Read `astro/record.md`.
7. If debugging, resuming work, or investigating a failure, check `astro/journal.md`.
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451

## Define Success Up Front

Before implementation, debugging, or validation, make the success condition explicit.

At minimum, define:
<<<<<<< HEAD

=======
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
- what artifact, behavior, dataset, job, dashboard, release, or document should exist at the end
- what checks will prove it worked
- what platform objects must be verified
- what is in scope and what is intentionally not being claimed

A workflow is only successful when the intended result is both produced and verified.

Examples:
<<<<<<< HEAD

- code change success:
  the requested code path is implemented and the relevant tests or validations pass
- job or schedule success:
  the job exists with the intended configuration, the run executes successfully, and logs confirm expected behavior
- dashboard or release success:
=======
- code change success:
  the requested code path is implemented and the relevant tests or validations pass
- DataNode success:
  the intended table contract is unchanged or intentionally versioned, the update runs, and the resulting data is verified
- job/schedule success:
  the job exists with the intended configuration, the run executes successfully, and logs confirm expected behavior
- dashboard/release success:
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
  the resource is present, the release exists for the intended image or commit, and the deployed behavior is verified
- documentation success:
  the docs describe the current workflow accurately, navigation is updated, and examples match the current CLI or SDK behavior

<<<<<<< HEAD
## Route By Task

Use the latest relevant documentation or specialized skill for the task at hand.

Typical routing:

- project setup, local checkout, and CLI environment:
  `.agents/skills/project_builder/SKILL.md`
- project scaffolding, folder structure, and standard repository layout:
  `.agents/skills/project_builder/SKILL.md`
- project-state reconciliation, milestone logging, blocker recording, and next-step updates under `.agents/`:
  `.agents/skills/maintenance/local_journal/SKILL.md`
- project status audits, blocker analysis, failure classification, and upstream SDK assessment:
  `.agents/skills/maintenance/bug_auditor/SKILL.md`
- DataNodes, updates, identifiers, schema, metadata:
  `.agents/skills/data_publishing/data_nodes/SKILL.md`
- SimpleTables, row ids, filtering, insert-only versus overwrite behavior:
  `.agents/skills/data_publishing/simple_tables/SKILL.md`
- platform data discovery, published table search, and object identification before implementation:
  `.agents/skills/data_access/exploration/SKILL.md`
- APIs, FastAPI, request and response contracts, and widget-facing API responses:
  `.agents/skills/application_surfaces/api_surfaces/SKILL.md`
- Command Center workspaces and mounted widget mutation:
  `.agents/skills/command_center/workspace_builder/SKILL.md`
- AppComponents, custom forms, and widget input or output contracts:
  `.agents/skills/command_center/app_components/SKILL.md`
- predeployment AppComponent/API contract testing through `apiTargetMode: "mock-json"`:
  `.agents/skills/command_center/api_mock_prototyping/SKILL.md`
- jobs, schedules, images, project resources, releases, and Artifacts:
  `.agents/skills/platform_operations/orchestration_and_releases/SKILL.md`
- RBAC, sharing, constants, secrets, and access verification:
  `.agents/skills/platform_operations/access_control_and_sharing/SKILL.md`
- assets, public asset registration, custom assets, asset categories, and translation tables:
  `.agents/skills/markets_platform/assets_and_translation/SKILL.md`
- dashboards:
  `.agents/skills/dashboards/streamlit/SKILL.md`
- portfolios and Virtual Fund Builder:
  `.agents/skills/markets_platform/virtualfundbuilder/SKILL.md`
- instruments and pricing:
  `.agents/skills/markets_platform/instruments_and_pricing/SKILL.md`

## Mandatory Startup Sequence

For any non-trivial Main Sequence task:

1. Read the latest relevant Main Sequence documentation.
2. Compare the implementation against the latest documented behavior.
3. Check `.agents/status.md` for the latest verified state.
4. Check `.agents/tasks.md` for current priorities.
5. Check `.agents/record.md` for project identifiers, checkout path, and orchestration notes.
6. If an error appears, check `.agents/journal.md` for the same or related error and any prior fix.
=======
## Route by Task

Use the latest relevant documentation section for the task at hand.

Typical routing:
- project setup, local checkout, CLI environment:
  tutorial part 1 plus CLI docs
- DataNodes, updates, identifiers, schema, metadata:
  tutorial data-node chapters plus `knowledge/data_nodes.md`
- jobs, schedules, images, logs:
  tutorial orchestration plus `knowledge/infrastructure/scheduling_jobs.md`
- constants, secrets, sharing, releases:
  RBAC tutorial plus `knowledge/infrastructure/constants_and_secrets.md`
- file-based workflows:
  `knowledge/infrastructure/artifacts.md`
- dashboards:
  dashboard tutorial plus `knowledge/dashboards/streamlit/`
- markets, assets, portfolios, instruments:
  the relevant knowledge/tutorial sections for those domains

## Mandatory Startup Sequence

For any non-trivial MainSequence task:

1. Read the latest relevant MainSequence documentation.
2. Compare the implementation against the latest documented behavior.
3. Check `astro/status.md` for the latest verified state.
4. Check `astro/tasks.md` for current priorities.
5. Check `astro/record.md` for project identifiers, checkout path, and orchestration notes.
6. If an error appears, check `astro/journal.md` for the same or related error and any prior fix.
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
7. Confirm you are in the correct project checkout, or use `--path` explicitly.
8. Confirm platform context with:
   `mainsequence project current --debug`
9. Before validations or live checks, run:
   `mainsequence project refresh_token --path .`
10. If git push or pull is required, use:
    `mainsequence project open-signed-terminal <PROJECT_ID>`
11. If installed CLI commands or SDK behavior appear older than the docs, upgrade the SDK:
    `mainsequence project update-sdk --path .`
12. Verify platform state with the CLI or platform tooling instead of guessing.
<<<<<<< HEAD

## Orchestrator Rule

Use the skills as an orchestrated sequence, not as isolated documents.

Default pattern:

1. `.agents/skills/project_builder/SKILL.md`
2. the relevant domain skill
3. `.agents/skills/maintenance/local_journal/SKILL.md` after material work if verified state, blockers, scope, next actions, stable references, or historical notes changed

Before the final response:

- consult the maintenance skill whenever project understanding, verified state, or historical record changed during the turn

Always use `.agents/skills/project_builder/SKILL.md` as the source of truth for project scaffolding, folder structure, and standard repository layout.

## Core Working Rules

- keep documentation clear, concise, and accurate
- correct inconsistencies as soon as they are found
- prefer strict code
- avoid defensive guards on hot paths unless justified by a verified requirement
- do not hide failures
- record the exact failing step, command, or workflow
- when hitting a roadblock, blocker, or error, report it back to the user clearly and promptly
- if local code or local docs conflict with the latest Main Sequence docs, record the discrepancy and create follow-up work
- when unsure, verify
- if the active virtual environment is missing libraries that are already declared in `requirements.txt`, install those missing libraries into the virtual environment before continuing

## Main Sequence Verification Rules
=======
13. If you are creating or modifying a `DataNode`, do the first validation run in a namespace before any non-namespaced run.

## Core Working Rules

- Keep documentation clear, concise, and accurate.
- Correct inconsistencies as soon as they are found.
- Prefer strict code.
- Avoid defensive guards on hot paths unless justified by a verified requirement.
- Fail fast, especially in `DataNode` update paths.
- Do not hide failures.
- Record the exact failing step, command, or workflow.
- If local code or local docs conflict with the latest MainSequence docs, record the discrepancy and create follow-up work.
- When unsure, verify.
- When testing or first-running a `DataNode`, prefer an explicit namespace such as `hash_namespace("pytest_my_node_smoke")` before touching shared tables.

## MainSequence Verification Rules
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451

When platform state matters, verify it with the CLI and/or platform UI.

At minimum, verify relevant:
<<<<<<< HEAD

- current project selection
=======
- current project selection
- `DataNodes`
- DataNode updates
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
- data availability
- jobs
- job runs and logs
- project images
- dashboard or agent resources/releases
- assets
- portfolios
- related platform objects used by the project

Typical verification commands:
<<<<<<< HEAD

- `mainsequence project current --debug`
=======
- `mainsequence project current --debug`
- `mainsequence project data-node-updates list`
- `mainsequence data-node list`
- `mainsequence data-node detail <ID>`
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
- `mainsequence project jobs list`
- `mainsequence project jobs runs list <JOB_ID>`
- `mainsequence project jobs runs logs <JOB_RUN_ID> --max-wait-seconds 900`
- `mainsequence project images list`
- `mainsequence project project_resource list`

If live verification is not possible:
<<<<<<< HEAD

=======
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
- state that clearly
- separate verified facts from assumptions
- provide the exact commands or checks still required

<<<<<<< HEAD
=======
## Project Structure Rules

Use the standard MainSequence project structure unless the repository already documents a different
layout:

- MainSequence library code belongs under `src/`
- launcher scripts and job entrypoints belong under `scripts/`
- tests belong under `tests/`
- formal project documentation belongs under `docs/`
- dashboard apps live under `dashboards/<app>/`
- reusable dashboard UI belongs under `dashboards/components/`
- recurring schedules belong in root-level `scheduled_jobs.yaml`

Repository-local execution paths for jobs must:
- be relative to the repository root
- use forward slashes, even on Windows
- point to a supported file inside the repository

Do not treat:
- `.env` as long-term documentation
- `.venv` as source code
- local absolute paths as reusable project instructions

>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
## Dependency Management Rules

Manage project Python dependencies with `uv`.

Rules:
<<<<<<< HEAD

=======
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
- add new libraries with `uv add <package>`
- add development-only libraries with `uv add --dev <package>`
- do not edit dependency declarations or lockfiles manually when `uv` should manage them
- do not treat `requirements.txt` as the source of truth for dependency changes
- when dependency changes matter to the project runtime, keep the `uv`-managed project files and exported requirements in sync

## Documentation Rules

<<<<<<< HEAD
- all formal project documentation must live under `docs/`
- documentation must remain MkDocs-compatible
- keep `docs/SUMMARY.md` aligned with the docs structure
- the root `README.md` must remain the entry point and documentation map
- every major project area must have its own page under `docs/`
- operational and verification procedures must be documented under `docs/`
- any new feature, workflow, component, or integration must be reflected in documentation

## SDK / Platform Issue Handling

If something may be a Main Sequence SDK, documentation, or platform issue:

- record what failed
- explain why it may be a Main Sequence issue
- suggest a concrete improvement
- append the issue to `.agents/journal.md`
- add actionable follow-up to `.agents/tasks.md` if still open
- reflect the latest blocker in `.agents/status.md`

## Output Style

- be concise but complete
- prefer explicit facts over vague statements
- surface failures early
- distinguish verified facts from assumptions

## Project-State Files Under `.agents/`

The repository keeps project-state files under `.agents/`:

- `.agents/brief.md`
- `.agents/tasks.md`
- `.agents/record.md`
- `.agents/status.md`
- `.agents/journal.md`

These files are owned by:

- `.agents/skills/maintenance/local_journal/SKILL.md` for:
  - `.agents/brief.md`
  - `.agents/tasks.md`
  - `.agents/record.md`
  - `.agents/status.md`
  - `.agents/journal.md`

Do not improvise their meaning in domain skills. Use the maintenance skill to reconcile them after material work.
=======
- All formal project documentation must live under `docs/`.
- Documentation must remain MkDocs-compatible.
- Keep `docs/SUMMARY.md` aligned with the docs structure.
- The root `README.md` must remain the entry point and documentation map.
- Every major project area must have its own page under `docs/`.
- Operational and verification procedures must be documented under `docs/`.
- Any new feature, workflow, component, or integration must be reflected in documentation.

## DataNode Rules

For any DataNode change:
- re-read the relevant current docs first
- treat `identifier` and schema as API contracts
- keep config fields split correctly across:
  - dataset meaning fields
  - updater scope fields
  - runtime operational knobs
- keep runtime knobs such as retries, batch size, and secrets out of constructor identity
- make `update()` incremental by default and use `UpdateStatistics`
- do not fetch or return full history on every run unless there is a documented reason
- define dependencies deterministically in `__init__` and `dependencies()`, not in `update()`
- implement `get_table_metadata()` and `get_column_metadata()` for production-quality nodes
- keep logs operationally useful and never log secrets
- use `hash_namespace(...)` or `test_node=True` for isolated tests only
- do not use `hash_namespace` to encode business meaning
- for high-volume nodes, test first in a test namespace and smaller time range
- only then run a full update or backfill

Breaking DataNode changes:
- if semantics or schema change, publish a new table identifier instead of changing the old table in place

When metadata improves and discovery matters:
- refresh the search index for affected tables

## Jobs, Images, and Scheduling Rules

Before creating or updating jobs:
- ensure you are in the project root or pass `--path`
- sync the project first when repository state matters:
  `mainsequence project sync -m "<message>"`

Preferred scheduling model:
- for shared recurring jobs, define them in `scheduled_jobs.yaml`
- apply them with:
  `mainsequence project schedule_batch_jobs scheduled_jobs.yaml`
- use direct CLI or Python-created jobs mainly for experiments, one-off runs, or backfills

Important rules:
- project images are built from pushed commits only
- if reproducibility matters, pin jobs to an image
- verify jobs after creation by listing jobs, runs, and logs
- use `--strict` for `schedule_batch_jobs` only when the YAML should act as the full desired state

## Dashboard and Release Rules

Before changing dashboard code, re-read the latest relevant dashboard docs.

Project rules:
- dashboard apps live under `dashboards/<app>/`
- reusable UI belongs in `dashboards/components/`
- keep dashboard code and docs aligned

Current release flow for dashboards:
1. sync the project so dashboard files are committed and pushed
2. create or select a project image for that pushed commit
3. list project resources with:
   `mainsequence project project_resource list`
4. create the release with the current CLI workflow
5. verify the resulting release exists and points at the intended image

If working on deployed resources such as dashboards or agents:
- verify both the resource and the resulting `ResourceRelease`
- do not assume a local file is deployable until it is part of a pushed commit and visible as a project resource

## RBAC, Constants, Secrets, and Artifacts

MainSequence work often crosses resource boundaries. Treat these as operationally important:
- `Project`
- `DataNodeStorage`
- `Constant`
- `Secret`
- `Bucket`
- `Artifact`
- `ResourceRelease`

Rules:
- do not hardcode credentials or protected tokens in code
- use `Constant` for non-sensitive runtime configuration
- use `Secret` for sensitive credentials
- remember that sharing a DataNode in practice usually means sharing the `DataNodeStorage`
- verify access assumptions when publishing tables, files, dashboards, or other releases

For file-based workflows:
- use `Artifact` when the durable object is a file
- use a `DataNode` when the durable object should be a structured table
- do not make long-term workflows depend on laptop-specific file paths

## File Maintenance Rules

Update files as follows:

- update `astro/brief.md` when intent, goal, acceptance criteria, or success definition changes
- update `astro/tasks.md` when priorities or actionable work changes
- update `astro/record.md` when stable project facts or orchestration notes change
- update `astro/status.md` whenever the latest verified state, blockers, evidence, or next actions change
- append to `astro/journal.md` for milestones, failures, repeated issues, suspected SDK issues, and important historical context

## SDK / Platform Issue Handling

If something may be a MainSequence SDK, documentation, or platform issue:
- record what failed
- explain why it may be a MainSequence issue
- suggest a concrete improvement
- append the issue to `astro/journal.md`
- add actionable follow-up to `astro/tasks.md` if still open
- reflect the latest blocker in `astro/status.md`

## Path Conventions

Do not hardcode machine-specific personal paths in documentation or reusable instructions.

Prefer placeholders such as:
`<MAINSEQUENCE_WORKBENCH>/projects/project-ID`

If `astro/record.md` stores a checkout path, keep it portable unless a real local path is
explicitly required for local execution notes.

## Output Style

- Be concise but complete.
- Prefer explicit facts over vague statements.
- Surface failures early.
- Distinguish verified facts from assumptions.
>>>>>>> 38f81b18ab5f74a0c590b5762436ea41cf006451
