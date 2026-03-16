# Astro Journal

## Implemented

### 2026-03-16

- Created the required Astro tracking files:
  - `astro/journal.md`
  - `astro/tasks.md`
  - `astro/docs/index.md`
- Updated the project SDK to the current MainSequence release and aligned the
  exported dependency file:
  - installed SDK: `3.15.4`
  - `requirements.txt`: `3.15.4`
  - `mainsequence project current --debug` now reports `Status: match`
- Identified the root cause of the forward-dated Banxico history:
  - Banxico returns dates as `DD/MM/YYYY`
  - the source transformation had been parsing them with generic
    `pd.to_datetime(...)`
  - example of the bad parse: `12/01/2026 -> 2026-12-01`
- Fixed the repository code so the issue cannot silently recur:
  - `banxico_connectors/utils.py` now parses Banxico dates with explicit
    `%d/%m/%Y`
  - `banxico_connectors/data_nodes/banxico_mx_otr.py` now raises if a source
    update produces future-dated rows beyond the allowed update window
  - the dashboard now separates future-dated rows from valid history and warns
    explicitly instead of plotting them as if they were current observations
- Cleaned the stale platform state that was known to be wrong:
  - deleted the old dashboard resource release `7`
  - deleted the Banxico source and downstream storages:
    - `discount_curves` storage `5660`
    - `fixing_rates_1d` storage `5662`
    - `banxico_1d_otr_mxn` storage `5664`
  - verified afterward that those three table identifiers no longer resolve
- Cleaned the dashboard job state for the active Banxico dashboard:
  - project image `24` exists for repo commit `c25a3aa`
  - dashboard job `426` exists for `dashboards/banxico_rates_monitor/app.py`
  - dashboard run `1327` succeeded
- Created a recurring ETL job directly through the current CLI as a fallback to
  the broken batch flow:
  - job `429`
  - name `Banxico Curves Refresh`
  - execution path `scripts/build_curves.py`
  - image `24`
  - cron `0 0 * * *`
- Ran the new ETL job once to validate the runtime:
  - run `1328`
  - status `FAILED`
- Identified a second repo-side ETL issue from the failed remote run:
  - `scripts/build_curves.py` was forcing `debug_mode=True`
  - the remote run entered local-mode behavior and failed during node startup
  - the repo has now been patched so the three node runs no longer force
    `debug_mode=True`
- Built follow-up images and revalidated the runtime in the platform:
  - image `25` for commit `dc47c4c`
  - image `26` for commit `4513d5c`
  - ETL job `431` now points at image `26`
  - ETL run `1332` reached `BanxicoMXNOTR.update()` and failed with an explicit
    runtime message:
    `BANXICO_TOKEN environment variable is required for Banxico SIE access.`
- Fixed the Streamlit `use_container_width` deprecation in the dashboard code:
  - replaced `use_container_width=True` with `width="stretch"` in the
    Banxico dashboard pages
  - built image `27` for commit `632ed4a`
  - recreated the dashboard job as job `432` on image `27`

## Failed

### 2026-03-16

- `mainsequence project project_resource list 138 --path . --timeout 60`
  still returns `0` resources for the current remote head.
- `mainsequence project schedule_batch_jobs scheduled_jobs.yaml 138 --path . --strict --timeout 60`
  failed with:
  - `400 POST https://main-sequence.app/orm/api/pods/job/sync_jobs/: {"project_id":["This field is required."]}`
  - this happened even though the CLI command was given project id `138`
- ETL run `1328` failed before any Banxico rebuild completed.
  - the visible log tail ends with:
    - `Could not retrieve pod project running in local mode`
    - `Main Sequence Running in local mode no pod attached`
    - `Creating configuration for BanxicoMXNOTR`
    - `Uncaught exception`
  - this is consistent with the old `debug_mode=True` runner behavior that has
    now been removed locally
- `mainsequence project data-node-updates list 138 --timeout 60`
  still does not show Banxico rebuild activity, which is expected because the
  Banxico tables were deleted and the ETL rebuild has not succeeded yet.
- Dashboard run `1333` for job `432` has been requested but is still `PENDING`,
  so the warning fix has been deployed but not yet observed through a fresh
  running dashboard session.

## Failed Due to Possible MainSequence Issue

### 2026-03-16

- Direct backend post-commit sync still fails:
  - call: `sync_project_after_commit(138, timeout=60)`
  - result:
    `405 POST https://main-sequence.app/orm/api/pods/projects/138/sync_project_after_commit/: Method "POST" not allowed.`
- Project resource indexing is still not updating for the current repo head:
  - symptom:
    `mainsequence project project_resource list 138 --path . --timeout 60`
    returns `0` resources even after image creation and a successful dashboard
    run
- Image deletion is still blocked by the backend:
  - `mainsequence project images delete 23 --yes --timeout 60`
    returned:
    `405 DELETE https://main-sequence.app/orm/api/pods/project-image/23/: Method "DELETE" not allowed.`
- The current batch scheduling endpoint appears broken for project job sync:
  - `mainsequence project schedule_batch_jobs ... --strict`
    returned:
    `400 .../sync_jobs/: {"project_id":["This field is required."]}`
  - the CLI did submit project id `138`, so either the CLI payload or the
    backend contract is not aligned

## Current Tasks Snapshot

- Push the `scripts/build_curves.py` runner fix, build a new project image, and
  move the ETL job to that image.
- Provide the Banxico runtime secret in the project job environment and rerun
  the ETL. The current blocker is now confirmed, not inferred:
  `BANXICO_TOKEN` is missing in the remote runtime.
- Rerun the Banxico ETL after the secret is available and verify the three
  deleted tables are recreated without future-dated history.
- Let dashboard job `432` leave the queue and verify one clean run on image
  `27` so the Streamlit warning fix is observed in live logs as well.
- Implement CLI support for setting up and controlling instrument
  configuration for the Banxico connector mappings and curve workflow.
- Restore backend resource indexing so project `138` exposes its current
  dashboard resources.
- Investigate the `schedule_batch_jobs` strict-sync failure.
- Investigate the `sync_project_after_commit` `405` failure.
- Remove stale image `23` once image deletion is supported again.

## Error Resolution Check

### 2026-03-16

- forward-dated Banxico source rows:
  - root cause found
  - repo fix implemented locally
  - live tables were deleted so the bad history is no longer active
  - rebuild still pending
- old dashboard tutorial state:
  - old dashboard release removed
  - old jobs `348` and `421` are no longer present in the current jobs list
- SDK version drift:
  - resolved
  - local project now matches latest SDK `3.15.4`
- `project_resource list` returning `0` resources:
  - still reproducible
- `schedule_batch_jobs --strict`:
  - still failing
- remote ETL execution:
  - first clean test run failed due to forced local debug mode
  - runner fix was deployed successfully
  - final validation now shows the remaining blocker is missing
    `BANXICO_TOKEN` in the remote runtime
- Streamlit `use_container_width` deprecation:
  - repo fix implemented
  - dashboard image `27` created
  - fresh dashboard job `432` created
  - live run verification is still pending because run `1333` remains queued
