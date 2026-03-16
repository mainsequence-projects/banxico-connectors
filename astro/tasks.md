# Astro Tasks

- Provide `BANXICO_TOKEN` to the remote project job environment, then rerun
  ETL job `431`.
- Verify after the next successful ETL run that:
  - `banxico_1d_otr_mxn` is recreated
  - `fixing_rates_1d` is recreated
  - `discount_curves` is recreated
  - no `time_index` values are greater than the current date
- Let dashboard job `432` complete on image `27` and verify that the old
  Streamlit `use_container_width` deprecation warning no longer appears in the
  run logs.
- Implement CLI support for setting up and controlling instrument
  configuration in this project, including the mapped MainSequence instrument
  definitions used by the Banxico curves workflow.
- Investigate why
  `mainsequence project schedule_batch_jobs scheduled_jobs.yaml 138 --path . --strict`
  fails with `{"project_id":["This field is required."]}`.
- Investigate why
  `mainsequence project project_resource list 138 --path . --timeout 60`
  still returns `0` resources for the current remote head.
- Investigate why `sync_project_after_commit(138)` still fails with
  `405 Method "POST" not allowed`.
- Remove stale image `23` once the backend supports project-image deletion for
  this project again.
