from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

from mainsequence.dashboards.streamlit.scaffold import PageConfig, run_page

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboards.banxico_rates_monitor.common import (
    CURVES_TABLE_IDENTIFIER,
    FIXINGS_TABLE_IDENTIFIER,
    ON_THE_RUN_DATA_NODE_TABLE_NAME,
    availability_summary,
    default_start_date,
    enrich_source_frame,
    fetch_table_df,
    get_bindings,
    latest_rows,
    normalize_frame,
    render_binding_alert,
)


def _render_binding_cards() -> None:
    bindings = get_bindings()
    start_date = default_start_date(365)
    source_df = fetch_table_df(ON_THE_RUN_DATA_NODE_TABLE_NAME, start_date=start_date)
    fixings_df = fetch_table_df(FIXINGS_TABLE_IDENTIFIER, start_date=start_date)
    curves_df = fetch_table_df(CURVES_TABLE_IDENTIFIER, start_date=start_date)

    summaries = [
        (bindings["source"], source_df),
        (bindings["fixings"], fixings_df),
        (bindings["curves"], curves_df),
    ]
    cols = st.columns(3)
    for col, (binding, df) in zip(cols, summaries):
        summary = availability_summary(binding, df)
        with col:
            st.metric(binding.title, summary["status"], summary["latest_time_index"])
            st.caption(f"Rows: {summary['rows']} | Identifiers: {summary['identifiers']}")
            render_binding_alert(binding)


def _render_source_overview() -> None:
    df = fetch_table_df(ON_THE_RUN_DATA_NODE_TABLE_NAME, start_date=default_start_date(365))
    flat = enrich_source_frame(df)
    if flat.empty:
        st.info("No Banxico source data is currently available. Use the deployment checks and ETL job flow first.")
        return

    latest = latest_rows(flat.set_index(["time_index", "unique_identifier"]))
    if latest.empty:
        st.info("The source table exists but has no latest snapshot yet.")
        return

    coverage = (
        latest.groupby("instrument_family")["unique_identifier"]
        .nunique()
        .rename("instrument_count")
        .reset_index()
        .sort_values("instrument_count", ascending=False)
    )
    fig = px.bar(
        coverage,
        x="instrument_family",
        y="instrument_count",
        title="Latest Source Coverage By Instrument Family",
        color="instrument_family",
    )
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(4)
    latest_ts = latest["time_index"].max()
    cols[0].metric("Latest Source Date", latest_ts.strftime("%Y-%m-%d"))
    cols[1].metric("Latest Instruments", f"{latest['unique_identifier'].nunique():,}")
    cols[2].metric("Families", f"{latest['instrument_family'].nunique():,}")
    cols[3].metric(
        "Avg Days To Maturity",
        f"{latest['days_to_maturity'].dropna().astype(float).mean():.0f}",
    )

    st.dataframe(
        latest.sort_values(["instrument_family", "unique_identifier"]).reset_index(drop=True),
        width="stretch",
        hide_index=True,
    )


ctx = run_page(
    PageConfig(
        title="Banxico Rates Monitor",
        use_wide_layout=True,
        inject_theme_css=True,
    )
)

st.caption(
    "Monitor the Banxico source node, the downstream fixing rates table, and the bootstrapped "
    "discount-curve output created through MainSequence."
)

_render_binding_cards()

st.markdown("### Navigate")
nav_cols = st.columns(3)
nav_cols[0].page_link("pages/01_source_market_data.py", label="Open Source Market Data", icon="📊")
nav_cols[1].page_link("pages/02_fixings_and_curves.py", label="Open Fixings And Curves", icon="📈")
nav_cols[2].page_link("pages/03_platform_health.py", label="Open Platform Health", icon="🩺")

st.markdown("### Source Snapshot")
_render_source_overview()
