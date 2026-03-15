# Introduction

`banxico-connectors` extends `mainsequence` with Banxico SIE market data for
Mexican rates. It loads on-the-run government instruments and the Banxico
target rate, stores them in a daily MainSequence DataNode, publishes TIIE and
CETE fixings, and bootstraps an MXN zero curve that can be consumed by
MainSequence pricing models and dashboards.

## What The Project Does

- Pulls Banxico SIE series for CETES, M Bonos, Bondes D, Bondes F, Bondes G,
  and the Banxico target rate.
- Registers Banxico-specific market assets and MainSequence constants.
- Builds MainSequence fixing datasets for TIIE and CETE reference rates.
- Builds a MainSequence discount curve from Banxico on-the-run instruments.
- Includes a Streamlit dashboard scaffold that uses the MainSequence dashboard
  runtime.

## MainSequence Alignment

The project follows MainSequence concepts directly:

- Source market data is exposed through a `DataNode`.
- Market identifiers are registered as MainSequence `Asset` and `Constant`
  objects.
- Curve and fixing ETL builders are registered through
  `mainsequence.instruments`.
- A Streamlit dashboard uses the MainSequence dashboard scaffold instead of a
  standalone app shell.

## Main Entry Points

- `scripts/build_curves.py` runs the end-to-end workflow.
- `banxico_connectors/data_nodes/nodes.py` defines the Banxico source node.
- `banxico_connectors/instruments/registry.py` wires the connector into
  MainSequence registries.
- `banxico_connectors/instruments/rates_to_curves.py` contains the Banxico
  fixing and curve-building logic.
- `dashboards/sample_app/app.py` is the current dashboard entry point.
