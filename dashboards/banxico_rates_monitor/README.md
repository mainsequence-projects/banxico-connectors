# Banxico Rates Monitor

## Purpose

`dashboards/banxico_rates_monitor/app.py` is the current MainSequence Streamlit dashboard
entry point shipped with this repository.

It started as a scaffold and now serves as an operational monitoring app:

- it bootstraps the MainSequence Streamlit runtime,
- it reads the Banxico source, fixing, and curve tables through `APIDataNode`,
- and it provides a multipage monitoring surface for the current connector.

## Current Behavior

The app currently:

- sets the landing page title to `Banxico Rates Monitor`
- shows table availability for:
  - `banxico_1d_otr_mxn`
  - `fixing_rates_1d`
  - `discount_curves`
- includes the following pages:
  - `pages/01_source_market_data.py`
  - `pages/02_fixings_and_curves.py`
  - `pages/03_platform_health.py`

The dashboard focuses on monitoring and exploration. It does not yet perform
instrument-level pricing analysis or portfolio analytics.

## Deployment

The repository-managed dashboard contract for this folder is:

- `dashboards/banxico_rates_monitor/app.py`
- `dashboards/banxico_rates_monitor/README.md`

To verify whether the current remote head has a deployed dashboard resource, use
the commands documented in `docs/deployment.md`.
