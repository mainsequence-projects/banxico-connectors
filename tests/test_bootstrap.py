from __future__ import annotations

import unittest

import pandas as pd

from banxico_connectors.instruments.bootstrap import bootstrap_from_curve_df


class BootstrapZeroRateUnitsTest(unittest.TestCase):
    def test_bootstrap_returns_decimal_zero_rates(self) -> None:
        curve_df = pd.DataFrame(
            [
                {
                    "type": "overnight_rate",
                    "tenor_days": 1,
                    "clean_price": None,
                    "dirty_price": 0.10,
                    "coupon": None,
                },
                {
                    "type": "zero_coupon",
                    "tenor_days": 28,
                    "clean_price": 9.30,
                    "dirty_price": 9.30,
                    "coupon": 0.0,
                },
            ]
        )

        out = bootstrap_from_curve_df(curve_df)

        one_day_zero = out.loc[out["days_to_maturity"] == 1, "zero_rate"].iloc[0]

        self.assertAlmostEqual(one_day_zero, 0.10, places=10)
        self.assertLess(one_day_zero, 1.0)


if __name__ == "__main__":
    unittest.main()
