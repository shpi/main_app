# -*- coding: utf-8 -*-

import logging

from PySide2.QtCore import QSettings, QObject, Property, Signal
from PySide2.QtGui import QPolygonF

from core.CircularBuffer import CircularBuffer
from core.Toolbox import Pre_5_15_2_fix


class ShowValue(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super(ShowValue, self).__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name

        self._value_path = settings.value('showvalue/' + self.name + "/path", '')

        if self._value_path in self.inputs.entries:
            self._value = self.inputs.entries[self._value_path].value
        else:
            self._value = 0

        self.buffer = CircularBuffer(100, initialvalue=self._value)

        self._precision = int(settings.value('showvalue/' + self.name + "/precision", 1))

        self._icon = settings.value('showvalue/' + self.name + "/icon", '')
        self._divider = settings.value('showvalue/' + self.name + "/divider", '1000')

        if self._value_path in self.inputs.entries:
            self.inputs.register_event(self._value_path, self.ui_event)

    @Signal
    def settingsChanged(self):
        pass

    @Signal
    def valueChanged(self):
        pass

    @Property(QPolygonF, notify=valueChanged)
    def preview(self):
        return self.buffer.preview(width=100, height=100, divider=self._divider)

    def get_inputs(self):
        return []

    def ui_event(self, path, value):
        try:
            self.buffer.append(value)
            if self._value != value and self.value_path == path:
                self._value = value
                self.valueChanged.emit()
        except Exception as e:
            logging.error(str(e))

    @Property(bool, notify=settingsChanged)
    def logging(self):
        if self._value_path in self.inputs.entries:
            return self.inputs.entries[self._value_path].logging
        else:
            return False

    @logging.setter
    def logging(self, value):
        if self._value_path in self.inputs.entries:
            self.inputs.entries[self._value_path].logging = bool(value)

    @Property(int, notify=settingsChanged)
    def interval(self):
        return self.inputs.entries[self._value_path].interval

    # @Property(str,notify=valueChanged)
    def precision(self):
        return self._precision

    # @value_path.setter
    @Pre_5_15_2_fix(int, precision, notify=settingsChanged)
    def precision(self, key):
        self.settings.setValue('showvalue/' + self.name + "/precision", key)
        logging.info(self.settings.value('showvalue/' + self.name + "/precision", ''))
        self._precision = int(key)

    # @Property(str,notify=valueChanged)
    def unit(self):
        return self._unit

    # @value_path.setter
    @Pre_5_15_2_fix(int, unit, notify=settingsChanged)
    def unit(self, key):
        self.settings.setValue('showvalue/' + self.name + "/unit", key)
        logging.info(self.settings.value('showvalue/' + self.name + "/unit", ''))
        self._precision = str(key)

    # @Property(str,notify=valueChanged)
    def value_path(self):
        return self._value_path

    # @value_path.setter
    @Pre_5_15_2_fix(str, value_path, notify=settingsChanged)
    def value_path(self, key):
        logging.info('setter ' + key)
        self.settings.setValue('showvalue/' + self.name + "/path", key)
        logging.info(self.settings.value('showvalue/' + self.name + "/path", ''))
        self.inputs.register_event(key, self.ui_event)
        self.inputs.unregister_event(self._value_path, self.ui_event)
        self._value_path = key

    # @Property(str,notify=valueChanged)
    def icon(self):
        return self._icon

    # @icon.setter
    @Pre_5_15_2_fix(str, icon, notify=settingsChanged)
    def icon(self, key):
        self._icon = key
        self.settings.setValue('showvalue/' + self.name + "/icon", key)
        self.valueChanged.emit()

    # @Property(str,notify=valueChanged)
    def divider(self):
        return str(self._divider)

    # @divider.setter
    @Pre_5_15_2_fix(str, divider, notify=settingsChanged)
    def divider(self, key):

        self._divider = float(key)
        self.settings.setValue('showvalue/' + self.name + "/divider", key)
        self.valueChanged.emit()

    def is_number(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    @Property(str, notify=valueChanged)
    def value(self):
        if self.is_number(self._value) and self.is_number(self._divider):
            return ("{:." + str(self._precision) + "f}").format(float(self._value) / float(self._divider))
        else:
            return self._value
