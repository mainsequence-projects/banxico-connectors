import datetime
from typing import Callable, Mapping, Optional

import pandas as pd
import pytz

from banxico_connectors.utils import fetch_banxico_series_batched, to_long_with_aliases
from banxico_connectors.settings import (
    BANXICO_TARGET_RATE,
    get_banxico_target_rate_id_map,
    get_banxico_token,
    get_cete_fixing_id_map,
    get_tiie_fixing_id_map,
)

from .bootstrap import bootstrap_from_curve_df


def _normalize_multiindex_time_index(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if not isinstance(df.index, pd.MultiIndex) or "time_index" not in df.index.names:
        raise ValueError("Output must be indexed by time_index and unique_identifier.")

    time_index = pd.DatetimeIndex(
        pd.to_datetime(df.index.get_level_values("time_index"), utc=True)
    ).astype("datetime64[ns, UTC]")
    unique_identifier = df.index.get_level_values("unique_identifier")

    normalized = df.copy()
    normalized.index = pd.MultiIndex.from_arrays(
        [time_index, unique_identifier],
        names=["time_index", "unique_identifier"],
    )
    return normalized.sort_index()


def _to_utc_midnight(value) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")
    return timestamp.normalize()


def _read_banxico_target_rate_fixing_series(start_date, end_date) -> pd.Series:
    start_ts = _to_utc_midnight(start_date)
    end_ts = _to_utc_midnight(end_date)
    if start_ts > end_ts:
        return pd.Series(dtype="float64")

    from mainsequence.instruments.interest_rates.etl.nodes import FixingRatesNode

    from banxico_connectors.instruments.configs import build_banxico_fixing_rate_config

    fixing_node = FixingRatesNode(rates_config=build_banxico_fixing_rate_config())
    if fixing_node.data_node_update is None:
        fixing_node.run(force_update=True)
    lookback_start = start_ts - pd.Timedelta(days=370)
    fixings = fixing_node.get_df_between_dates(
        start_date=lookback_start.to_pydatetime(),
        great_or_equal=True,
    )
    if fixings.empty:
        return pd.Series(dtype="float64")

    flat = fixings.reset_index()
    if "unique_identifier" in flat.columns:
        flat = flat[flat["unique_identifier"] == BANXICO_TARGET_RATE]
    if flat.empty:
        return pd.Series(dtype="float64")

    flat["time_index"] = pd.DatetimeIndex(
        pd.to_datetime(flat["time_index"], utc=True)
    ).astype("datetime64[ns, UTC]").normalize()
    flat["rate"] = pd.to_numeric(flat["rate"], errors="coerce")
    rates = (
        flat[(flat["time_index"] <= end_ts) & flat["rate"].notna()]
        .sort_values("time_index")
        .drop_duplicates(subset=["time_index"], keep="last")
        .set_index("time_index")["rate"]
    )
    return rates.astype("float64")


def _target_rate_for_time_index(target_rates: pd.Series, time_index) -> float | None:
    if target_rates.empty:
        return None
    lookup_ts = _to_utc_midnight(time_index)
    eligible = target_rates.loc[target_rates.index <= lookup_ts]
    if eligible.empty:
        return None
    return float(eligible.iloc[-1])


def _append_overnight_anchor(curve_df: pd.DataFrame, time_index, target_rate: float) -> pd.DataFrame:
    overnight_row = pd.DataFrame(
        [
            {
                "time_index": _to_utc_midnight(time_index),
                "unique_identifier": BANXICO_TARGET_RATE,
                "days_to_maturity": 1.0,
                "clean_price": pd.NA,
                "dirty_price": target_rate,
                "current_coupon": pd.NA,
                "type": "overnight_rate",
                "instrument_family": "banxico_target_rate",
                "quote_type": "rate",
                "coupon_type": "none",
            }
        ]
    ).set_index(["time_index", "unique_identifier"])
    return pd.concat([curve_df, overnight_row], sort=False)


def boostrap_mbono_curve(update_statistics, curve_unique_identifier: str, base_node_curve_points=None):
    """
    For each time_index:
      1) Reads node data from `base_node_curve_points` since the last_update.
      2) Bootstraps the zero curve using:
         - overnight_rate (Banxico target) as a 1-day anchor,
         - zero_coupon (Cetes, face = 10),
         - fixed_bond (Mbonos, 182-day coupons, uses clean price).
      3) Returns ONE dataframe with columns:
           time_index, days_to_maturity, zero_rate

    Assumptions:
      - Money-market simple yield Act/360 (consistent with your IRS code).
      - MBono coupon schedule is built in QuantLib with 182-day coupon spacing.
      - Required columns in input frame: ['time_index','type','tenor_days','clean_price','dirty_price','coupon'].
        For overnight rows, use 'dirty_price' to carry the annual rate (e.g. 0.0725).
    """
    # Last processed point for this curve identifier
    last_update = update_statistics.asset_time_statistics[curve_unique_identifier]

    if base_node_curve_points is None:
        from banxico_connectors.data_nodes.banxico_mx_otr import BanxicoMXNOTR, BanxicoMXNOTRConfig

        base_node_curve_points = BanxicoMXNOTR(config=BanxicoMXNOTRConfig())

    # Pull nodes since last update (inclusive)
    nodes_data_df = base_node_curve_points.get_df_between_dates(
        start_date=last_update,
        great_or_equal=True
    )


    if nodes_data_df.empty:
        # Return empty frame with the expected schema
        return pd.DataFrame()

    target_rates = _read_banxico_target_rate_fixing_series(
        start_date=last_update,
        end_date=nodes_data_df.index.get_level_values("time_index").max(),
    )

    results = []

    # Bootstrap per time_index
    for time_index, curve_df in nodes_data_df.groupby("time_index"):

        target_rate = _target_rate_for_time_index(target_rates, time_index)
        if target_rate is None:
            continue
        curve_df = _append_overnight_anchor(curve_df.copy(), time_index, target_rate)
        curve_df = curve_df[
            curve_df["type"].isin(
                {
                    "overnight_rate",
                    "zero_coupon",
                    "fixed_bond",
                }
            )
        ]

        if curve_df.shape[0] < 5:
            continue

        # robust numeric casting
        curve_df["tenor_days"] = pd.to_numeric(curve_df["days_to_maturity"], errors="coerce")
        curve_df["clean_price"] = pd.to_numeric(curve_df["clean_price"], errors="coerce")
        curve_df["dirty_price"] = pd.to_numeric(curve_df["dirty_price"], errors="coerce")
        curve_df["coupon"] = pd.to_numeric(curve_df["current_coupon"], errors="coerce")

        # Bootstrap one slice
        try:
            zero_df = bootstrap_from_curve_df(curve_df)
        except Exception as e:
            raise e

        zero_df.insert(0, "time_index", time_index)
        results.append(zero_df)
    if len(results)==0:
        return pd.DataFrame()
    final_df = pd.concat(results, ignore_index=True)
    final_df["unique_identifier"]=curve_unique_identifier

    grouped = (
        final_df.groupby(["time_index", "unique_identifier"])
        .apply(lambda g: g.set_index("days_to_maturity")["zero_rate"].to_dict())
        .rename("curve")
        .reset_index()
    )

    # 3. Final index and structure (your original code)
    grouped = grouped.set_index(["time_index", "unique_identifier"])


    return _normalize_multiindex_time_index(grouped)


def _update_banxico_fixings(
    *,
    update_statistics,
    unique_identifier: str,
    id_map: Mapping[str, str],
    value_to_rate: Optional[Callable[[pd.Series], pd.Series]] = None,
) -> pd.DataFrame:
    """
    Generic Banxico SIE fixing updater.

    Parameters
    ----------
    update_statistics : msc.UpdateStatistics
        Object holding per-asset last ingested timestamps (UTC).
    unique_identifier : str
        One of the aliases in `id_map` (e.g., "TIIE_28D", "CETE_91D", etc.).
    id_map : Mapping[str, str]
        Alias -> SIE series id mapping for the instrument family.
    instrument_label : str
        Human-friendly label used for error messages ("TIIE", "CETE", ...).
    value_to_rate : callable(pd.Series) -> pd.Series, optional
        Transform from raw SIE 'value' (typically percent) to decimal rate.
        Defaults to dividing by 100.0.

    Returns
    -------
    pd.DataFrame
        MultiIndex DataFrame indexed by (time_index, unique_identifier)
        with a single 'rate' column (decimal). Empty if nothing to update.
    """
    # --- 0) Validate + token
    assert unique_identifier in id_map, f"Invalid unique identifier for {unique_identifier}"
    token = get_banxico_token()

    if value_to_rate is None:
        value_to_rate = lambda s: s / 100.0  # default: percent -> decimal

    # --- 1) Update window (global single start for all unique_identifiers)
    yday = datetime.datetime.now(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)

    # Start = last ingested day + 1 (UTC, floored to midnight). New fixing assets
    # may not exist in backend statistics yet, so use the historical Banxico
    # backfill bound on first run.
    asset_time_statistics = update_statistics.asset_time_statistics or {}
    last_update = asset_time_statistics.get(unique_identifier)
    if last_update is None:
        start_dt = datetime.datetime(2010, 1, 1, tzinfo=pytz.utc)
    else:
        start_dt = (
            (last_update + datetime.timedelta(days=1))
            .astimezone(pytz.utc)
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )
    if start_dt > yday:
        return pd.DataFrame()  # nothing to fetch

    start_date = start_dt.date().isoformat()
    end_date = yday.date().isoformat()

    # --- 2) Build SID universe + alias expansion (handles duplicate SIDs mapping to multiple aliases)
    banxico_alias=id_map[unique_identifier]
    aliases_by_sid = {banxico_alias: [unique_identifier]}

    # --- 3) Pull once + normalize long
    raw = fetch_banxico_series_batched([banxico_alias], start_date=start_date, end_date=end_date, token=token)
    long_df = to_long_with_aliases(raw, aliases_by_sid)  # columns: date(UTC), alias, value
    if long_df.empty:
        return pd.DataFrame()

    # --- 4) Build MultiIndex and scale to decimal
    long_df = long_df.rename(columns={"date": "time_index", "alias": "unique_identifier"})
    long_df["rate"] = value_to_rate(long_df["value"])

    out = (
        long_df[["time_index", "unique_identifier", "rate"]]
        .set_index(["time_index", "unique_identifier"])
        .sort_index()
    )
    return _normalize_multiindex_time_index(out)


# --- Thin wrappers keep your public API stable and clear ----------------------

def update_tiie_fixings(update_statistics, unique_identifier: str) -> pd.DataFrame:
    return _update_banxico_fixings(
        update_statistics=update_statistics,
        unique_identifier=unique_identifier,
        id_map=get_tiie_fixing_id_map(),
        value_to_rate=lambda s: s / 100.0,
    )


def update_cete_fixing(update_statistics, unique_identifier: str) -> pd.DataFrame:
    return _update_banxico_fixings(
        update_statistics=update_statistics,
        unique_identifier=unique_identifier,
        id_map=get_cete_fixing_id_map(),
        value_to_rate=lambda s: s / 100.0,
    )


def update_banxico_target_rate(update_statistics, unique_identifier: str) -> pd.DataFrame:
    return _update_banxico_fixings(
        update_statistics=update_statistics,
        unique_identifier=unique_identifier,
        id_map=get_banxico_target_rate_id_map(),
        value_to_rate=lambda s: s / 100.0,
    )

def build_banxico_mbonos_otr_zero_curve(update_statistics, curve_unique_identifier: str, base_node_curve_points=None):
    return boostrap_mbono_curve(
        update_statistics=update_statistics,
        curve_unique_identifier=curve_unique_identifier,
        base_node_curve_points=base_node_curve_points,
    )

build_banxico_mbonos_otr_curve = build_banxico_mbonos_otr_zero_curve
