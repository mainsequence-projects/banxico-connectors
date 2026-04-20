from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd


def ql_date(ql, value: pd.Timestamp):
    return ql.Date(int(value.day), int(value.month), int(value.year))


def quote_handle(ql, value: float):
    return ql.QuoteHandle(ql.SimpleQuote(float(value)))


@dataclass(frozen=True)
class BanxicoQuantLibInstrumentFactory:
    ql: object
    calendar: object
    day_count: object
    settlement_days: int = 0
    coupon_period_days: int = 182

    def build_cete(self, *, asof: pd.Timestamp, days_to_maturity: float):
        maturity = ql_date(
            self.ql,
            pd.Timestamp(asof).normalize() + pd.Timedelta(days=int(round(days_to_maturity))),
        )
        return self.ql.ZeroCouponBond(
            int(self.settlement_days),
            self.calendar,
            100.0,
            maturity,
            self.ql.Following,
            100.0,
        )

    def cete_helper(self, *, asof: pd.Timestamp, days_to_maturity: float, price: float):
        # CETES prices are quoted for a face value of 10. QuantLib clean prices
        # are quoted per 100 nominal.
        clean_price_per_100 = float(price) * 10.0
        return self.ql.BondHelper(
            quote_handle(self.ql, clean_price_per_100),
            self.build_cete(asof=asof, days_to_maturity=days_to_maturity),
        )

    def discount_factor_helper(
        self,
        *,
        asof: pd.Timestamp,
        days_to_maturity: float,
        discount_factor: float,
    ):
        clean_price_per_100 = 100.0 * float(discount_factor)
        return self.ql.BondHelper(
            quote_handle(self.ql, clean_price_per_100),
            self.build_cete(asof=asof, days_to_maturity=days_to_maturity),
        )

    def build_mbono(
        self,
        *,
        asof: pd.Timestamp,
        days_to_maturity: float,
        coupon_rate: float,
    ):
        asof = pd.Timestamp(asof).normalize()
        maturity_ts = asof + pd.Timedelta(days=int(round(days_to_maturity)))
        issue_ts = self._synthetic_issue_date(asof=asof, maturity=maturity_ts)
        schedule = self._coupon_schedule(issue=issue_ts, maturity=maturity_ts)

        return self.ql.FixedRateBond(
            int(self.settlement_days),
            100.0,
            schedule,
            [float(coupon_rate)],
            self.day_count,
            self.ql.Following,
            100.0,
        )

    def mbono_helper(
        self,
        *,
        asof: pd.Timestamp,
        days_to_maturity: float,
        coupon_rate: float,
        clean_price: float,
    ):
        return self.ql.BondHelper(
            quote_handle(self.ql, clean_price),
            self.build_mbono(
                asof=asof,
                days_to_maturity=days_to_maturity,
                coupon_rate=coupon_rate,
            ),
        )

    def _synthetic_issue_date(self, *, asof: pd.Timestamp, maturity: pd.Timestamp) -> pd.Timestamp:
        remaining_days = max(1, int((maturity - asof).days))
        periods_to_maturity = max(2, int(math.ceil(remaining_days / self.coupon_period_days)) + 1)
        issue = maturity - pd.Timedelta(days=periods_to_maturity * self.coupon_period_days)
        while issue >= asof:
            issue -= pd.Timedelta(days=self.coupon_period_days)
        return issue

    def _coupon_schedule(self, *, issue: pd.Timestamp, maturity: pd.Timestamp):
        dates = []
        current = pd.Timestamp(maturity).normalize()
        issue = pd.Timestamp(issue).normalize()

        while current > issue:
            dates.append(ql_date(self.ql, current))
            current -= pd.Timedelta(days=self.coupon_period_days)
        dates.append(ql_date(self.ql, issue))
        dates = sorted(set(dates))

        try:
            return self.ql.Schedule(dates, self.calendar, self.ql.Following)
        except TypeError:
            ql_dates = self.ql.DateVector()
            for date in dates:
                ql_dates.push_back(date)
            return self.ql.Schedule(ql_dates, self.calendar, self.ql.Following)
