from typing import Dict, Tuple, Optional, Union, List
from functools import cache

try:
    from mainsequence.client import Constant as _C, Secret as _S
except Exception as exc:
    _C = None
    _S = None
    _MS_CLIENT_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
else:
    _MS_CLIENT_IMPORT_ERROR = None


def _assert_mainsequence_client() -> None:
    if _C is None or _S is None:
        raise RuntimeError(
            "mainsequence client is not available. Set MAINSEQUENCE_ACCESS_TOKEN / MAINSEQUENCE_REFRESH_TOKEN and project context correctly."
        )







# -----------------------------
# Banxico series catalogs
# -----------------------------


BANXICO_SIE_BASE = "https://www.banxico.org.mx/SieAPIRest/service/v1"
CETES_SERIES: Dict[str, Dict[str, str]] = {
    # CETES (no coupon series in Banxico vector)

    "28d":  {"plazo": "SF45422", "precio_limpio": "SF45438", "precio_sucio": "SF45439"},
    "91d":  {"plazo": "SF45423", "precio_limpio": "SF45440", "precio_sucio": "SF45441"},
    "182d": {"plazo": "SF45424", "precio_limpio": "SF45442", "precio_sucio": "SF45443"},
    "364d": {"plazo": "SF45425", "precio_limpio": "SF45444", "precio_sucio": "SF45445"},
    # keep if you also track this bucket
    "2y":   {"plazo": "SF349886", "precio_limpio": "SF349887", "precio_sucio": "SF349888"},
}

BONOS_SERIES: Dict[str, Dict[str, str]] = {
    # BONOS M (Mbonos)
    "0-3y":   {"plazo": "SF45427", "precio_limpio": "SF45448", "precio_sucio": "SF45449", "cupon_vigente": "SF45475"},
    "3-5y":   {"plazo": "SF45428", "precio_limpio": "SF45450", "precio_sucio": "SF45451", "cupon_vigente": "SF45476"},
    "5-7y":   {"plazo": "SF45429", "precio_limpio": "SF45452", "precio_sucio": "SF45453", "cupon_vigente": "SF45477"},
    "7-10y":  {"plazo": "SF45430", "precio_limpio": "SF45454", "precio_sucio": "SF45455", "cupon_vigente": "SF45478"},
    "10-20y": {"plazo": "SF45431", "precio_limpio": "SF45456", "precio_sucio": "SF45457", "cupon_vigente": "SF45479"},
    "20-30y": {"plazo": "SF60720", "precio_limpio": "SF60721", "precio_sucio": "SF60722", "cupon_vigente": "SF60723"},
}

UDIBONOS_SERIES: Dict[str, Dict[str, str]] = {
    # UDIBONOS from Banxico CF300 vector. Prices are reported in pesos for UDI-linked bonds.
    "3y":  {"plazo": "SF61784", "precio_limpio": "SF61785", "precio_sucio": "SF61786", "cupon_vigente": "SF61787"},
    "10y": {"plazo": "SF45432", "precio_limpio": "SF45458", "precio_sucio": "SF45459", "cupon_vigente": "SF45480"},
    "20y": {"plazo": "SF50761", "precio_limpio": "SF50765", "precio_sucio": "SF50766", "cupon_vigente": "SF50763"},
    "30y": {"plazo": "SF50762", "precio_limpio": "SF50767", "precio_sucio": "SF50768", "cupon_vigente": "SF50764"},
}

BONDES_182_SERIES: Dict[str, Dict[str, str]] = {
    "182d": {
        "plazo": "SF45426",
        "precio_limpio": "SF45446",
        "precio_sucio": "SF45447",
        "cupon_vigente": "SF45474",
    }
}

BONDES_D_SERIES: Dict[str, Dict[str, str]] = {
    "1y": {"plazo": "SF59767",  "precio_limpio": "SF59773",  "precio_sucio": "SF59774",  "cupon_vigente": "SF59770"},
    "2y": {"plazo": "SF339752", "precio_limpio": "SF339753", "precio_sucio": "SF339754", "cupon_vigente": "SF339755"},
    "3y": {"plazo": "SF59768",  "precio_limpio": "SF59775",  "precio_sucio": "SF59776",  "cupon_vigente": "SF59771"},
    "5y": {"plazo": "SF59769",  "precio_limpio": "SF59777",  "precio_sucio": "SF59778",  "cupon_vigente": "SF59772"},
}

BONDES_F_SERIES: Dict[str, Dict[str, str]] = {
    "1y": {"plazo": "SF343403", "precio_limpio": "SF343391", "precio_sucio": "SF343395", "cupon_vigente": "SF343399"},
    "2y": {"plazo": "SF343404", "precio_limpio": "SF343392", "precio_sucio": "SF343396", "cupon_vigente": "SF343400"},
    "3y": {"plazo": "SF343405", "precio_limpio": "SF343393", "precio_sucio": "SF343397", "cupon_vigente": "SF343401"},
    "5y": {"plazo": "SF343406", "precio_limpio": "SF343394", "precio_sucio": "SF343398", "cupon_vigente": "SF343402"},
    "7y": {"plazo": "SF345944", "precio_limpio": "SF345941", "precio_sucio": "SF345942", "cupon_vigente": "SF345943"},
}

BONDES_G_SERIES: Dict[str, Dict[str, str]] = {
    "2y":  {"plazo": "SF347149", "precio_limpio": "SF347134", "precio_sucio": "SF347139", "cupon_vigente": "SF347144"},
    "4y":  {"plazo": "SF347150", "precio_limpio": "SF347135", "precio_sucio": "SF347140", "cupon_vigente": "SF347145"},
    "6y":  {"plazo": "SF347151", "precio_limpio": "SF347136", "precio_sucio": "SF347141", "cupon_vigente": "SF347146"},
    "8y":  {"plazo": "SF347152", "precio_limpio": "SF347137", "precio_sucio": "SF347142", "cupon_vigente": "SF347147"},
    "10y": {"plazo": "SF347153", "precio_limpio": "SF347138", "precio_sucio": "SF347143", "cupon_vigente": "SF347148"},
}

# (Optional) convenience registry if you like iterating by family name
BONDES_FAMILIES: Dict[str, Dict[str, Dict[str, str]]] = {
    "Bondes_182": BONDES_182_SERIES,
    "Bondes_D": BONDES_D_SERIES,
    "Bondes_F": BONDES_F_SERIES,
    "Bondes_G": BONDES_G_SERIES,
}

FUNDING_RATES={"1d":"SF331451"}

FONDEO_GUVBERNAMENTAL={"":"SF43774"}



BANXICO_TARGET_RATE="BANXICO_TARGET_RATE"
ON_THE_RUN_DATA_NODE_TABLE_NAME="banxico_1d_otr_mxn"
BANXICO_TOKEN_SECRET_NAME = "BANXICO_TOKEN"

MONEY_MARKET_RATES={BANXICO_TARGET_RATE:"SF61745",
                    }


def get_banxico_token() -> str:
    """
    Resolve the Banxico SIE API token from a Main Sequence Secret.

    The secret must be named BANXICO_TOKEN and shared with the authenticated
    project/session that runs the DataNode or fixing updater.
    """
    try:
        _assert_mainsequence_client()
        secret = _S.get(name=BANXICO_TOKEN_SECRET_NAME)
        value = secret.value
        if value is None:
            raise RuntimeError(f"Secret {BANXICO_TOKEN_SECRET_NAME!r} has no readable value.")
        token = value.get_secret_value() if hasattr(value, "get_secret_value") else str(value)
        if not token:
            raise RuntimeError(f"Secret {BANXICO_TOKEN_SECRET_NAME!r} is empty.")
        return token
    except Exception as e:
        raise RuntimeError(
            f"Main Sequence Secret {BANXICO_TOKEN_SECRET_NAME!r} is required for Banxico SIE access. "
            "Create it with `mainsequence secrets create BANXICO_TOKEN <token>` and ensure this project can view it."
        ) from e


@cache
def get_tiie_fixing_id_map() -> Dict[str, str]:
    """
    Resolve TIIE UID -> Banxico SIE series id mapping lazily.
    No Constant calls at import time.
    """
    try:
        _assert_mainsequence_client()
        return {
            _C.get_value(name="REFERENCE_RATE__TIIE_OVERNIGHT"): "SF331451",
            _C.get_value(name="REFERENCE_RATE__TIIE_28"): "SF43783",
            _C.get_value(name="REFERENCE_RATE__TIIE_91"): "SF43878",
            _C.get_value(name="REFERENCE_RATE__TIIE_182"): "SF111916",
        }
    except Exception as e:
        raise RuntimeError(
            "Missing Banxico constants for TIIE. "
            "Run instruments.scafold.seed_defaults() (or create the constants) before using Banxico fixings."
        ) from e


@cache
def get_cete_fixing_id_map() -> Dict[str, str]:
    """
    Resolve CETE UID -> Banxico SIE series id mapping lazily.
    No Constant calls at import time.
    """
    try:
        _assert_mainsequence_client()
        return {
            _C.get_value(name="REFERENCE_RATE__CETE_28"): "SF45470",
            _C.get_value(name="REFERENCE_RATE__CETE_91"): "SF45471",
            _C.get_value(name="REFERENCE_RATE__CETE_182"): "SF45472",
        }
    except Exception as e:
        raise RuntimeError(
            "Missing Banxico constants for CETE. "
            "Run instruments.scafold.seed_defaults() (or create the constants) before using Banxico fixings."
        ) from e


@cache
def get_banxico_target_rate_id_map() -> Dict[str, str]:
    """
    Resolve Banxico target-rate UID -> Banxico SIE series id mapping lazily.
    No Constant calls at import time.
    """
    try:
        _assert_mainsequence_client()
        return {
            _C.get_value(name=BANXICO_TARGET_RATE): MONEY_MARKET_RATES[BANXICO_TARGET_RATE],
        }
    except Exception as e:
        raise RuntimeError(
            "Missing Banxico target-rate constant. "
            "Run instruments.scafold.seed_defaults() (or create the constant) before using Banxico fixings."
        ) from e
