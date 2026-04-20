from __future__ import annotations

import datetime as dt
import math
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import pytz
import mainsequence.client as msc
from pydantic import Field

from mainsequence.tdag import DataNode, DataNodeConfiguration, DataNodeMetaData, RecordDefinition
from mainsequence.client.models_tdag import UpdateStatistics

from banxico_connectors.settings import (
    CETES_SERIES,
    BONOS_SERIES,
    UDIBONOS_SERIES,
    BONDES_D_SERIES,
    BONDES_F_SERIES,
    BONDES_G_SERIES,
    ON_THE_RUN_DATA_NODE_TABLE_NAME,
    get_banxico_token,
)
from banxico_connectors.utils import fetch_banxico_series_batched, to_long

UTC = pytz.utc



# -----------------------------
# HTTP helpers
# -----------------------------


class BanxicoMXNOTRConfig(DataNodeConfiguration):
    offset_start: dt.datetime = Field(
        default=dt.datetime(2010, 1, 1, tzinfo=UTC),
        description="First-run fallback start date for Banxico OTR backfills.",
        json_schema_extra={"update_only": True},
    )
    records: list[RecordDefinition] = Field(
        default_factory=lambda: [
            RecordDefinition(
                column_name="days_to_maturity",
                dtype="float64",
                label="Days to Maturity",
                description="Number of days until maturity (Banxico vector).",
            ),
            RecordDefinition(
                column_name="clean_price",
                dtype="float64",
                label="Clean Price",
                description="Price excluding accrued interest.",
            ),
            RecordDefinition(
                column_name="dirty_price",
                dtype="float64",
                label="Dirty Price",
                description="Dirty price for quoted securities.",
            ),
            RecordDefinition(
                column_name="current_coupon",
                dtype="float64",
                label="Current Coupon",
                description="Coupon or spread-like input reported by Banxico, depending on type.",
            ),
            RecordDefinition(
                column_name="yield_rate",
                dtype="float64",
                label="Yield Rate",
                description=(
                    "Derived annual yield as a decimal rate when it can be calculated from "
                    "the quoted price and maturity."
                ),
            ),
            RecordDefinition(
                column_name="yield_source",
                dtype="string",
                label="Yield Source",
                description="Method used to derive yield_rate, or not_available when unavailable.",
            ),
            RecordDefinition(
                column_name="type",
                dtype="string",
                label="Instrument Type",
                description="Normalized instrument role used by the curve bootstrapper.",
            ),
            RecordDefinition(
                column_name="instrument_family",
                dtype="string",
                label="Instrument Family",
                description="Normalized Banxico family name for the row.",
            ),
            RecordDefinition(
                column_name="quote_type",
                dtype="string",
                label="Quote Type",
                description="Whether dirty_price should be interpreted as a price or a rate.",
            ),
            RecordDefinition(
                column_name="coupon_type",
                dtype="string",
                label="Coupon Type",
                description="Whether current_coupon is unused, a coupon, or a spread-like input.",
            ),
        ]
    )
    node_metadata: DataNodeMetaData = Field(
        default_factory=lambda: DataNodeMetaData(
            identifier=ON_THE_RUN_DATA_NODE_TABLE_NAME,
            data_frequency_id=msc.DataFrequency.one_d,
            description=(
                "On-the-run CETES, BONOS, UDIBONOS, and BONDES D/F/G quotes from Banxico SIE. "
                "The dataset stores security price observations with normalized type, family, "
                "quote_type, coupon_type, yield_rate, and yield_source fields for plotting and "
                "downstream curve construction."
            ),
        ),
        json_schema_extra={"runtime_only": True},
    )


class BanxicoMXNOTR(DataNode):
    """
    Pull Banxico SIE observations for on-the-run Mexican rates instruments.

    Output:
        MultiIndex: (time_index [UTC], unique_identifier)
        Columns:
            days_to_maturity, clean_price, dirty_price, current_coupon,
            yield_rate, yield_source, type, instrument_family, quote_type, coupon_type
    """

    CETES_TENORS: Tuple[str, ...] = tuple(CETES_SERIES.keys())
    BONOS_TENORS: Tuple[str, ...] = tuple(BONOS_SERIES.keys())
    UDIBONOS_TENORS: Tuple[str, ...] = tuple(UDIBONOS_SERIES.keys())

    # BONDES_182_TENORS: Tuple[str, ...] = tuple(BONDES_182_SERIES.keys())  # ("182d",)
    BONDES_D_TENORS: Tuple[str, ...] = tuple(BONDES_D_SERIES.keys())  # ("1y","2y","3y","5y")
    BONDES_F_TENORS: Tuple[str, ...] = tuple(BONDES_F_SERIES.keys())  # ("1y","2y","3y","5y","7y")
    BONDES_G_TENORS: Tuple[str, ...] = tuple(BONDES_G_SERIES.keys())  # ("2y","4y","6y","8y","10y")

    SPANISH_TO_EN = {
        "plazo": "days_to_maturity",
        "precio_limpio": "clean_price",
        "precio_sucio": "dirty_price",
        "cupon_vigente": "current_coupon",
    }
    TARGET_COLS = ("days_to_maturity", "clean_price", "dirty_price", "current_coupon")
    COUPON_TYPE_BY_SEC_TYPE = {
        "zero_coupon": "none",
        "fixed_bond": "coupon",
        "inflation_linked_bond": "coupon",
        "floating_bondes_d": "spread_like_rate",
        "floating_bondes_f": "spread_like_rate",
        "floating_bondes_g": "spread_like_rate",
    }


    def __init__(
        self,
        config: BanxicoMXNOTRConfig,
        *,
        hash_namespace: str | None = None,
        test_node: bool = False,
    ):
        self.offset_start = config.offset_start
        super().__init__(
            config=config,
            hash_namespace=hash_namespace,
            test_node=test_node,
        )

    @staticmethod
    def _assert_no_future_time_index(df: pd.DataFrame, max_allowed: dt.datetime) -> None:
        if df.empty:
            return
        time_index = pd.to_datetime(
            df.index.get_level_values("time_index"),
            utc=True,
            errors="coerce",
        )
        future_rows = time_index[time_index > pd.Timestamp(max_allowed)]
        if future_rows.empty:
            return
        sample_dates = ", ".join(
            pd.Series(future_rows.unique()).sort_values().dt.strftime("%Y-%m-%d").head(5).tolist()
        )
        raise ValueError(
            "BanxicoMXNOTR produced future-dated observations beyond the requested update window. "
            f"Max allowed date: {max_allowed.date().isoformat()}. "
            f"Sample future dates: {sample_dates}. "
            "This usually means Banxico DD/MM/YYYY dates were parsed incorrectly or the source payload format changed."
        )

    @staticmethod
    def _normalize_multiindex_time_index(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        if not isinstance(df.index, pd.MultiIndex) or "time_index" not in df.index.names:
            raise ValueError("BanxicoMXNOTR output must be indexed by time_index and unique_identifier.")

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

    @staticmethod
    def _cetes_money_market_yield(dirty_price: float, days_to_maturity: float) -> float | None:
        if pd.isna(dirty_price) or pd.isna(days_to_maturity):
            return None
        price = float(dirty_price)
        days = float(days_to_maturity)
        if price <= 0.0 or days <= 0.0:
            return None
        return (10.0 / price - 1.0) * (360.0 / days)

    @staticmethod
    def _fixed_bond_yield_from_dirty_price(
        dirty_price: float,
        days_to_maturity: float,
        current_coupon: float,
    ) -> float | None:
        if pd.isna(dirty_price) or pd.isna(days_to_maturity) or pd.isna(current_coupon):
            return None

        price = float(dirty_price)
        days = float(days_to_maturity)
        coupon_rate = float(current_coupon) / 100.0
        if price <= 0.0 or days <= 0.0 or coupon_rate < 0.0:
            return None

        face = 100.0
        coupon_step_days = 182.0
        payment_count = max(1, int(math.ceil(days / coupon_step_days)))
        payment_days = [min(coupon_step_days * i, days) for i in range(1, payment_count + 1)]

        cashflows: list[tuple[float, float]] = []
        previous_day = 0.0
        for payment_day in payment_days:
            accrual_days = max(payment_day - previous_day, 0.0)
            amount = face * coupon_rate * accrual_days / 360.0
            if math.isclose(payment_day, days):
                amount += face
            cashflows.append((payment_day, amount))
            previous_day = payment_day

        def present_value(yield_rate: float) -> float:
            base = 1.0 + yield_rate / 2.0
            if base <= 0.0:
                return float("inf")
            return sum(
                amount / (base ** (2.0 * payment_day / 360.0))
                for payment_day, amount in cashflows
            )

        low = -0.95
        high = 2.0
        low_diff = present_value(low) - price
        high_diff = present_value(high) - price
        if low_diff * high_diff > 0:
            return None

        for _ in range(80):
            mid = (low + high) / 2.0
            mid_diff = present_value(mid) - price
            if abs(mid_diff) < 1e-12:
                return mid
            if low_diff * mid_diff <= 0:
                high = mid
                high_diff = mid_diff
            else:
                low = mid
                low_diff = mid_diff
        return (low + high) / 2.0

    @classmethod
    def _derive_yield(cls, row: pd.Series) -> tuple[float | None, str]:
        family = str(row.get("instrument_family", "")).lower()
        instrument_type = str(row.get("type", "")).lower()

        if family == "cetes" or instrument_type == "zero_coupon":
            rate = cls._cetes_money_market_yield(
                row.get("dirty_price"),
                row.get("days_to_maturity"),
            )
            if rate is not None:
                return rate, "cetes_money_market"

        if family == "bonos" or instrument_type == "fixed_bond":
            rate = cls._fixed_bond_yield_from_dirty_price(
                row.get("dirty_price"),
                row.get("days_to_maturity"),
                row.get("current_coupon"),
            )
            if rate is not None:
                return rate, "dirty_price_fixed_bond_ytm"

        return None, "not_available"

    def dependencies(self) -> Dict[str, Union["DataNode", "APIDataNode"]]:
        return {}


    def get_asset_list(self) -> List[msc.Asset]:
        cetes_tickers = [f"MCET_{t}_OTR" for t in self.CETES_TENORS]
        bonos_tickers = [f"MBONO_{t}_OTR" for t in self.BONOS_TENORS]
        udibonos_tickers = [f"UDIBONO_{t}_OTR" for t in self.UDIBONOS_TENORS]

        bondes_d_tickers = [f"BONDES_D_{t}_OTR" for t in self.BONDES_D_TENORS]
        bondes_f_tickers = [f"BONDES_F_{t}_OTR" for t in self.BONDES_F_TENORS]
        bondes_g_tickers = [f"BONDES_G_{t}_OTR" for t in self.BONDES_G_TENORS]

        wanted = (
                cetes_tickers
                + bonos_tickers
                + udibonos_tickers
                +  bondes_d_tickers + bondes_f_tickers + bondes_g_tickers
        )

        assets_payload=[]
        for identifier in wanted:
            snapshot = {
                "name": identifier,
                "ticker": identifier,
                "exchange_code": "MEXICO",
            }
            payload_item = {
                "unique_identifier": identifier,
                "snapshot": snapshot,
                "security_market_sector" : msc.MARKETS_CONSTANTS.FIGI_MARKET_SECTOR_GOVT,
            "security_type" : msc.MARKETS_CONSTANTS.FIGI_SECURITY_TYPE_DOMESTIC,
            "security_type_2" : msc.MARKETS_CONSTANTS.FIGI_SECURITY_TYPE_2_GOVT,
            }
            assets_payload.append(payload_item)


        try:
            assets = msc.Asset.batch_get_or_register_custom_assets(assets_payload)

        except Exception as e:
            self.logger.error(f"Failed to process asset batch: {e}")
            raise




        return assets

    def update(self) -> pd.DataFrame:
        us: UpdateStatistics = self.update_statistics

        # --- 0) Token from platform Secret (kept out of config/hash identity)
        token = get_banxico_token()

        # --- 1) Compute update window (yesterday 00:00 UTC end). Start = min(last+1d)
        yday = dt.datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=1)
        effective_assets = us.asset_list or self.get_asset_list() or []
        effective_assets = [
            asset
            for asset in effective_assets
            if (
                (getattr(asset, "ticker", None) or getattr(asset, "unique_identifier", "") or "")
                .startswith(("MCET_", "MBONO_", "UDIBONO_", "BONDES_D_", "BONDES_F_", "BONDES_G_"))
            )
        ]
        if not effective_assets:
            return pd.DataFrame()

        asset_time_statistics = us.asset_time_statistics or {}
        starts: List[dt.datetime] = []
        for asset in effective_assets:
            last = us.get_asset_earliest_multiindex_update(asset=asset)
            if asset_time_statistics.get(asset.unique_identifier) and last is not None:
                starts.append((last + dt.timedelta(days=1)).astimezone(UTC).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ))
            else:
                starts.append(self.offset_start)
        start_dt = min(starts) if starts else self.offset_start
        if start_dt > yday:
            return pd.DataFrame()

        start_date = start_dt.date().isoformat()
        end_date = yday.date().isoformat()

        # --- 2) Build the series universe: CETES + BONOS (map to EN metric names)
        metric_by_sid: Dict[str, str] = {}

        def add_family(series_map: Dict[str, Dict[str, str]]):
            for _tenor, m in series_map.items():
                for sk, sid in m.items():
                    en = self.SPANISH_TO_EN.get(sk)
                    if en and sid:
                        metric_by_sid[sid] = en

        add_family(CETES_SERIES)
        add_family(BONOS_SERIES)
        add_family(BONDES_D_SERIES)
        add_family(BONDES_F_SERIES)
        add_family(BONDES_G_SERIES)

        all_sids = list(metric_by_sid.keys())
        if not all_sids:
            return pd.DataFrame()

        # --- 3) Pull once from Banxico + normalize (metric column already in EN via metric_by_sid)
        raw = fetch_banxico_series_batched(all_sids, start_date=start_date, end_date=end_date, token=token)
        long_df = to_long(raw, metric_by_sid)  # produces columns: date, series_id, metric(EN), value
        if long_df.empty:
            return pd.DataFrame()

        # --- 4) Prepare pivoted frames per (family, tenor), columns in EN
        frames: Dict[tuple, pd.DataFrame] = {}

        def pivot_family(family_name: str, series_map: Dict[str, Dict[str, str]]):
            for tenor, mapping in series_map.items():
                sids = set(mapping.values())
                sub = long_df[long_df["series_id"].isin(sids)]
                if sub.empty:
                    continue
                wide = (
                    sub.pivot_table(index="date", columns="metric", values="value", aggfunc="last")
                    .rename_axis(None, axis="columns")
                )
                for col in self.TARGET_COLS:
                    if col not in wide.columns:
                        wide[col] = np.nan
                wide.index = pd.to_datetime(wide.index, utc=True)
                wide.index.name = "time_index"
                frames[(family_name, f"{tenor}_OTR")] = wide[list(self.TARGET_COLS)]
        # CETES / BONOS
        pivot_family("Cetes", CETES_SERIES)
        pivot_family("Bonos", BONOS_SERIES)
        pivot_family("Udibonos", UDIBONOS_SERIES)

        # NEW: BONDES (182 / D / F / G)
        pivot_family("Bondes_D", BONDES_D_SERIES)
        pivot_family("Bondes_F", BONDES_F_SERIES)
        pivot_family("Bondes_G", BONDES_G_SERIES)

        if not frames:
            return pd.DataFrame()

        # --- 5) Attach each asset to its (family, tenor) frame
        out_parts: List[pd.DataFrame] = []
        assets = effective_assets
        for a in assets:
            tkr = (a.ticker or "")

            if tkr.startswith("MCET_"):
                family, tenor = "Cetes", tkr.split("MCET_", 1)[1]
                sec_type = "zero_coupon"

            elif tkr.startswith("MBONO_"):
                family, tenor = "Bonos", tkr.split("MBONO_", 1)[1]
                sec_type = "fixed_bond"

            elif tkr.startswith("UDIBONO_"):
                family, tenor = "Udibonos", tkr.split("UDIBONO_", 1)[1]
                sec_type = "inflation_linked_bond"

            #  Bondes families

            elif tkr.startswith("BONDES_D_"):
                family, tenor = "Bondes_D", tkr.split("BONDES_D_", 1)[1]
                sec_type = "floating_bondes_d"

            elif tkr.startswith("BONDES_F_"):
                family, tenor = "Bondes_F", tkr.split("BONDES_F_", 1)[1]
                sec_type = "floating_bondes_f"

            elif tkr.startswith("BONDES_G_"):
                family, tenor = "Bondes_G", tkr.split("BONDES_G_", 1)[1]
                sec_type = "floating_bondes_g"

            else:
                continue

            key = (family, tenor)
            if key not in frames:
                continue

            df = frames[key].copy()
            uid = getattr(a, "unique_identifier", None) or tkr
            df["unique_identifier"] = uid
            df["type"] = sec_type
            df["instrument_family"] = family.lower()
            df["quote_type"] = "price"
            df["coupon_type"] = self.COUPON_TYPE_BY_SEC_TYPE[sec_type]
            out_parts.append(df.set_index("unique_identifier", append=True))

        if not out_parts:
            return pd.DataFrame()

        out = pd.concat(out_parts).sort_index()

        out=out[out.days_to_maturity>0] #some banxico series have errors
        if out.empty:
            return pd.DataFrame()
        yield_data = out.apply(self._derive_yield, axis=1, result_type="expand")
        out["yield_rate"] = pd.to_numeric(yield_data[0], errors="coerce")
        out["yield_source"] = yield_data[1].astype("string")
        out = self._normalize_multiindex_time_index(out)
        self._assert_no_future_time_index(out, yday)

        return out
