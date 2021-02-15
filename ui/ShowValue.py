# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal
from core.Toolbox import Pre_5_15_2_fix
import logging


class ShowValue(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super(ShowValue, self).__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name
        self._value_path = settings.value('showvalue/' + self.name + "/path", '')
        self._value = ''
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

    def ui_event(self):
        try:
            if self._value != str(self.inputs.entries[self._value_path].value):
                self._value = str(self.inputs.entries[self._value_path].value)
                self.valueChanged.emit()
        except Exception as e:
            logging.error(str(e))

    @Property(bool, notify=settingsChanged)
    def logging(self):
        return self.inputs.entries[self._value_path].logging

    @Property(int, notify=settingsChanged)
    def interval(self):
        return self.inputs.entries[self._value_path].interval

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
            return "{:.1f}".format(float(self._value) / float(self._divider))
        else:
            return self._value
