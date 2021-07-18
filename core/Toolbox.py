# -*- coding: utf-8 -*-

import socket
import logging
import ctypes
from re import compile
from typing import NamedTuple, Optional, Union
from threading import Thread
import os

from PySide2.QtCore import QTimer


SIOCGIFNETMASK = 0x891b
SIOCGIFHWADDR = 0x8927
SIOCGIFADDR = 0x8915


class IPEndpoint(NamedTuple):
    ip: str
    hostname: str
    mac: Optional[str] = None
    oui: Optional[str] = None
    iface: Optional[str] = None

    def __repr__(self):
        return f"{self.ip}: {self.hostname} [{self.mac}, {self.oui}]"


def lookup_oui(mac: Union[bytes, str]) -> str:
    file_path = "/usr/share/nmap/nmap-mac-prefixes"

    if type(mac) is bytes:
        mac = "".join(['%02X' % byte for byte in mac])
    elif type(mac) is str:
        mac = mac.replace(":", "")
    else:
        raise ValueError("mac must be bytes or string")

    mac = mac[:6].upper()

    # 887E25 Extreme Networks
    matcher = compile(f"^{mac} (.*)$")
    # Caching in a dict: +5MB RAM

    with open(file_path, encoding="utf8") as file:
        for line in file:
            m = matcher.match(line)
            if m:
                return m.group(1)
        else:
            return "-Unknown Vendor-"


def ipbytes_to_ipstr(ip: bytes) -> str:
    return socket.inet_ntoa(ip)


def netmaskbytes_to_prefixlen(netmask: bytes) -> int:
    bits = 0
    valid_maskbytes = {255 << 8 - bits & 255: bits for bits in range(9)}

    for b in netmask:
        if b not in valid_maskbytes:
            raise ValueError("Invalid subnet mask")

        if not b:
            break

        bits += valid_maskbytes[b]

    return bits


class RepeatingTimer:
    def __init__(self, timeout, func, autostart=True, *args, **kwargs):
        """
        Create a timer that is safe against garbage collection and overlapping
        calls.
        """

        self.timeout = timeout
        self.started = False

        t = self.timer = QTimer()

        def _repeatingtimer_event():
            try:
                func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in RepeatingTimer: {e!s}", exc_info=True)

        t.timeout.connect(_repeatingtimer_event)

        if autostart:
            self.start()

    def start(self):
        if self.started:
            logging.info("RepeatingTimer already started!")
            return
        self.timer.start(self.timeout)
        self.started = True

    def stop(self):
        if not self.started:
            logging.info("RepeatingTimer already stopped!")
            return
        self.timer.stop()
        self.started = False

    def __del__(self):
        if self.started:
            self.stop()
        del self.timer


def thread_kill(thread: Thread, join_timeout: int = None) -> bool:
    if not thread.is_alive():
        logging.warning('Thread has already stopped.')
        return False

    thread_id = ctypes.c_long(thread.ident)
    exc = ctypes.py_object(SystemExit)

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, exc)
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        logging.error('Thread Exception raise failure.')

    join_timeout = float(join_timeout) if join_timeout else None

    if res == 1 and join_timeout:
        thread.join(join_timeout)
        return not thread.is_alive()

    return res == 1


class Pipe:
    def __init__(self):
        self.read_fd, self.write_fd = os.pipe()

    def write(self, data: bytes):
        os.write(self.write_fd, data)

    def read(self, size=0):
        os.read(self.read_fd, size)

    def __del__(self):
        os.close(self.read_fd)
        os.close(self.write_fd)

    def __repr__(self):
        return f"<{self.__class__.__name__} read={self.read_fd} write={self.write_fd}>"
