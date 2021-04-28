# -*- coding: utf-8 -*-

import logging
import threading
import time

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot

from core.Toolbox import Pre_5_15_2_fix


class Shutter(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super(Shutter, self).__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name
        self._actual_position_path = settings.value('shutter/' + self.name + "/actual_position", '')
        self._desired_position_path = settings.value('shutter/' + self.name + "/desired_position", '')
        try:
            if self._actual_position_path in self.inputs.entries:
                self.inputs.register_event(self._actual_position_path, self.ui_event)
                self._actual_position = int(self.inputs.entries[self._actual_position_path].value)
            else:
                self._actual_position = None
                logging.error(self.name + ' no valid actual position value')

            if self._desired_position_path in self.inputs.entries:
                self.inputs.register_event(self._desired_position_path, self.ui_event)
                self._desired_position = int(self.inputs.entries[self._desired_position_path].value)
            else:
                self._desired_position = None
                logging.error(self.name + ' no valid desired position value')
        except:
            self._actual_position = None
            self._desired_position = None
            pass

        if self._actual_position_path in self.inputs.entries:
            self.inputs.register_event(self._actual_position_path, self.ui_event)

        if self._desired_position_path in self.inputs.entries:
            self.inputs.register_event(self._desired_position_path, self.ui_event)

        self.checkthread = threading.Thread(target=self.thread)
        self.checkthread.start()

    def delete_inputs(self):
        pass

    @Signal
    def position_pathChanged(self):
        pass

    # @Property(str)
    def actual_position_path(self):
        return self._actual_position_path

    # @actual_position_path.setter
    @Pre_5_15_2_fix(str, actual_position_path, notify=position_pathChanged)
    def actual_position_path(self, key):
        logging.debug(key)
        if self._actual_position_path in self.inputs.entries:
            self.inputs.unregister_event(self._actual_position_path, self.ui_event)
        self._actual_position_path = key
        if self._actual_position_path in self.inputs.entries:
            self.inputs.register_event(self._actual_position_path, self.ui_event)
        self.settings.setValue('shutter/' + self.name + "/actual_position", key)

    # @Property(str)
    def desired_position_path(self):
        return self._desired_position_path

    # @desired_position_path.setter
    @Pre_5_15_2_fix(str, desired_position_path, notify=position_pathChanged)
    def desired_position_path(self, key):
        if self._desired_position_path in self.inputs.entries:
            self.inputs.unregister_event(self._desired_position_path, self.ui_event)
        self._desired_position_path = key
        if self._desired_position_path in self.inputs.entries:
            self.inputs.register_event(self._desired_position_path, self.ui_event)

        self.settings.setValue('shutter/' + self.name + "/desired_position", key)

    def ui_event(self, path, value):
        if path == self._desired_position_path and self._desired_position_path in self.inputs.entries:
            self._desired_position = value
            self.positionChanged.emit()
            if not self.checkthread.is_alive():
                self.checkthread = threading.Thread(target=self.thread)
                self.checkthread.start()

        if path == self._actual_position_path and self._actual_position_path in self.inputs.entries:
            self._actual_position = value
            self.positionChanged.emit()
            if not self.checkthread.is_alive():
                self.checkthread = threading.Thread(target=self.thread)
                self.checkthread.start()

    def thread(self):
        while self._actual_position is not None and self._actual_position != self._desired_position:
            self.inputs.entries[self._desired_position_path].update()
            self.inputs.entries[self._actual_position_path].update()
            time.sleep(0.1)
            # self.inputs.update_value(self._actual_position_path)

    @Signal
    def positionChanged(self):
        pass

    @Property(int, notify=positionChanged)
    def desired_position(self):
        return int(self.inputs.entries[self._desired_position_path].value)

    @Property(float, notify=positionChanged)
    def actual_position(self):
        return int(self.inputs.entries[self._actual_position_path].value)

    @Slot(int)
    def set_position(self, value):
        self.inputs.entries[self._desired_position_path].set(int(value))
        self._desired_position = int(value)
        self.positionChanged.emit()
        if not self.checkthread.is_alive():
            self.checkthread = threading.Thread(target=self.thread)
            self.checkthread.start()
