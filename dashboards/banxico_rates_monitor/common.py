"""Shared data-access helpers for the Banxico rates monitor dashboard."""

from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Any

import pandas as pd
import pytz
import streamlit as st


def _backend_auth_error() -> str | None:
    if (
        not os.getenv("MAINSEQUENCE_ACCESS_TOKEN")
        and not os.getenv("MAINSEQUENCE_REFRESH_TOKEN")
    ):
        return "Authentication env is missing. Set MAINSEQUENCE_ACCESS_TOKEN / MAINSEQUENCE_REFRESH_TOKEN."
    return None


def _curve_decode_fallback(_value: Any) -> dict[str, float]:
    return {}


_MAINSEQUENCE_IMPORT_ERROR = _backend_auth_error()
msc = None
APIDataNode = None
decompress_string_to_curve = _curve_decode_fallback

if _MAINSEQUENCE_IMPORT_ERROR is None:
    try:
        from mainsequence.instruments.interest_rates.etl.curve_codec import (
            decompress_string_to_curve as _decompress_string_to_curve,
        )
        import mainsequence.client as msc
        from mainsequence.tdag import APIDataNode  # type: ignore[import]
    except Exception as exc:
        msc = None
        APIDataNode = None
        _MAINSEQUENCE_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
    else:
        decompress_string_to_curve = _decompress_string_to_curve

UTC = pytz.UTC
ON_THE_RUN_DATA_NODE_TABLE_NAME = "banxico_1d_otr_mxn"
FIXINGS_TABLE_IDENTIFIER = "fixing_rates_1d"
CURVES_TABLE_IDENTIFIER = "discount_curves"
DEFAULT_LOOKBACK_DAYS = 180


@dataclass(frozen=True)
class TableBinding:
    identifier: str
    title: str
    description: str
    storage: msc.DataNodeStorage | None
    node: APIDataNode | None
    error: str | None = None

    @property
    def available(self) -> bool:
        return self.storage is not None and self.node is not None and self.error is None


def client_import_error() -> str | None:
    """Return a user-facing reason for why the MainSequence client is unavailable."""
    return _MAINSEQUENCE_IMPORT_ERROR


def render_backend_status() -> bool:
    """Render a clear backend error banner when MainSequence cannot be used."""
    reason = client_import_error()
    if reason is None:
        return False
    st.error("MainSequence backend is currently unavailable.")
    st.caption(reason)
    return True


def _coerce_zero_rate_to_decimal(rate: Any) -> float:
    """Handle legacy curve rows stored as percent (e.g. 7.5) by normalizing to decimal."""
    if rate is None or pd.isna(rate):
        return float("nan")
    try:
        value = float(rate)
    except (TypeError, ValueError):
        return float("nan")
    return value / 100.0 if abs(value) > 2.0 else value


def _utc_now() -> pd.Timestamp:
    return pd.Timestamp.now(tz=UTC)


def default_start_date(days: int = DEFAULT_LOOKBACK_DAYS) -> pd.Timestamp:
    return (_utc_now() - pd.Timedelta(days=days)).normalize()


def storage_data_source_id(storage: msc.DataNodeStorage) -> int:
    data_source = storage.data_source
    return data_source.id if hasattr(data_source, "id") else int(data_source)


@st.cache_resource(show_spinner=False)
def get_table_binding(identifier: str, title: str, description: str) -> TableBinding:
    if client_import_error() is not None:
        return TableBinding(
            identifier=identifier,
            title=title,
            description=description,
            storage=None,
            node=None,
            error=client_import_error(),
        )
    if msc is None or APIDataNode is None:
        return TableBinding(
            identifier=identifier,
            title=title,
            description=description,
            storage=None,
            node=None,
            error="MainSequence runtime modules are not available in this environment.",
        )
    try:
        storage = msc.DataNodeStorage.get(identifier=identifier)
        node = APIDataNode(
            data_source_id=storage_data_source_id(storage),
            storage_hash=storage.storage_hash,
        )
        return TableBinding(
            identifier=identifier,
            title=title,
            description=description,
            storage=storage,
            node=node,
        )
    except Exception as exc:
        return TableBinding(
            identifier=identifier,
            title=title,
            description=description,
            storage=None,
            node=None,
            error=str(exc),
        )


def get_bindings() -> dict[str, TableBinding]:
    return {
        "source": get_table_binding(
            ON_THE_RUN_DATA_NODE_TABLE_NAME,
            "Banxico Source Node",
            "On-the-run Banxico market observations used as the source layer for fixings and curve construction.",
        ),
        "fixings": get_table_binding(
            FIXINGS_TABLE_IDENTIFIER,
            "Fixing Rates Node",
            "Daily decimal fixings published by MainSequence for TIIE and CETE reference rates.",
        ),
        "curves": get_table_binding(
            CURVES_TABLE_IDENTIFIER,
            "Discount Curves Node",
            "Compressed zero-curve payloads built by MainSequence discount-curve ETL.",
        ),
    }


@st.cache_data(show_spinner=False, ttl=120)
def fetch_table_df(
    identifier: str,
    start_date: pd.Timestamp | None = None,
    end_date: pd.Timestamp | None = None,
    unique_identifier_list: list[str] | None = None,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    bindings = get_bindings()
    binding = next((b for b in bindings.values() if b.identifier == identifier), None)
    if binding is None or not binding.available or binding.node is None:
        return pd.DataFrame()

    start = start_date.to_pydatetime() if isinstance(start_date, pd.Timestamp) else start_date
    end = end_date.to_pydatetime() if isinstance(end_date, pd.Timestamp) else end_date

    try:
        return binding.node.get_df_between_dates(
            start_date=start,
            end_date=end,
            unique_identifier_list=unique_identifier_list,
            columns=columns,
        )
    except Exception:
        return pd.DataFrame()


def normalize_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if isinstance(out.index, pd.MultiIndex):
        out = out.reset_index()
    elif "time_index" in out.columns:
        out = out.reset_index(drop=True)
    else:
        out = out.reset_index(names=["time_index"])
    if "time_index" in out.columns:
        out["time_index"] = pd.to_datetime(out["time_index"], utc=True, errors="coerce")
    return out


def separate_future_rows(
    df: pd.DataFrame,
    *,
    cutoff: pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    flat = normalize_frame(df)
    if flat.empty or "time_index" not in flat.columns:
        return flat, flat.iloc[0:0].copy()

    cutoff_ts = (cutoff or _utc_now()).normalize()
    future_mask = flat["time_index"] > cutoff_ts
    return flat.loc[~future_mask].copy(), flat.loc[future_mask].copy()


def render_future_rows_warning(
    title: str,
    future_df: pd.DataFrame,
    *,
    cutoff: pd.Timestamp | None = None,
) -> None:
    if future_df.empty or "time_index" not in future_df.columns:
        return
    cutoff_ts = (cutoff or _utc_now()).normalize()
    earliest = future_df["time_index"].min()
    latest = future_df["time_index"].max()
    st.warning(
        f"{title} contains {len(future_df):,} future-dated rows beyond {cutoff_ts.strftime('%Y-%m-%d')}. "
        f"Earliest future date: {earliest.strftime('%Y-%m-%d')}. "
        f"Latest future date: {latest.strftime('%Y-%m-%d')}. "
        "The dashboard is excluding those rows from charts and latest-snapshot views. "
        "This usually comes from an earlier DD/MM/YYYY parsing bug in the Banxico source loader."
    )


def enrich_source_frame(df: pd.DataFrame) -> pd.DataFrame:
    flat = normalize_frame(df)
    if flat.empty:
        return flat

    uid_series = flat["unique_identifier"].astype(str) if "unique_identifier" in flat.columns else pd.Series("", index=flat.index)

    if "type" not in flat.columns:
        flat["type"] = "unknown"
        flat.loc[uid_series.str.startswith("MCET_"), "type"] = "zero_coupon"
        flat.loc[uid_series.str.startswith("MBONO_"), "type"] = "fixed_bond"
        flat.loc[uid_series.str.startswith("BONDES_D_"), "type"] = "floating_bondes_d"
        flat.loc[uid_series.str.startswith("BONDES_F_"), "type"] = "floating_bondes_f"
        flat.loc[uid_series.str.startswith("BONDES_G_"), "type"] = "floating_bondes_g"
        flat.loc[uid_series.eq("BANXICO_TARGET_RATE"), "type"] = "overnight_rate"

    if "instrument_family" not in flat.columns:
        flat["instrument_family"] = "unknown"
        flat.loc[uid_series.str.startswith("MCET_"), "instrument_family"] = "cetes"
        flat.loc[uid_series.str.startswith("MBONO_"), "instrument_family"] = "bonos"
        flat.loc[uid_series.str.startswith("BONDES_D_"), "instrument_family"] = "bondes_d"
        flat.loc[uid_series.str.startswith("BONDES_F_"), "instrument_family"] = "bondes_f"
        flat.loc[uid_series.str.startswith("BONDES_G_"), "instrument_family"] = "bondes_g"
        flat.loc[uid_series.eq("BANXICO_TARGET_RATE"), "instrument_family"] = "banxico_target_rate"

    if "quote_type" not in flat.columns:
        flat["quote_type"] = "price"
        flat.loc[uid_series.eq("BANXICO_TARGET_RATE"), "quote_type"] = "rate"

    if "coupon_type" not in flat.columns:
        flat["coupon_type"] = "none"
        flat.loc[flat["type"].eq("fixed_bond"), "coupon_type"] = "coupon"
        flat.loc[
            flat["type"].isin(["floating_bondes_d", "floating_bondes_f", "floating_bondes_g"]),
            "coupon_type",
        ] = "spread_like_rate"

    return flat


def latest_rows(df: pd.DataFrame) -> pd.DataFrame:
    flat = normalize_frame(df)
    if flat.empty or "time_index" not in flat.columns:
        return flat
    latest = flat["time_index"].max()
    return flat[flat["time_index"] == latest].copy()


def available_identifiers(df: pd.DataFrame) -> list[str]:
    flat = normalize_frame(df)
    if flat.empty or "unique_identifier" not in flat.columns:
        return []
    return sorted(flat["unique_identifier"].dropna().astype(str).unique().tolist())


def source_metric_options(df: pd.DataFrame) -> list[str]:
    flat = normalize_frame(df)
    preferred = [
        "dirty_price",
        "clean_price",
        "current_coupon",
        "days_to_maturity",
    ]
    return [col for col in preferred if col in flat.columns]


@st.cache_data(show_spinner=False, ttl=120)
def fetch_assets(unique_identifiers: tuple[str, ...]) -> list[Any]:
    if client_import_error() is not None or msc is None:
        return []
    if not unique_identifiers:
        return []
    try:
        return list(msc.Asset.query(unique_identifier__in=list(unique_identifiers)))
    except Exception:
        return []


def build_asset_frame(unique_identifiers: list[str]) -> pd.DataFrame:
    assets = fetch_assets(tuple(unique_identifiers))
    if not assets:
        return pd.DataFrame(columns=["unique_identifier", "name", "ticker", "exchange_code"])
    rows: list[dict[str, Any]] = []
    for asset in assets:
        snapshot = getattr(asset, "snapshot", None) or {}
        rows.append(
            {
                "unique_identifier": getattr(asset, "unique_identifier", None),
                "name": snapshot.get("name"),
                "ticker": getattr(asset, "ticker", None) or snapshot.get("ticker"),
                "exchange_code": snapshot.get("exchange_code"),
            }
        )
    return pd.DataFrame(rows).sort_values("unique_identifier")


def decode_curve_frame(df: pd.DataFrame) -> pd.DataFrame:
    flat = normalize_frame(df)
    if flat.empty or "curve" not in flat.columns:
        return pd.DataFrame(columns=["time_index", "unique_identifier", "days_to_maturity", "zero_rate"])

    rows: list[dict[str, Any]] = []
    for row in flat.itertuples(index=False):
        try:
            curve_dict = decompress_string_to_curve(getattr(row, "curve"))
        except Exception:
            continue
        for tenor, zero_rate in sorted(curve_dict.items(), key=lambda item: float(item[0])):
            rows.append(
                {
                    "time_index": getattr(row, "time_index"),
                    "unique_identifier": getattr(row, "unique_identifier"),
                    "days_to_maturity": float(tenor),
                    "zero_rate": _coerce_zero_rate_to_decimal(zero_rate),
                }
            )
    if not rows:
        return pd.DataFrame(columns=["time_index", "unique_identifier", "days_to_maturity", "zero_rate"])
    out = pd.DataFrame(rows)
    out["time_index"] = pd.to_datetime(out["time_index"], utc=True, errors="coerce")
    return out.sort_values(["time_index", "unique_identifier", "days_to_maturity"])


def availability_summary(binding: TableBinding, df: pd.DataFrame) -> dict[str, str]:
    if not binding.available:
        return {
            "status": "Unavailable",
            "latest_time_index": "-",
            "rows": "0",
            "identifiers": "0",
        }
    flat, future = separate_future_rows(df)
    latest = "-"
    identifiers = 0
    if not flat.empty and "time_index" in flat.columns:
        latest_ts = flat["time_index"].max()
        latest = latest_ts.strftime("%Y-%m-%d") if pd.notna(latest_ts) else "-"
    if not flat.empty and "unique_identifier" in flat.columns:
        identifiers = flat["unique_identifier"].nunique()
    return {
        "status": (
            "Available + Future Rows"
            if not flat.empty and not future.empty
            else "Future Rows Only"
            if flat.empty and not future.empty
            else "Available"
            if not flat.empty
            else "Empty"
        ),
        "latest_time_index": latest,
        "rows": f"{len(flat):,}",
        "identifiers": f"{identifiers:,}",
    }


def render_binding_alert(binding: TableBinding) -> None:
    if binding.available:
        return
    st.warning(
        f"{binding.title} is not currently available from the backend. "
        f"Identifier: `{binding.identifier}`. "
        f"{binding.error or 'No storage binding could be resolved.'}"
    )


def date_window_label(start: pd.Timestamp, end: pd.Timestamp | None) -> str:
    end_label = (end or _utc_now()).strftime("%Y-%m-%d")
    return f"{start.strftime('%Y-%m-%d')} to {end_label}"
