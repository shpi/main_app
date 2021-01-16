# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import threading
from core.Toolbox import Pre_5_15_2_fix


class ShowValue(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super(ShowValue, self).__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name
        self._value_path = settings.value('showvalue/' + self.name + "/path", 'alsa/PCH/recording')
        self._value = str(self.inputs.entries[self._value_path]['value'])
        self._icon = settings.value('showvalue/' + self.name + "/icon", '')
        self._divider = settings.value('showvalue/' + self.name + "/divider", '1000')


    @Signal
    def valueChanged(self):
            pass


    def update(self):
        if self._value != str(self.inputs.entries[self._value_path]['value']):
            self._value = str(self.inputs.entries[self._value_path]['value'])
            self.valueChanged.emit()


    @Property(bool,notify=valueChanged)
    def logging(self):
        return self.inputs.entries[self._value_path]['logging']


    #@Property(str,notify=valueChanged)
    def value_path(self):
        return self._value_path


    #@value_path.setter
    @Pre_5_15_2_fix(str, value_path, notify=valueChanged)
    def value_path(self, key):
        self._value_path = key
        self.settings.setValue('showvalue/' + self.name + "/path", key)

    #@Property(str,notify=valueChanged)
    def icon(self):
        return self._icon

    #@icon.setter
    @Pre_5_15_2_fix(str, icon, notify=valueChanged)
    def icon(self, key):

        self._icon = key
        self.settings.setValue('showvalue/' + self.name + "/icon", key)
        self.valueChanged.emit()


    #@Property(str,notify=valueChanged)
    def divider(self):
        return str(self._divider)

    #@divider.setter
    @Pre_5_15_2_fix(str, divider, notify=valueChanged)
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
            return str(float(self._value) / float(self._divider))
        else:
            return "{:.1f}".format(self._value)


