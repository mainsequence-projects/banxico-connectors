<p align="center">
<img src="https://main-sequence.app/static/media/logos/MS_logo_long_black.png" alt="Main Sequence Logo" width="500"/>
</p>

# banxico-connectors

`banxico-connectors` extends `mainsequence` with Banxico SIE market data for Mexican
rates. It loads on-the-run government instruments and the Banxico target rate,
stores them in a daily MainSequence DataNode, publishes TIIE and CETE fixings,
and bootstraps an MXN zero curve that can be consumed by MainSequence pricing
models and dashboards.

## What The Project Does

- Pulls Banxico SIE series for CETES, M Bonos, Bondes D, Bondes F, Bondes G,
  and the Banxico target rate.
- Registers Banxico-specific market assets and MainSequence constants.
- Builds MainSequence fixing datasets for TIIE and CETE reference rates.
- Builds a MainSequence discount curve from Banxico on-the-run instruments.
- Includes a Streamlit dashboard scaffold that uses the MainSequence dashboard
  runtime.

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

## Documentation

Project documentation lives under the standard `docs/` path and is organized to
match MainSequence concepts rather than only repository folders.

- `docs/index.md`: documentation entry point and navigation
- `docs/introduction.md`: project overview; this page intentionally mirrors the
  README
- `docs/data-nodes.md`: source DataNode definitions and stored fields
- `docs/markets.md`: MainSequence market assets, constants, and platform objects
- `docs/instruments.md`: `mainsequence.instruments` integration and instrument
  mapping logic
- `docs/dashboards.md`: dashboards currently shipped by the project

## Key Entry Points

- `scripts/build_curves.py`: end-to-end runner for node refresh, fixings, and
  zero curve creation
- `banxico_connectors/data_nodes/nodes.py`: Banxico source DataNode
- `banxico_connectors/instruments/registry.py`: MainSequence registry wiring
- `banxico_connectors/instruments/rates_to_curves.py`: fixing updates and curve
  builders
- `dashboards/sample_app/app.py`: sample dashboard scaffold
