# Astro Tasks

- Build and register a new project image from the commit that removes
  `debug_mode=True` from `scripts/build_curves.py`.
- Repoint or recreate the Banxico ETL job so it uses the new image instead of
  image `24`.
- Rerun the Banxico ETL and verify that:
  - `banxico_1d_otr_mxn` is recreated
  - `fixing_rates_1d` is recreated
  - `discount_curves` is recreated
  - no `time_index` values are greater than the current date
- Verify whether the runtime has a valid Banxico secret after the runner fix is
  deployed. If not, document the missing secret explicitly as the next blocker.
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
