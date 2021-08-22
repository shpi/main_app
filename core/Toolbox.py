# -*- coding: utf-8 -*-

import socket
import logging
import ctypes
import os
import numpy

from re import compile
from typing import NamedTuple, Optional, Union, List, Any, Callable, Set
from threading import Thread
from logging import Logger

from PySide2.QtCore import QTimer, QAbstractListModel, QModelIndex, Qt, QObject


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


class KwReplace:
    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        out = self.template
        for key, value in kwargs.items():
            out = out.replace('{' + key + '}', value)

        return out


class MeanWindow:
    def __init__(self, first: float = None, window_size=10, func=None, dtype=numpy.int16):
        self._window_size = window_size
        self._data: Optional[numpy.ndarray] = None
        self._dtype = dtype
        self._circular_index = 0
        self._func = func
        if first is not None:
            self.update(first)

    @property
    def mean(self) -> Optional[float]:
        if self._data is None:
            return None
        return self._data.mean()

    def update(self, value: float = None):
        if value is None:
            value = self._func()

        if self._data is None:
            # First element. Fill to force average.
            self._data = numpy.full(self._window_size, value, dtype=self._dtype)
            return

        # Write to pointer pos
        self._data[self._circular_index] = value

        # Move pointer
        self._circular_index = (self._circular_index + 1) % self._window_size


class AutoEnum:
    """
    Enumerates integer values on classes.
    class Test:
        auto = AutoEnum(512)
        item1 = auto()  # gets 512
        item2 = auto()  # gets 513

    """
    def __init__(self, start=0):
        self._next = int(start)

    def __call__(self, *args, **kwargs):
        ret = self._next
        self._next += 1
        return ret


class StandardListModel(QAbstractListModel):
    rolenames = {}

    dataroles_read_funcs = {}
    dataroles_write_funcs = {}

    item_flags = Qt.ItemIsSelectable | Qt.ItemNeverHasChildren
    logger = logging.getLogger('StandardListModel')

    _invalid_index = QModelIndex()

    def __init__(self, parent: QObject, data: Optional[List[Any]]):
        QAbstractListModel.__init__(self, parent=parent)
        if data is None:
            self._external_data = False
            self._data = []
        else:
            self._external_data = True
            self._data = data

    def index_valid(self, index: QModelIndex) -> bool:
        return index.isValid() and 0 <= index.row() < len(self._data)

    def reload(self):
        self.beginResetModel()
        self.endResetModel()

    def _item_from_index(self, index: QModelIndex) -> Optional[Any]:
        if not self.index_valid(index):
            return

        row = index.row()
        if row + 1 > len(self._data):
            return None

        return self._data[row]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        item = self._item_from_index(index)

        if item is None:
            return None

        func = self.dataroles_read_funcs.get(role)
        if not func:
            return None

        try:
            return func(item)
        except Exception as e:
            self.logger.error('Exception on fetching data (role=%s) in %s: %s', role, type(self), repr(e))
            return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        prop = self._item_from_index(index)

        if prop is None:
            return Qt.NoItemFlags

        return self.item_flags

    def setData(self, index: QModelIndex, value, role: int = Qt.DisplayRole) -> bool:
        func = self.dataroles_write_funcs.get(role)
        if not func:
            return False

        item = self._item_from_index(index)
        if item is None:
            return False

        try:
            res = func(item, value)
        except Exception as e:
            self.logger.error('Exception on setting data in %s: %s', type(self), repr(e))
            return False

        if res:
            self.dataChanged.emit(index, index, (role,))
        return res

    def data_changed(self, item: Any, roles=()):
        """
        Called from internal operations to annouce changes to the model
        """
        try:
            changed_pos = self._data.index(item)
        except ValueError:
            self.logger.warning('Item is not in this model. Cannot update: %s', repr(item))
            return

        changed_index = self.index(changed_pos)  # QModelIndex
        self.dataChanged.emit(changed_index, changed_index, roles)

    def hasChildren(self, parent: QModelIndex) -> bool:
        # If valid, it's an item which does not have children
        # If not valid, it can
        return not parent.isValid()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def roleNames(self):
        return self.rolenames

    def unload(self):
        self.beginResetModel()
        if self._external_data:
            self._data = []  # Set to an empty list.
        else:
            self._data.clear()
        self.endResetModel()


class LockReleaseTrigger:
    def __init__(self, callback_func: Callable[[Set[Any]], None] = None):
        self._callback_func = callback_func
        self._lock_cnt = 0
        self._flags: Set[Any] = set()

    def trigger_action(self, action):
        self._flags.add(action)

    @property
    def active(self) -> bool:
        return self._lock_cnt > 0

    def __enter__(self):
        if self._lock_cnt == 0:
            # First locking. Reset old stuff.
            self._flags.clear()
        self._lock_cnt += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock_cnt -= 1
        if self._lock_cnt == 0 and self._callback_func:
            self._callback_func(self._flags)

    def unload(self):
        self._callback_func = None
        self._lock_cnt = 0
        self._flags.clear()
