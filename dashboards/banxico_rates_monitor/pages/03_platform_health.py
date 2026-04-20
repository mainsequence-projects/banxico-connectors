from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from mainsequence.dashboards.streamlit.scaffold import PageConfig, run_page

ROOT = Path(__file__).resolve().parents[3]
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
    render_backend_status,
    normalize_frame,
    render_future_rows_warning,
    render_binding_alert,
    separate_future_rows,
    storage_data_source_id,
)


run_page(
    PageConfig(
        title="Platform Health And Metadata",
        use_wide_layout=True,
        inject_theme_css=True,
    )
)

st.caption(
    "Check table bindings, storage metadata, and backend availability for the Banxico dashboard inputs."
)

if render_backend_status():
    st.stop()

bindings = get_bindings()
start_date = default_start_date(365)
source_df = fetch_table_df(ON_THE_RUN_DATA_NODE_TABLE_NAME, start_date=start_date)
fixings_df = fetch_table_df(FIXINGS_TABLE_IDENTIFIER, start_date=start_date)
curves_df = fetch_table_df(CURVES_TABLE_IDENTIFIER, start_date=start_date)
source_current, source_future = separate_future_rows(source_df)
fixings_current, fixings_future = separate_future_rows(fixings_df)
curves_current, curves_future = separate_future_rows(curves_df)

table_rows = []
for key, raw_df, df, future_df in [
    ("source", source_df, source_current, source_future),
    ("fixings", fixings_df, fixings_current, fixings_future),
    ("curves", curves_df, curves_current, curves_future),
]:
    binding = bindings[key]
    summary = availability_summary(binding, raw_df)
    table_rows.append(
        {
            "title": binding.title,
            "identifier": binding.identifier,
            "storage_hash": binding.storage.storage_hash if binding.storage else None,
            "data_source_id": storage_data_source_id(binding.storage) if binding.storage else None,
            "status": summary["status"],
            "latest_time_index": summary["latest_time_index"],
            "rows": summary["rows"],
            "identifiers": summary["identifiers"],
            "future_rows": f"{len(future_df):,}",
            "future_latest_time_index": (
                future_df["time_index"].max().strftime("%Y-%m-%d")
                if not future_df.empty and "time_index" in future_df.columns
                else "-"
            ),
        }
    )

st.markdown("### Table Availability")
st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

for binding in bindings.values():
    render_binding_alert(binding)

render_future_rows_warning(bindings["source"].title, source_future)
render_future_rows_warning(bindings["fixings"].title, fixings_future)
render_future_rows_warning(bindings["curves"].title, curves_future)

st.markdown("### Healthy Deployment Checklist")
st.markdown(
    """
- `banxico_1d_otr_mxn` resolves to a storage node and returns recent rows.
- `fixing_rates_1d` resolves and returns TIIE/CETE decimal fixings.
- `discount_curves` resolves and returns compressed curve payloads.
- The scheduled ETL job exists in the project and has recent successful runs.
- The current remote head has project resources for the dashboard package.
"""
)

st.markdown("### Storage Metadata")
choice = st.selectbox(
    "Inspect table metadata",
    options=list(bindings.keys()),
    format_func=lambda key: bindings[key].title,
)
binding = bindings[choice]
if binding.storage is not None:
    payload = binding.storage.model_dump(mode="json")
    st.json(payload, expanded=False)
else:
    st.info(f"No storage metadata is currently available for `{binding.identifier}`.")

st.markdown("### Data Preview")
preview_df = normalize_frame(
    {
        "source": enrich_source_frame(source_current),
        "fixings": fixings_current,
        "curves": curves_current,
    }[choice]
)
if preview_df.empty:
    st.info("No rows available for preview.")
else:
    st.dataframe(preview_df.head(200), width="stretch", hide_index=True)
