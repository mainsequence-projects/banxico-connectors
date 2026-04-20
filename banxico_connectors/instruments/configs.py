from __future__ import annotations

from mainsequence.client import Constant as _C
from mainsequence.instruments.interest_rates.etl.nodes import FixingRateConfig, RateConfig


def build_banxico_fixing_rate_config() -> FixingRateConfig:
    """
    Build the canonical Banxico fixing config.

    The curve bootstrapper must read the same FixingRatesNode identity that the
    ETL runner updates. Keeping this config in one place avoids accidentally
    creating a target-rate-only node with a different hash and no data update.
    """
    return FixingRateConfig(
        rates=[
            RateConfig(
                rate_const="BANXICO_TARGET_RATE",
                name=f"Banxico target rate {_C.get_value(name='BANXICO_TARGET_RATE')}",
            ),
            RateConfig(
                rate_const="REFERENCE_RATE__TIIE_OVERNIGHT",
                name=f"Interbank Equilibrium Interest Rate (TIIE) {_C.get_value(name='REFERENCE_RATE__TIIE_OVERNIGHT')}",
            ),
            RateConfig(
                rate_const="REFERENCE_RATE__TIIE_28",
                name=f"Interbank Equilibrium Interest Rate (TIIE) {_C.get_value(name='REFERENCE_RATE__TIIE_28')}",
            ),
            RateConfig(
                rate_const="REFERENCE_RATE__TIIE_91",
                name=f"Interbank Equilibrium Interest Rate (TIIE) {_C.get_value(name='REFERENCE_RATE__TIIE_91')}",
            ),
            RateConfig(
                rate_const="REFERENCE_RATE__TIIE_182",
                name=f"Interbank Equilibrium Interest Rate (TIIE) {_C.get_value(name='REFERENCE_RATE__TIIE_182')}",
            ),
            RateConfig(
                rate_const="REFERENCE_RATE__CETE_28",
                name=f"CETE 28 days {_C.get_value(name='REFERENCE_RATE__CETE_28')}",
            ),
            RateConfig(
                rate_const="REFERENCE_RATE__CETE_91",
                name=f"CETE 91 days {_C.get_value(name='REFERENCE_RATE__CETE_91')}",
            ),
            RateConfig(
                rate_const="REFERENCE_RATE__CETE_182",
                name=f"CETE 182 days {_C.get_value(name='REFERENCE_RATE__CETE_182')}",
            ),
        ]
    )
