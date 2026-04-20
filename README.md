<p align="center">
<img src="https://main-sequence.app/static/media/logos/MS_logo_long_black.png" alt="Main Sequence Logo" width="500"/>
</p>

# banxico-connectors

`banxico-connectors` extends `mainsequence` with Banxico SIE market data for Mexican
rates. It stores on-the-run government-instrument quotes in a daily
MainSequence DataNode, publishes Banxico target-rate, TIIE, and CETE fixings,
and bootstraps an MXN zero curve that can be consumed by MainSequence pricing
models and dashboards.

## What The Project Does

- Pulls Banxico SIE series for CETES, M Bonos, UDIBONOS, Bondes D, Bondes F,
  Bondes G, and the Banxico target-rate fixing.
- Registers Banxico-specific market assets and MainSequence constants.
- Builds MainSequence fixing datasets for Banxico target-rate, TIIE, and CETE
  reference rates.
- Builds a MainSequence discount curve from Banxico on-the-run instruments.
- Includes a multipage Streamlit dashboard that monitors the source node,
  fixing rates, zero curves, and platform table health.

## Quickstart

### Requirements

- Python 3.11 or newer
- A valid `BANXICO_TOKEN`
- A working MainSequence environment

### Install

```bash
pip install -e .
# or
uv pip install -e .
```

### Run The Curve Build

```bash
export BANXICO_TOKEN="<your-token>"
python scripts/build_curves.py
```

The runner seeds Banxico constants, registers the connector builders in
`mainsequence.instruments`, refreshes the Banxico source DataNode, ingests the
configured fixings, and then builds the Banxico zero curve.

## Deployment State

The repository implementation can exist before the platform state is fully
aligned. If the CLI returns no project resources, no project images, or no data
node updates, the code is present locally but not yet fully built or registered
 on the backend.

Use the current CLI commands below to verify the state that actually exists:

```bash
mainsequence project current --debug
mainsequence project jobs list 138 --timeout 60
mainsequence project data-node-updates list 138 --timeout 60
mainsequence project project_resource list 138 --path . --timeout 60
mainsequence project images list 138 --timeout 60
```

After the project is synced, imaged, and run successfully, the healthy state
should look like this:

- `mainsequence project jobs list 138 --timeout 60` shows the repository job
  from `scheduled_jobs.yaml`
- `mainsequence project images list 138 --timeout 60` shows at least one usable
  project image
- `mainsequence project project_resource list 138 --path . --timeout 60`
  returns resources for the current remote head, including the Banxico rates
  monitor dashboard
- `mainsequence project data-node-updates list 138 --timeout 60` shows update
  history for the Banxico source node, fixings, and discount-curve pipeline

If that state is missing, use the recovery flow documented in
`docs/deployment.md`.

## Schedule The ETL

Recurring jobs are managed through the current MainSequence batch scheduling
flow with `scheduled_jobs.yaml` at the repository root.

Submit the batch with:

```bash
mainsequence project schedule_batch_jobs scheduled_jobs.yaml 138 --path .
```

The current CLI prompts for the project image to apply to the batch and then
submits the normalized job list. The checked-in `related_image_id` in
`scheduled_jobs.yaml` should be treated as a placeholder/default because the CLI
can override it for the whole batch at submission time. This replaces the older
`project_configuration` style guidance for this project.

## Documentation

Project documentation lives under the standard `docs/` path and is organized to
match MainSequence concepts rather than only repository folders.

- `docs/index.md`: documentation entry point and navigation
- `docs/introduction.md`: project overview; this page intentionally mirrors the
  README
- `docs/deployment.md`: deployment state, working CLI commands, and recovery
  steps when backend state is missing
- `docs/data-nodes.md`: source DataNode definitions and stored fields
- `docs/markets.md`: MainSequence market assets, constants, and platform objects
- `docs/instruments.md`: `mainsequence.instruments` integration and instrument
  mapping logic
- `docs/dashboards.md`: dashboards currently shipped by the project

## Out Of Scope

This repository currently does not create:

- MainSequence portfolios
- asset translation tables
- portfolio analytics or a broader production analytics application beyond the
  current Banxico monitoring dashboard

## Key Entry Points

- `scheduled_jobs.yaml`: repository-managed batch job definition for the Banxico
  ETL
- `scripts/build_curves.py`: end-to-end runner for node refresh, fixings, and
  zero curve creation
- `banxico_connectors/data_nodes/banxico_mx_otr.py`: Banxico source DataNode
- `banxico_connectors/instruments/registry.py`: MainSequence registry wiring
- `banxico_connectors/instruments/rates_to_curves.py`: fixing updates and curve
  builders
- `dashboards/banxico_rates_monitor/app.py`: Banxico monitoring dashboard landing page
