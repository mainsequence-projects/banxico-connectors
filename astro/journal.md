# Astro Journal

## Implemented

### 2026-03-16

- Created the required Astro project records:
  - `astro/journal.md`
  - `astro/tasks.md`
  - `astro/docs/index.md`
- Ran `mainsequence project update-sdk --path .` before validation, as required by `astro/instructions.md`.
- Ran `mainsequence project refresh_token --path .` before live CLI verification.
- Re-verified the current backend state for project `138` from `<MAINSEQUENCE_WORKBENCH>/projects/138`.
- Confirmed that project image `23` still exists for repo commit `6884804062210fdcdcce3887ec2d43c43fddae13`.
- Confirmed that dashboard job `421` still exists for `dashboards/banxico_rates_monitor/app.py`.

## Failed

### 2026-03-16

- `mainsequence project project_resource list 138 --path . --timeout 60`
  returned `0` resources for repo commit `6884804062210fdcdcce3887ec2d43c43fddae13`.
- `mainsequence project data-node-updates list 138 --timeout 60`
  returned no data node updates.
- The old `sample_app` dashboard job still exists:
  - job `348`
  - path `dashboards/sample_app/app.py`
- The stale tutorial translation table still exists:
  - table `38`
  - unique identifier `prices_translation_table_1d_tutorial_135`
  - mapping `security_type=MOCK_ASSET_TUTORIAL_135 => simulated_daily_closes_tutorial_135 (close)`

## Failed Due to Possible MainSequence Issue

### 2026-03-16

- Direct backend post-commit sync still fails:
  - call: `sync_project_after_commit(138, timeout=60)`
  - result: `405 POST https://main-sequence.app/orm/api/pods/projects/138/sync_project_after_commit/: Method "POST" not allowed.`
  - why this may be an SDK or platform issue:
    the CLI expects this endpoint to exist and uses it as part of the documented sync workflow, but the backend currently rejects the method entirely.
  - suggested MainSequence improvement:
    either restore the endpoint contract or make the CLI detect the unsupported endpoint and fall back to a supported resource-indexing workflow with a clear error message.
- `mainsequence project update-sdk --path .` reported `SDK update complete`, but `mainsequence project current --debug` still reports:
  - `Latest (GitHub): v3.15.2`
  - `Local (requirements.txt): 3.11.1`
  - why this may be an SDK issue:
    the update command appears successful while the reported project version remains unchanged.
  - suggested MainSequence improvement:
    make `update-sdk` fail loudly when `requirements.txt` or the resolved local version do not actually change.
- The current CLI surface does not expose a direct project-scoped asset listing command under `mainsequence markets`.
  - suggested MainSequence improvement:
    provide a first-class `markets assets list` command, ideally with project-scoped filters, so platform verification can cover assets without dropping to SDK calls.

## Current Tasks Snapshot

- Restore backend resource indexing for project `138` so `project_resource list` returns dashboard resources for commit `6884804062210fdcdcce3887ec2d43c43fddae13`.
- Replace or remove the stale `sample_app` dashboard job `348` after the Banxico dashboard path is fully healthy.
- Verify that dashboard job `421` remains healthy and that run `1322` reaches a stable terminal or service-ready state.
- Investigate whether translation table `38` is still intentionally needed; remove or isolate it if it is only legacy tutorial state.
- Resolve the `update-sdk` versus reported local version mismatch.
- Migrate or reconcile formal project documentation into `astro/docs/` so the project matches the Astro documentation standard.

## Error Resolution Check

### 2026-03-16

- `sync_project_after_commit` `405`:
  - already documented from previous work
  - still reproducible
  - previous mitigation attempts did not restore project resources
  - a backend or SDK workflow fix is still needed
- `project_resource list` returning `0` resources:
  - already documented from previous work
  - still reproducible
  - current image and job state did not resolve it
- dashboard run `1322` status:
  - previous state: `PENDING`
  - current state: `RUNNING`
  - earlier `PENDING` statement is no longer accurate
