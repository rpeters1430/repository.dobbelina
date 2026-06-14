import importlib
import os

from kodi_six import xbmc

# Sites intentionally excluded from Kodi runtime listing.
EXCLUDED_SITE_MODULES = {"luxuretv.py", "missav.py", "pornxpert.py", "stripchat.py"}

_pkg = __name__
_dir = os.path.dirname(__file__)

__all__ = []

for _filename in sorted(os.listdir(_dir)):
    if (
        _filename.startswith("__")
        or not _filename.endswith(".py")
        or _filename in EXCLUDED_SITE_MODULES
    ):
        continue
    _module_name = _filename[:-3]
    try:
        importlib.import_module("{0}.{1}".format(_pkg, _module_name))
    except Exception as e:
        xbmc.log(
            "Cumination: incompatible site module ({0}): {1}".format(_module_name, e),
            xbmc.LOGERROR,
        )
    else:
        __all__.append(_module_name)
