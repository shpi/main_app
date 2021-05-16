# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject


class Settings(QSettings):
    def __init__(self, filename: str, fmt: QSettings.Format, parent: QObject = None):
        super().__init__(filename, fmt, parent)

    def get(self, key: str, default):
        # get value without type conversion
        return self.value(key, default)

    def int(self, key: str, default=0) -> int:
        # get value with int conversion
        return int(self.value(key, default))

    def str(self, key: str, default="") -> str:
        # get value with str conversion
        return str(self.value(key, default))

    def bool(self, key: str, default=False) -> bool:
        # Create bool via int
        return bool(self.int(key, default))

    def list(self, key: str, default: list = None, none_to_empty_list=True) -> list:
        # Create bool via int
        data = self.value(key, default)

        if not isinstance(data, list):
            if data is None and none_to_empty_list:
                return []

            return [data]

        return data  # Already a list

    def set(self, key: str, value):
        # simple set without type conversions
        self.setValue(key, value)

    def setint(self, key: str, value):
        # simple set value as int
        self.setValue(key, int(value))

    def setstr(self, key: str, value):
        # simple set value as str
        self.setValue(key, str(value))


settings = Settings('settings.ini', QSettings.IniFormat)
