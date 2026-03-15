# Dashboards

## Current Dashboard

The repository currently ships one dashboard entry point:

- `dashboards/sample_app/app.py`

It is a minimal Streamlit page built on top of
`mainsequence.dashboards.streamlit.scaffold`.

## What It Creates

The dashboard sets up a standard MainSequence Streamlit page with:

- Title: `Main Sequence Demo App`
- Wide layout enabled
- MainSequence theme CSS injection enabled

At the moment, the page only renders a small caption and acts as a scaffold:

- It does not yet query the Banxico DataNode
- It does not yet visualize fixings or zero curves
- It does not yet create domain-specific Banxico dashboard pages

## Why It Exists

This dashboard establishes the expected MainSequence dashboard runtime for the
project. It is the starting point for adding Banxico-specific visualizations on
top of the data and curve objects created by the connector.
