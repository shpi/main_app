# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import threading
from core.Toolbox import Pre_5_15_2_fix




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
        self._heatingstate = False
        self._actual_temp = 20.5
        self._hysteresis = 0.5
        self._set_temp = float(settings.value("thermostat/"+ self.name + '/set_temp', 20))



    @Signal
    def stateChanged(self):
                        pass

    @Signal
    def tempChanged(self):
                    pass


    @Signal
    def settingsChanged(self):
                        pass



    @Property(bool,notify=stateChanged)
    def heatingstate(self):
       return int(self._heatingstate)


    @Property(float,notify=tempChanged)
    def actual_temp(self):
      return float(self._actual_temp)



    def set_temp(self):
       return float(self._set_temp)


    @Pre_5_15_2_fix(float, set_temp, notify=settingsChanged)
    def set_temp(self, value):
        self._set_temp = float(value)
        self.settings.setValue("thermostat/"+ self.name + '/set_temp', value)
        self.settingsChanged.emit()


    def heatingcontact_path(self):
       return int(self._heatingcontact_path)


    @Pre_5_15_2_fix(str, heatingcontact_path, notify=settingsChanged)
    def heatingcontact_path(self, value):
        self._heatingcontact_path = str(value)
        self.settings.setValue("thermostat/"+ self.name + '/heatingcontact', self._heatingcontact_path)
        self.settingsChanged.emit()



    def irtemp_path(self):
       return int(self._heatingcontact_path)


    @Pre_5_15_2_fix(str, irtemp_path, notify=settingsChanged)
    def irtemp_path(self, value):
        self._irtemp_path = str(value)
        self.settings.setValue("thermostat/"+ self.name + '/irtemp', self._irtemp_path)
        self.settingsChanged.emit()

    def internaltemp_path(self):
       return int(self._internaltemp_path)


    @Pre_5_15_2_fix(str, internaltemp_path, notify=settingsChanged)
    def internaltemp_path(self, value):
        self._internaltemp_path = str(value)
        self.settings.setValue("thermostat/"+ self.name + '/internaltemp', value)
        self.settingsChanged.emit()





    def update(self):

       try:
        if (self.inputs['lastinput']['value'] + 10 < time.time()):

            objecttemp = float(self.inputs[self._irtemp_path]['value'])
            internaltemp = float(self.inputs[self._internaltemp_path]['value'])
            correctedtemp = objecttemp - 1
            self._actual_temp = correctedtemp

            if (internaltemp > objecttemp):
                        correctedtemp = objecttemp - ((correctedtemp - internaltemp) / 6)
                        self._actual_temp = correctedtemp
                        self.tempChanged.emit()

            if   (correctedtemp + self._hysteresis) < self._set_temp:
                               self.inputs[self._heatingcontact_path]['set'](True)
                               self._heatingstate = True
                               self.stateChanged.emit()

            elif (correctedtemp - self._hysteresis) > self._set_temp:
                               self.inputs[self._heatingcontact_path]['set'](False)
                               self._heatingstate = False
                               self.stateChanged.emit()
       except Exception as e:
           print(e)



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


