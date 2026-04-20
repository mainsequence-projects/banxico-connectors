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
    CURVES_TABLE_IDENTIFIER,
    FIXINGS_TABLE_IDENTIFIER,
    decode_curve_frame,
    render_backend_status,
    default_start_date,
    fetch_table_df,
    latest_rows,
    normalize_frame,
    render_future_rows_warning,
    separate_future_rows,
)


run_page(
    PageConfig(
        title="Fixings And Curves",
        use_wide_layout=True,
        inject_theme_css=True,
    )
)

st.caption(
    "Inspect the MainSequence fixing-rates table and the Banxico zero-curve output built from the source node."
)

if render_backend_status():
    st.stop()

lookback_days = st.sidebar.select_slider(
    "Lookback window (days)",
    options=[30, 60, 90, 180, 365, 730],
    value=180,
)
start_date = default_start_date(lookback_days)

fixings_df, future_fixings = separate_future_rows(fetch_table_df(FIXINGS_TABLE_IDENTIFIER, start_date=start_date))
curves_flat, future_curves = separate_future_rows(
    decode_curve_frame(fetch_table_df(CURVES_TABLE_IDENTIFIER, start_date=start_date))
)

st.markdown("### Fixings")
render_future_rows_warning("Fixing Rates Node", future_fixings)
if fixings_df.empty:
    st.warning("No fixing-rates data is available yet.")
else:
    fixing_uids = sorted(fixings_df["unique_identifier"].dropna().astype(str).unique().tolist())
    selected_fixings = st.sidebar.multiselect("Fixings", fixing_uids, default=fixing_uids)
    filtered_fixings = (
        fixings_df[fixings_df["unique_identifier"].isin(selected_fixings)].copy()
        if selected_fixings
        else fixings_df.copy()
    )
    if filtered_fixings.empty:
        st.info("No fixing rows match the current selection.")
    else:
        latest_fixings = latest_rows(filtered_fixings.set_index(["time_index", "unique_identifier"]))
        fix_cols = st.columns(3)
        fix_cols[0].metric("Latest Fixing Date", filtered_fixings["time_index"].max().strftime("%Y-%m-%d"))
        fix_cols[1].metric("Fixing Series", f"{filtered_fixings['unique_identifier'].nunique():,}")
        fix_cols[2].metric("Latest Rows", f"{len(latest_fixings):,}")

        fix_fig = px.line(
            filtered_fixings,
            x="time_index",
            y="rate",
            color="unique_identifier",
            title="Fixing Rates History",
        )
        fix_fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fix_fig, width="stretch")
        st.dataframe(
            latest_fixings.sort_values("unique_identifier").reset_index(drop=True),
            width="stretch",
            hide_index=True,
        )

st.markdown("### Zero Curves")
render_future_rows_warning("Discount Curves Node", future_curves)
if curves_flat.empty:
    st.warning("No discount-curve data is available yet.")
else:
    curve_uids = sorted(curves_flat["unique_identifier"].dropna().astype(str).unique().tolist())
    selected_curve = st.sidebar.selectbox("Curve identifier", curve_uids, index=0)
    filtered_curves = curves_flat[curves_flat["unique_identifier"] == selected_curve].copy()
    available_dates = (
        filtered_curves["time_index"]
        .dropna()
        .sort_values()
        .dt.strftime("%Y-%m-%d")
        .unique()
        .tolist()
    )
    default_date = available_dates[-1]
    compare_date = available_dates[max(0, len(available_dates) - 6)]
    selected_dates = st.sidebar.multiselect(
        "Curve dates to compare",
        available_dates,
        default=[compare_date, default_date] if compare_date != default_date else [default_date],
    )
    selected_curves = filtered_curves[
        filtered_curves["time_index"].dt.strftime("%Y-%m-%d").isin(selected_dates)
    ].copy()
    if selected_curves.empty:
        st.info("No curve snapshots match the selected dates.")
    else:
        selected_curves["curve_date"] = selected_curves["time_index"].dt.strftime("%Y-%m-%d")

        curve_cols = st.columns(3)
        curve_cols[0].metric("Latest Curve Date", filtered_curves["time_index"].max().strftime("%Y-%m-%d"))
        curve_cols[1].metric("Tenor Points", f"{filtered_curves['days_to_maturity'].nunique():,}")
        curve_cols[2].metric("Curve Snapshots", f"{filtered_curves['time_index'].nunique():,}")

        curve_fig = px.line(
            selected_curves,
            x="days_to_maturity",
            y="zero_rate",
            color="curve_date",
            title=f"Zero Curve Comparison: {selected_curve}",
            markers=True,
        )
        curve_fig.update_layout(
            xaxis_title="Days to maturity",
            yaxis_title="Zero rate (decimal)",
            legend_title="Curve date",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(curve_fig, width="stretch")

        latest_curve = latest_rows(filtered_curves.set_index(["time_index", "unique_identifier"]))
        st.dataframe(
            latest_curve.sort_values("days_to_maturity").reset_index(drop=True),
            width="stretch",
            hide_index=True,
        )
