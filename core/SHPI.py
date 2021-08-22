from logging import getLogger
logger = getLogger('SHPI')


def _iio() -> bool:
    from ctypes import CDLL
    from ctypes.util import find_library

    lib = CDLL(find_library('iio'), use_errno=True, use_last_error=True)
    if not lib._name:
        logger.error('Check iio: Missing library libiio.')
        return False

    return True


_checks = _iio,


def check() -> bool:
    ok = True

    for c in _checks:
        ok = ok and c()

    return ok
