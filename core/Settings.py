# -*- coding: utf-8 -*-

from typing import List, Optional
from datetime import datetime, date, time

from PySide2.QtCore import QSettings, QObject

from interfaces.DataTypes import DataType


class Settings(QSettings):
    def __init__(self, filename: str, fmt: QSettings.Format, parent: QObject = None):
        super().__init__(filename, fmt, parent)
        self._read_funcs = {
            int: self.int,
            str: self.str,
            bool: self.bool,
            float: self.float,
        }

        self._write_funcs = {
            int: self.setint,
            str: self.setstr,
            bool: self.setbool,
            float: self.setfloat,
        }

    # ---- get functions

    def get(self, key: str, default, datatype: DataType):
        # Get value and convert.
        basic_type = DataType.to_basic_type(datatype)
        return self._read_funcs.get(basic_type, self.get_raw)(key, default)
        # or KeyError("<type>")

    def get_raw(self, key: str, default):
        # Get value for supported data types without conversion
        return self.value(key, default)

    def int(self, key: str, default=0) -> Optional[int]:
        # get value with int conversion
        # noinspection PyTypeChecker
        v = self.value(key, default)
        if v is None:
            return None
        return int(v)

    def float(self, key: str, default=0.) -> Optional[float]:
        # get value with float conversion
        # noinspection PyTypeChecker
        v = self.value(key, default)
        if v is None:
            return None
        return float(v)

    def str(self, key: str, default='') -> Optional[str]:
        # get value with str conversion
        v = self.value(key, default)
        if v is None:
            return None
        return str(v)

    def bool(self, key: str, default=False) -> Optional[bool]:
        # get value with bool conversion
        v = self.value(key, default)
        if v is None:
            return None
        return v in {True, "true", 1, "1"} or default

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
        self._write_funcs.get(basic_type, self.set_raw)(key, value)
        # or KeyError("<type>")

    def set_raw(self, key: str, value):
        # Raw set value for supported types
        self.setValue(key, value)

    def setint(self, key: str, value: Optional[int]):
        # simple set value as int
        self.setValue(key, None if value is None else int(value))  # will be string

    def setfloat(self, key: str, value: Optional[float]):
        # simple set value as float
        self.setValue(key, None if value is None else str(float(value)))  # will be string anyway. Include dot.

    def setstr(self, key: str, value: Optional[str]):
        # simple set value as str
        self.setValue(key, None if value is None else str(value))  # str() to not create complex types

    def setbool(self, key: str, value: Optional[bool]):
        # simple set value as bool
        self.setValue(key, None if value is None else bool(value))  # will be string


def new_settings_instance(section: str = None) -> Settings:
    s = Settings('settings.ini', QSettings.IniFormat)
    if section:
        s.beginGroup(section)
    return s


settings = new_settings_instance()