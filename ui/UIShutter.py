# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import threading


class UIShutter(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super(UIShutter, self).__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name
        self._actual_position_path = settings.value('uishutter/' + self.name + "/actual_position", 'shutter/local/actual_position')
        self._desired_position_path = settings.value('uishutter/' + self.name + "/desired_position", 'shutter/local/desired_position')

        try:
            self._actual_position = int(self.inputs.entries[self._actual_position_path]['value'])
        except:
            print(self.name + ' no valid actual position value')
            self._actual_position = None

        try:
            self._desired_position = int(self.inputs.entries[self._desired_position_path]['value'])
        except:
            print(self.name + ' no valid desired position value')

        self.checkthread = threading.Thread(target=self.thread)
        self.checkthread.start()

    @Property(str)
    def actual_position_path(self):
        return self._actual_position_path

    @actual_position_path.setter
    def actual_position_path(self, key):
        self._actual_position_path = key
        self.settings.setValue('uishutter/' + self.name + "/actual_position", key)

    @Property(str)
    def desired_position_path(self):
        return self._desired_position_path

    @desired_position_path.setter
    def desired_position_path(self, key):
        self._desired_position_path = key
        self.settings.setValue('uishutter/' + self.name + "/desired_position", key)

    def update(self):
        if self._desired_position !=  self.inputs.entries[self._desired_position_path]['value']:
            self._desired_position =  self.inputs.entries[self._desired_position_path]['value']
            self.positionChanged.emit()
            if not self.checkthread.is_alive():
                self.checkthread = threading.Thread(target=self.thread)
                self.checkthread.start()

    def thread(self):
        while self._actual_position is not None and self._actual_position != self._desired_position:
            time.sleep(0.1)

            self.inputs.update_value(self._actual_position_path)

            if self._actual_position != self.inputs.entries[self._actual_position_path]['value']:
                self._actual_position = self.inputs.entries[self._actual_position_path]['value']
                self.positionChanged.emit()

    @Signal
    def positionChanged(self):
        pass

    @Property(int, notify=positionChanged)
    def desired_position(self):
        return int(self.inputs.entries[self._desired_position_path]['value'])

    @Property(float, notify=positionChanged)
    def actual_position(self):
        return int(self.inputs.entries[self._actual_position_path]['value'])

    @Slot(int)
    def set_position(self, value):
        self.inputs.entries[self._desired_position_path]['set'](int(value))
        self._desired_position = int(value)
        self.positionChanged.emit()
        if not self.checkthread.is_alive():
            self.checkthread = threading.Thread(target=self.thread)
            self.checkthread.start()