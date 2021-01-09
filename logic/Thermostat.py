# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import threading


class Thermostat(QObject):
    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()
        self.name = name
        self.settings = settings
        self.inputs = inputs.entries
        self._schedule = self.convert_schedule(settings.value("thermostat/"+ self.name + '/schedule', ''))

        self._schedulemode = (settings.value("thermostat/"+ self.name + '/schedulemode', 'off'))
        # off, day, workday/weekend, week

        self._mode = settings.value("thermostat/"+ self.name + '/mode', 'Auto')

        # boolean mode with two binary outputs
        self._heatingcontact = settings.value("thermostat/"+ self.name + '/heatingcontact', '')
        self._coolingcontact = settings.value("thermostat/"+ self.name + '/coolingcontact', '')


    def convert_schedule(self,value):
            value = [i.strip(';').split(';') for i in value.strip().split('\n')]

            for a in range(0, len(value)):
                for b in range(0, len(value[a])):
                        if ':' in value[a][b]:
                            value[a][b] = list(map(int, value[a][b].split(':'))) # tuple didnt work with qml


                if len(value[a]):
                    try:
                        value[a] = sorted(value[a], key=lambda tup: tup[0])
                    except IndexError:
                        pass


            return value


    @Slot(str)
    def save_schedule(self, value):
        self.settings.setValue("thermostat/"+ self.name + '/schedule', value)
        self._schedule = self.convert_schedule(value)

    @Signal
    def scheduleChanged(self):
            pass

    @Property('QVariantList', notify=scheduleChanged)
    def schedule(self):
         return self._schedule


