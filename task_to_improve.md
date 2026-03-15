# Task To Improve

Most of the original repository/documentation issues have already been
implemented. The remaining items are operational follow-ups rather than missing
repo structure.

## Remaining Improvements

## 1. Align backend deployment state with the repository

The codebase now contains:

- the Banxico source node
- the fixing and curve ETL flow
- `scheduled_jobs.yaml`
- the multipage dashboard
- updated documentation

What is still missing is the live backend state for project `138`.

The last CLI verification showed:

- no project images
- no project resources for the current remote head
- no DataNode updates

Remaining action:

```bash
mainsequence project sync -m "Sync Banxico connector updates" --path .
mainsequence project schedule_batch_jobs scheduled_jobs.yaml 138 --path .
mainsequence project jobs list 138 --timeout 60
mainsequence project data-node-updates list 138 --timeout 60
mainsequence project project_resource list 138 --path . --timeout 60
```

## 2. Submit the scheduled batch with a real project image

`scheduled_jobs.yaml` is present, but the checked-in `related_image_id` should
be treated as a placeholder/default.

Remaining action:

- build or select a valid project image
- submit the batch with `mainsequence project schedule_batch_jobs ...`
- verify the CLI applies the intended image to the job

## 3. Run the ETL once remotely and verify resulting tables

The repository now documents the expected healthy state, but it still needs one
successful remote job cycle to confirm:

- `banxico_1d_otr_mxn` has recent data
- `fixing_rates_1d` has TIIE/CETE fixings
- `discount_curves` has Banxico zero curves

Remaining action:

- run the scheduled or manual job remotely
- check job runs and logs
- confirm `data-node-updates` is no longer empty

## 4. Validate the dashboard in a real Streamlit session

The dashboard code imports successfully with backend-enabled imports and passed
syntax checks, but it has not yet been visually validated through a full
`streamlit run` or deployed dashboard session.

Remaining action:

- open the dashboard through Streamlit or the platform
- verify the landing page and all three pages render correctly
- confirm the empty-state behavior is acceptable when backend tables are still
  missing

## 5. Optional future cleanup

These are optional and not blockers:

- introduce a Pydantic config model for the source DataNode if the connector
  grows into multiple node variants
- replace the remaining monitoring-only dashboard with richer Banxico analytics
  if portfolio or pricing use cases are added later

## Conclusion

There are still things to improve, so this file should not be emptied yet.
However, the remaining work is now mostly:

- deployment
- image selection
- remote ETL execution
- and end-to-end dashboard validation
