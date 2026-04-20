from __future__ import annotations

import datetime as dt
from typing import Any

import pandas as pd

from .quantlib_factories import BanxicoQuantLibInstrumentFactory, ql_date


NOMINAL_BOOTSTRAP_TYPES = {
    "overnight_rate",
    "zero_coupon",
    "fixed_bond",
}


def _require_quantlib():
    try:
        import QuantLib as ql  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "QuantLib is required for Banxico nominal curve bootstrapping. "
            "Install it with `uv add QuantLib`."
        ) from exc
    return ql


def _mx_calendar(ql):
    return ql.Mexico() if hasattr(ql, "Mexico") else ql.TARGET()


def _asof_timestamp(curve_df: pd.DataFrame) -> pd.Timestamp:
    if "time_index" in curve_df.columns:
        values = curve_df["time_index"]
    elif isinstance(curve_df.index, pd.MultiIndex) and "time_index" in curve_df.index.names:
        values = curve_df.index.get_level_values("time_index")
    else:
        raise ValueError("Curve input must include a time_index column or index level.")

    if len(values) == 0:
        raise ValueError("Curve input is empty.")

    asof = pd.to_datetime(values[0], utc=True, errors="coerce")
    if pd.isna(asof):
        raise ValueError("Curve input has an invalid time_index.")
    return pd.Timestamp(asof).normalize()


def _build_helper_from_row(
    *,
    row: pd.Series,
    asof: pd.Timestamp,
    factory: BanxicoQuantLibInstrumentFactory,
):
    inst_type = str(row["type"]).strip().lower()
    days_to_maturity = pd.to_numeric(row.get("tenor_days", row.get("days_to_maturity")), errors="coerce")
    if not pd.notna(days_to_maturity) or float(days_to_maturity) <= 0.0:
        return None

    if inst_type == "overnight_rate":
        rate = pd.to_numeric(row.get("dirty_price"), errors="coerce")
        if not pd.notna(rate):
            return None
        rate = float(rate)
        if rate > 1.0:
            rate /= 100.0
        discount_factor = 1.0 / (1.0 + rate / 360.0)
        return factory.discount_factor_helper(
            asof=asof,
            days_to_maturity=float(days_to_maturity),
            discount_factor=discount_factor,
        )

    if inst_type == "zero_coupon":
        price = pd.to_numeric(row.get("dirty_price"), errors="coerce")
        if not pd.notna(price):
            price = pd.to_numeric(row.get("clean_price"), errors="coerce")
        if not pd.notna(price) or float(price) <= 0.0:
            return None

        return factory.cete_helper(
            asof=asof,
            days_to_maturity=float(days_to_maturity),
            price=float(price),
        )

    if inst_type == "fixed_bond":
        clean_price = pd.to_numeric(row.get("clean_price"), errors="coerce")
        coupon = pd.to_numeric(row.get("coupon", row.get("current_coupon")), errors="coerce")
        if not pd.notna(clean_price) or not pd.notna(coupon):
            return None
        if float(clean_price) <= 0.0:
            return None

        return factory.mbono_helper(
            clean_price=float(clean_price),
            coupon_rate=float(coupon) / 100.0,
            asof=asof,
            days_to_maturity=float(days_to_maturity),
        )

    return None


def _curve_class(ql, interpolation: str):
    interpolation = (interpolation or "PiecewiseLogLinearDiscount").strip()
    if interpolation == "PiecewiseLogLinearDiscount":
        return ql.PiecewiseLogLinearDiscount
    if interpolation == "PiecewiseLogCubicDiscount":
        if not hasattr(ql, "PiecewiseLogCubicDiscount"):
            raise ImportError("QuantLib missing PiecewiseLogCubicDiscount.")
        return ql.PiecewiseLogCubicDiscount
    if interpolation == "PiecewiseFlatForward":
        if not hasattr(ql, "PiecewiseFlatForward"):
            raise ImportError("QuantLib missing PiecewiseFlatForward.")
        return ql.PiecewiseFlatForward
    raise ValueError(f"Unsupported interpolation: {interpolation}")


def bootstrap_from_curve_df(
    curve_df: pd.DataFrame,
    day_count_convention: float = 360.0,
    interpolation: str = "PiecewiseLogLinearDiscount",
) -> pd.DataFrame:
    """
    Bootstrap one nominal MXN zero curve from Banxico OTR rows using QuantLib.

    Input rows supported:
      - overnight_rate: stored Banxico target-rate fixing, decimal in dirty_price
      - zero_coupon: CETES price rows, price for face value 10
      - fixed_bond: MBONOS clean-price rows with coupon in percent

    Excluded by design:
      - BONDES floating-rate notes
      - UDIBONOS inflation-linked bonds

    Returns:
      DataFrame with columns ['days_to_maturity', 'zero_rate'], where zero_rate
      is a decimal simple annual zero rate on Actual/360.
    """
    if curve_df.empty:
        return pd.DataFrame(columns=["days_to_maturity", "zero_rate"])

    ql = _require_quantlib()
    asof = _asof_timestamp(curve_df)
    asof_date = ql_date(ql, asof)
    ql.Settings.instance().evaluationDate = asof_date

    calendar = _mx_calendar(ql)
    day_count: Any
    if float(day_count_convention) == 360.0:
        day_count = ql.Actual360()
    elif float(day_count_convention) == 365.0:
        day_count = ql.Actual365Fixed()
    else:
        day_count = ql.Actual360()

    factory = BanxicoQuantLibInstrumentFactory(
        ql=ql,
        calendar=calendar,
        day_count=day_count,
        settlement_days=0,
        coupon_period_days=182,
    )

    df = curve_df.copy()
    df["type"] = df["type"].astype(str).str.strip().str.lower()
    df = df[df["type"].isin(NOMINAL_BOOTSTRAP_TYPES)]
    if df.empty:
        return pd.DataFrame(columns=["days_to_maturity", "zero_rate"])

    helpers = []
    seen_pillar_days: set[int] = set()
    for _, row in df.sort_values("days_to_maturity").iterrows():
        helper = _build_helper_from_row(
            row=row,
            asof=asof,
            factory=factory,
        )
        if helper is None:
            continue
        pillar_days = int(helper.latestDate() - asof_date)
        if pillar_days <= 0 or pillar_days in seen_pillar_days:
            continue
        seen_pillar_days.add(pillar_days)
        helpers.append(helper)

    if not helpers:
        return pd.DataFrame(columns=["days_to_maturity", "zero_rate"])

    curve_cls = _curve_class(ql, interpolation)
    curve = curve_cls(asof_date, helpers, day_count)
    curve.enableExtrapolation()

    rows = []
    for helper in helpers:
        pillar_date = helper.latestDate()
        days = int(pillar_date - asof_date)
        if days <= 0:
            continue
        zero_rate = curve.zeroRate(pillar_date, day_count, ql.Simple, ql.Annual).rate()
        rows.append({"days_to_maturity": days, "zero_rate": float(zero_rate)})

    return (
        pd.DataFrame(rows)
        .drop_duplicates(subset=["days_to_maturity"], keep="last")
        .sort_values("days_to_maturity", kind="mergesort")
        .reset_index(drop=True)
    )
