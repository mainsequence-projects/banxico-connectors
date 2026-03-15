# Dashboards

## Current Dashboard

The repository currently ships one dashboard entry point:

- `dashboards/banxico_rates_monitor/app.py`

It is a Streamlit app built on top of
`mainsequence.dashboards.streamlit.scaffold`.

The dashboard package now includes the required sibling `README.md` expected by
the MainSequence Streamlit dashboard docs.

## What It Creates

The dashboard sets up a standard MainSequence multipage app with:

- Landing title: `Banxico Rates Monitor`
- Wide layout enabled
- MainSequence theme CSS injection enabled
- Shared data access helpers for:
  - `banxico_1d_otr_mxn`
  - `fixing_rates_1d`
  - `discount_curves`

The current pages are:

- `app.py`: landing page with table availability and source snapshot
- `pages/01_source_market_data.py`: source-node explorer
- `pages/02_fixings_and_curves.py`: fixings and zero-curve monitor
- `pages/03_platform_health.py`: table bindings, metadata, and deployment-health view

The dashboard still remains operational rather than analytical:

- it does not price portfolios
- it does not build portfolio views
- it does not create asset translation tables or other market-side application objects

## Package Contract

The current dashboard folder is expected to contain:

- `dashboards/banxico_rates_monitor/app.py`
- `dashboards/banxico_rates_monitor/README.md`
- `dashboards/banxico_rates_monitor/common.py`
- `dashboards/banxico_rates_monitor/pages/...`

This matches the current MainSequence dashboard guidance that each dashboard
folder should document its own app entry point.

## Why It Exists

This dashboard establishes the expected MainSequence dashboard runtime for the
project. It is the starting point for adding Banxico-specific visualizations on
top of the data and curve objects created by the connector.

## Deployment Note

If the backend shows historical dashboard jobs but `project_resource list`
returns no resources for the current remote head, treat the dashboard as a local
or legacy scaffold rather than a currently deployed Banxico app. Use the checks
in [Deployment And CLI](deployment.md).
