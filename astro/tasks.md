# Astro Tasks

- Restore backend resource indexing for project `138`; `mainsequence project project_resource list 138 --path . --timeout 60` still returns `0` resources for commit `6884804062210fdcdcce3887ec2d43c43fddae13`.
- Replace or remove the stale `sample_app` dashboard job `348` once the Banxico dashboard path is fully healthy.
- Verify that dashboard job `421` and run `1322` reach a stable healthy state and expose the Banxico dashboard without tutorial artifacts.
- Review whether translation table `38` (`prices_translation_table_1d_tutorial_135`) should still exist; remove or isolate it if it is only legacy tutorial state.
- Investigate why `sync_project_after_commit(138)` still fails with `405 Method "POST" not allowed`.
- Investigate why `mainsequence project update-sdk --path .` reports success while `mainsequence project current --debug` still reports local version `3.11.1`.
- Reconcile formal project documentation into `astro/docs/` so the documentation layout matches `astro/instructions.md`.
