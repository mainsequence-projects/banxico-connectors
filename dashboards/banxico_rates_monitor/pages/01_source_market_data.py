from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

from mainsequence.dashboards.streamlit.scaffold import PageConfig, run_page

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboards.banxico_rates_monitor.common import (
    ON_THE_RUN_DATA_NODE_TABLE_NAME,
    build_asset_frame,
    default_start_date,
    enrich_source_frame,
    fetch_table_df,
    latest_rows,
)


run_page(
    PageConfig(
        title="Banxico Source Market Data",
        use_wide_layout=True,
        inject_theme_css=True,
    )
)

st.caption(
    "Explore the on-the-run Banxico source table that feeds the fixing and curve ETL."
)

lookback_days = st.sidebar.select_slider(
    "Lookback window (days)",
    options=[30, 60, 90, 180, 365, 730],
    value=180,
)

source_df = fetch_table_df(ON_THE_RUN_DATA_NODE_TABLE_NAME, start_date=default_start_date(lookback_days))
flat = enrich_source_frame(source_df)

if flat.empty:
    st.warning("No source-node observations are currently available for the selected lookback window.")
    st.stop()

families = sorted(flat["instrument_family"].dropna().unique().tolist())
selected_families = st.sidebar.multiselect("Instrument families", families, default=families)
filtered = flat[flat["instrument_family"].isin(selected_families)].copy() if selected_families else flat.copy()

types = sorted(filtered["type"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect("Instrument types", types, default=types)
filtered = filtered[filtered["type"].isin(selected_types)].copy() if selected_types else filtered

uids = sorted(filtered["unique_identifier"].dropna().astype(str).unique().tolist())
default_uids = uids[: min(8, len(uids))]
selected_uids = st.sidebar.multiselect("Instrument identifiers", uids, default=default_uids)
if selected_uids:
    filtered = filtered[filtered["unique_identifier"].isin(selected_uids)].copy()

if filtered.empty:
    st.warning("No source rows match the current filters.")
    st.stop()

metric = st.sidebar.selectbox(
    "Metric",
    [col for col in ["dirty_price", "clean_price", "current_coupon", "days_to_maturity"] if col in filtered.columns],
    index=0,
)

latest = latest_rows(filtered.set_index(["time_index", "unique_identifier"]) if {"time_index", "unique_identifier"}.issubset(filtered.columns) else filtered)
latest_ts = filtered["time_index"].max()

metric_cols = st.columns(4)
metric_cols[0].metric("Latest Date", latest_ts.strftime("%Y-%m-%d"))
metric_cols[1].metric("Instruments", f"{filtered['unique_identifier'].nunique():,}")
metric_cols[2].metric("Families", f"{filtered['instrument_family'].nunique():,}")
metric_cols[3].metric("Rows", f"{len(filtered):,}")

chart_df = filtered.dropna(subset=[metric]).copy()
if not chart_df.empty:
    fig = px.line(
        chart_df,
        x="time_index",
        y=metric,
        color="unique_identifier",
        title=f"{metric.replace('_', ' ').title()} History",
        hover_data=["instrument_family", "type", "quote_type", "coupon_type"],
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

latest_panel = latest.sort_values(["instrument_family", "unique_identifier"]).reset_index(drop=True)
st.markdown("### Latest Snapshot")
st.dataframe(latest_panel, width="stretch", hide_index=True)

coverage = (
    latest_panel.groupby(["instrument_family", "type"])["unique_identifier"]
    .nunique()
    .rename("instrument_count")
    .reset_index()
    .sort_values(["instrument_family", "type"])
)
if not coverage.empty:
    coverage_fig = px.bar(
        coverage,
        x="instrument_family",
        y="instrument_count",
        color="type",
        title="Latest Coverage By Family And Type",
        barmode="group",
    )
    coverage_fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(coverage_fig, use_container_width=True)

st.markdown("### Asset Registry Snapshot")
asset_frame = build_asset_frame(sorted(latest_panel["unique_identifier"].astype(str).unique().tolist()))
st.dataframe(asset_frame, width="stretch", hide_index=True)

st.markdown("### Raw Source Data")
st.dataframe(
    filtered.sort_values(["time_index", "instrument_family", "unique_identifier"], ascending=[False, True, True]),
    width="stretch",
    hide_index=True,
)
