# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import threading
from core.Toolbox import Pre_5_15_2_fix
import logging

class MultiShutter(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super(MultiShutter, self).__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name

        self._desired_position_path = settings.value('multishutter/' + self.name + "/desired_position_path", [])

        if isinstance(self._desired_position_path, str):
            self._desired_position_path = [self._desired_position_path]
        elif self._desired_position_path is None:
            self._desired_position_path = []

        self._desired_position = int(settings.value('multishutter/' + self.name + "/desired_position", 0))

        self._success = 0
        self._failed = 0

    @Signal
    def position_pathChanged(self):
        pass

    # @Property(str)
    def desired_position_path(self):
        return self._desired_position_path

    # @desired_position_path.setter
    @Pre_5_15_2_fix('QVariantList', desired_position_path, notify=position_pathChanged)
    def desired_position_path(self, key):
        self._desired_position_path = key
        self.settings.setValue('multishutter/' + self.name + "/desired_position_path", key)

    @Signal
    def positionChanged(self):
        pass

    @Signal
    def statusChanged(self):
        pass

    @Property(int, notify=statusChanged)
    def success(self):

        return self._success

    @Property(int, notify=statusChanged)
    def failed(self):

        return self._failed

    @Property(int, notify=positionChanged)
    def desired_position(self):
        return int(self._desired_position)

    @Slot(str)
    def add_path(self, value):

        self._desired_position_path.append(value)
        self.settings.setValue('multishutter/' + self.name + "/desired_position_path", self._desired_position_path)
        self.position_pathChanged.emit()

    @Slot(str)
    def remove_path(self, value):

        if value in self._desired_position_path:
            self._desired_position_path.remove(value)
            self.settings.setValue('multishutter/' + self.name + "/desired_position_path", self._desired_position_path)
            self.position_pathChanged.emit()

    @Slot(int)
    def set_position(self, value):

        self._desired_position = int(value)
        self.positionChanged.emit()
        self._success = 0
        self._failed = 0
        for path in self._desired_position_path:
            threading.Thread(target=self._set_position, args=(path, value,)).start()

    def _set_position(self, path, value):
        try:

            self.inputs.entries[path].set(int(value))
            self._success += 1
        except Exception as e:
            logging.error(str(e))
            self._failed += 1

        self.statusChanged.emit()
