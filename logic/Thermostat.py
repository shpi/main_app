# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import threading




class ThermostatModes:
    OFF = 0 # totally off
    AWAY = 1 # constant away temp
    ECO = 2 # reduced automatic temp
    AUTO = 3 # automatic temp regarding schedule
    PARTY = 4 # ignore schedule
    __valid_range = OFF, PARTY  # lowest and highest

    @classmethod
    def is_valid(cls, number) -> bool:
        min_, max_ = cls.__valid_range
        return min_ <= number <= max_


class Thermostat(QObject):
    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()
        self.name = name
        self.settings = settings
        self.inputs = inputs.entries
        self._schedule = self.convert_schedule(settings.value("thermostat/"+ self.name + '/schedule', ''))

        self._schedulemode = int(settings.value("thermostat/"+ self.name + '/schedulemode', 7))
        # 0 off, 1 day, 2 workday/weekend,  7 week

        self._mode = int(settings.value("thermostat/"+ self.name + '/mode', 3))


        self._heatingcontact_path = settings.value("thermostat/"+ self.name + '/heatingcontact', '')
        self._irtemp_path = settings.value("thermostat/"+ self.name + '/irtemp', '')
        self._internaltemp_path = settings.value("thermostat/"+ self.name + '/internaltemp', '')


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


