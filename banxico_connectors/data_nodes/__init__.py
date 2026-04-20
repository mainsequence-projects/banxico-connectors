from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from .banxico_mx_otr import BanxicoMXNOTR, BanxicoMXNOTRConfig

__all__ = ["BanxicoMXNOTR", "BanxicoMXNOTRConfig"]
