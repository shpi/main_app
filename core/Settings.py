# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject
from typing import List
from core.DataTypes import DataType

# Settings functions shadow internal classes :(
_int = int
_str = str
_bool = bool
_float = float


class Settings(QSettings):
    def __init__(self, filename: str, fmt: QSettings.Format, parent: QObject = None):
        super().__init__(filename, fmt, parent)

    # ---- get functions

    def get(self, key: str, default, datatype: DataType):
        # Get value and convert.
        basic_type = DataType.to_basic_type(datatype)
        return self._read_funcs[basic_type](key, default)
        # or KeyError("<type>")

    def int(self, key: str, default=0) -> int:
        # get value with int conversion
        # noinspection PyTypeChecker
        return int(self.value(key, default))

    def float(self, key: str, default=0.) -> float:
        # get value with float conversion
        # noinspection PyTypeChecker
        return float(self.value(key, default))

    def str(self, key: str, default="") -> str:
        # get value with str conversion
        return str(self.value(key, default))

    def bool(self, key: str, default=False) -> bool:
        # get value with bool conversion
        return self.value(key) in (True, "true", 1, "1") or default

    def list(self, key: str, default: list = None, none_to_empty_list=True) -> List[str]:
        # get list of strings
        data = self.value(key, default)

        if not isinstance(data, list):
            if data is None and none_to_empty_list:
                return []

            # Single string element
            return [str(data)]

        return data  # Already a list (of strings)

    # ---- set functions

    def set(self, key: str, value, datatype: DataType):
        # Get value and convert.
        basic_type = DataType.to_basic_type(datatype)
        self._write_funcs[basic_type](key, value)
        # or KeyError("<type>")

    def setint(self, key: str, value: int):
        # simple set value as int
        self.setValue(key, int(value))  # will be string

    def setfloat(self, key: str, value: float):
        # simple set value as float
        self.setValue(key, str(float(value)))  # will be string anyway. Include dot.

    def setstr(self, key: str, value: str):
        # simple set value as str
        self.setValue(key, str(value))  # str() to not create complex types

    def setbool(self, key: str, value: bool):
        # simple set value as bool
        self.setValue(key, bool(value))  # will be string

    _read_funcs = {
        _int: int,
        _str: str,
        _bool: bool,
        _float: float,
    }

    _write_funcs = {
        _int: setint,
        _str: setstr,
        _bool: setbool,
        _float: setfloat,
    }


settings = Settings('settings.ini', QSettings.IniFormat)
