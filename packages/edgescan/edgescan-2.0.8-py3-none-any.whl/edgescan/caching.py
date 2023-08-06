import distutils.util
import os


def is_enabled() -> bool:
    v = os.getenv('EDGESCAN_ENABLE_CACHE', True)
    if v is None:
        return False

    if isinstance(v, str):
        v = bool(distutils.util.strtobool(v))
    return v


def is_disabled() -> bool:
    return is_enabled() is False
