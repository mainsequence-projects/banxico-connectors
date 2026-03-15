# Deployment And CLI

## Repository State Versus Platform State

This repository can be ahead of the current deployed MainSequence project state.
That is the first thing to verify before assuming that code, jobs, dashboards,
or DataNode updates are already active on the backend.

If the following commands return empty state, the repository and deployment are
not aligned yet:

```bash
mainsequence project current --debug
mainsequence project jobs list 138 --timeout 60
mainsequence project data-node-updates list 138 --timeout 60
mainsequence project project_resource list 138 --path . --timeout 60
mainsequence project images list 138 --timeout 60
```

## Current CLI Commands That Match The Installed SDK

These commands match the current SDK/CLI behavior:

```bash
mainsequence project current --debug
mainsequence project jobs list 138 --timeout 60
mainsequence project data-node-updates list 138 --timeout 60
mainsequence project project_resource list 138 --path . --timeout 60
mainsequence project images list 138 --timeout 60
mainsequence project schedule_batch_jobs scheduled_jobs.yaml 138 --path .
mainsequence project jobs runs list <JOB_ID> --timeout 60
mainsequence project jobs runs logs <JOB_RUN_ID> --max-wait-seconds 900
```

Notes:

- `mainsequence project current` does not take `--path`.
- The batch scheduling command is `schedule_batch_jobs` with a trailing `s`.
- The batch scheduler uses `scheduled_jobs.yaml`, validates the `jobs` list, and
  prompts for the project image to apply to the submitted batch.

## Repository-Managed Job Scheduling

Recurring jobs for this repository live in `scheduled_jobs.yaml`.

Submit or refresh the batch with:

```bash
mainsequence project schedule_batch_jobs scheduled_jobs.yaml 138 --path .
```

This is the preferred workflow for this project because:

- the job definition stays reviewable in git,
- the CLI validates the same job fields used by direct job creation,
- and the chosen project image is applied consistently at submission time.

The checked-in `related_image_id` in `scheduled_jobs.yaml` is therefore treated
as a placeholder/default. The CLI can override it when you submit the batch.

## Expected Healthy State After Build And Submission

After the repository is synced, the batch job is submitted, and the scheduled
or manual run succeeds, the expected state is:

- `mainsequence project jobs list 138 --timeout 60` shows `Banxico Curves Refresh`
- `mainsequence project images list 138 --timeout 60` shows at least one
  project image
- `mainsequence project project_resource list 138 --path . --timeout 60`
  returns resources for the current remote head, including the Banxico rates
  monitor dashboard
- `mainsequence project data-node-updates list 138 --timeout 60` shows update
  history for:
  - the Banxico source node
  - the fixing pipeline
  - the discount-curve pipeline
- `mainsequence project jobs runs list <JOB_ID> --timeout 60` shows successful
  recent runs for the batch-managed ETL job

## Recovery Flow When State Is Missing

If the state above is missing, use this order:

1. Confirm project detection:

```bash
mainsequence project current --debug
```

2. Sync the repository state:

```bash
mainsequence project sync -m "Sync Banxico connector updates" --path .
```

3. Submit the repository-managed jobs batch:

```bash
mainsequence project schedule_batch_jobs scheduled_jobs.yaml 138 --path .
```

4. Verify the job exists and get its id:

```bash
mainsequence project jobs list 138 --timeout 60
```

5. After the job runs, inspect the resulting update history:

```bash
mainsequence project data-node-updates list 138 --timeout 60
```

6. Confirm the current remote head now has resources:

```bash
mainsequence project project_resource list 138 --path . --timeout 60
```
