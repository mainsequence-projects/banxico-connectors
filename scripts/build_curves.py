# scripts/build_curves.py
from __future__ import annotations

from mainsequence.client import Constant as _C

# 1) Seed Banxico-owned constants FIRST (before any module that might call _C.get_value at import time)
from banxico_connectors.instruments.scafold import seed_defaults
seed_defaults()

# 2) Import registries explicitly (this is what you said was missing)
from mainsequence.instruments.interest_rates.etl.registry import (
    DISCOUNT_CURVE_BUILDERS,
    FIXING_RATE_BUILDERS,
)

# 3) Ensure builders are registered (NO side-effects at import time)
#    This also wires the new pricing_models.indices IndexSpec registry.
from banxico_connectors.instruments.registry import register_all

register_all()

# 4) Now import ETL nodes/configs (they rely on the registries above)
from mainsequence.instruments.interest_rates.etl.nodes import CurveConfig, DiscountCurvesNode, FixingRatesNode

from banxico_connectors.data_nodes.banxico_mx_otr import BanxicoMXNOTR, BanxicoMXNOTRConfig
from banxico_connectors.instruments.configs import build_banxico_fixing_rate_config
from banxico_connectors.settings import ON_THE_RUN_DATA_NODE_TABLE_NAME


_REQUIRED_CURVE_CONSTS = (
    "ZERO_CURVE__BANXICO_M_BONOS_OTR",
)

_REQUIRED_FIXING_CONSTS = (
    "BANXICO_TARGET_RATE",
    "REFERENCE_RATE__TIIE_OVERNIGHT",
    "REFERENCE_RATE__TIIE_28",
    "REFERENCE_RATE__TIIE_91",
    "REFERENCE_RATE__TIIE_182",
    "REFERENCE_RATE__CETE_28",
    "REFERENCE_RATE__CETE_91",
    "REFERENCE_RATE__CETE_182",
)


def _assert_registry_wired() -> None:
    missing: list[str] = []

    for c in _REQUIRED_CURVE_CONSTS:
        if c not in DISCOUNT_CURVE_BUILDERS.all_const_names():
            missing.append(f"DISCOUNT_CURVE_BUILDERS missing: {c}")

    for c in _REQUIRED_FIXING_CONSTS:
        if c not in FIXING_RATE_BUILDERS.all_const_names():
            missing.append(f"FIXING_RATE_BUILDERS missing: {c}")

    if missing:
        raise RuntimeError(
            "Builder registry is NOT wired (banxico_connectors.instruments.registry didn't register what this runner needs):\n"
            + "\n".join(f" - {m}" for m in missing)
        )


def main() -> None:
    _assert_registry_wired()

    # ---- Refresh Banxico OTR points ----
    BanxicoMXNOTR(config=BanxicoMXNOTRConfig()).run(force_update=True)

    # ---- Fixings ----
    FixingRatesNode(rates_config=build_banxico_fixing_rate_config()).run(force_update=True)

    # ---- Discount curve ----
    curve_cfg = CurveConfig(
        curve_const="ZERO_CURVE__BANXICO_M_BONOS_OTR",
        name="Discount Curve M Bonos Banxico Bootstrapped",
    )
    DiscountCurvesNode(curve_config=curve_cfg).run(force_update=True)


if __name__ == "__main__":
    main()
