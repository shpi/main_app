#!/usr/bin/env python3
"""Python replacement for ``keymap.c``.

The module can either be executed as a script or imported. When run as a
script it prints all available key codes for a given
``/dev/input/eventX`` device. The output format matches the original
C program: ``<keycode>:<name>`` per line.  When imported, the helper
function :func:`get_keycodes` returns the key map as a dictionary.
"""
import os
import sys
import re
import fcntl
import ctypes
from array import array

__all__ = ["get_keycodes"]

# ---------------------------------------------------------------------------
# Helpers for ioctl numbers (based on linux/ioctl.h)
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2


def _IOC(dir_, type_, nr, size):
    return (
        (dir_ << _IOC_DIRSHIFT)
        | (type_ << _IOC_TYPESHIFT)
        | (nr << _IOC_NRSHIFT)
        | (size << _IOC_SIZESHIFT)
    )


def _IOR(type_, nr, size):
    return _IOC(_IOC_READ, type_, nr, size)


def EVIOCGBIT(ev, length):
    return _IOC(_IOC_READ, ord("E"), 0x20 + ev, length)


# ---------------------------------------------------------------------------
# Structures used by ioctls
class InputKeymapEntryV2(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_uint8),
        ("len", ctypes.c_uint8),
        ("index", ctypes.c_uint16),
        ("keycode", ctypes.c_uint32),
        ("scancode", ctypes.c_uint8 * 32),
    ]


# ioctl constants
EVIOCGVERSION = _IOR(ord("E"), 0x01, ctypes.sizeof(ctypes.c_int))
EVIOCGKEYCODE = _IOR(ord("E"), 0x04, ctypes.sizeof(ctypes.c_int) * 2)
EVIOCGKEYCODE_V2 = _IOR(ord("E"), 0x04, ctypes.sizeof(InputKeymapEntryV2))
EV_KEY = 0x01
KEYMAP_BY_INDEX = 1


# ---------------------------------------------------------------------------
# Parse key names from linux-input.h
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_HEADER = os.path.join(THIS_DIR, "linux-input.h")

#KEY_PATTERN = re.compile(r"#define\s+(KEY_[A-Z0-9_]+)\s+(0x[0-9A-Fa-f]+|\d+)")
KEY_PATTERN = re.compile(r"#define\s+((?:KEY|BTN)_[A-Z0-9_]+)\s+(0x[0-9A-Fa-f]+|\d+)")



def parse_key_names():
    mapping = {}
    key_reserved = 0
    key_max = 0
    with open(INPUT_HEADER) as fh:
        for line in fh:
            m = KEY_PATTERN.match(line.strip())
            if not m:
                continue
            name, value = m.groups()
            val = int(value, 0)
            mapping[val] = name
            if name == "KEY_RESERVED":
                key_reserved = val
            if name == "KEY_MAX":
                key_max = val
    if not key_max:
        key_max = max(mapping)
    return mapping, key_reserved, key_max


# ---------------------------------------------------------------------------
# Main functionality

def kbd_print_bits(fd, key_names, key_max):
    """Return keycodes using ``EVIOCGBIT`` when ``EVIOCGKEYCODE`` is not
    supported."""
    length = (key_max + 7) // 8
    buf = array("B", [0] * length)
    try:
        fcntl.ioctl(fd, EVIOCGBIT(EV_KEY, length), buf, True)
    except OSError:
        return {}
    result = {}
    for bit in range(key_max + 1):
        if buf[bit // 8] & (1 << (bit % 8)):
            name = key_names.get(bit, f"KEY_{bit}")
            result[bit] = name
    return result


def kbd_map_read(fd, version, key_reserved):
    """Read keymap via ``EVIOCGKEYCODE``."""
    result = []
    for idx in range(65536):
        if version < 0x10001:
            entry = array("i", [idx, key_reserved])
            try:
                fcntl.ioctl(fd, EVIOCGKEYCODE, entry, True)
            except OSError:
                break
            scancode, keycode = entry
        else:
            ke = InputKeymapEntryV2()
            ke.index = idx
            ke.flags = KEYMAP_BY_INDEX
            ke.len = ctypes.sizeof(ctypes.c_uint32)
            try:
                fcntl.ioctl(fd, EVIOCGKEYCODE_V2, ke)
            except OSError:
                break
            scancode = int.from_bytes(bytes(ke.scancode[:4]), "little")
            keycode = ke.keycode
        result.append((scancode, keycode))
    return result


def read_keymap(fd, version, key_names, key_reserved, key_max):
    """Return a dictionary mapping keycodes to names."""
    mapping = kbd_map_read(fd, version, key_reserved)
    result = {}
    if mapping:
        for _scancode, keycode in mapping:
            if keycode != key_reserved:
                name = key_names.get(keycode, f"KEY_{keycode}")
                result[keycode] = name
    else:
        result = kbd_print_bits(fd, key_names, key_max)
    return result


# ---------------------------------------------------------------------------

def get_keycodes(event_number: int) -> dict[int, str]:
    """Return a mapping of keycodes to names for ``/dev/input/eventX``."""
    dev_path = f"/dev/input/event{event_number}"
    fd = os.open(dev_path, os.O_RDONLY)
    try:
        version_buf = array("i", [0])
        fcntl.ioctl(fd, EVIOCGVERSION, version_buf, True)
        version = version_buf[0]
        key_names, key_reserved, key_max = parse_key_names()
        return read_keymap(fd, version, key_names, key_reserved, key_max)
    finally:
        os.close(fd)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: keymap.py <event_number>", file=sys.stderr)
        return 1
    try:
        codes = get_keycodes(int(argv[1]))
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for keycode, name in sorted(codes.items()):
        print(f"{keycode}:{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
