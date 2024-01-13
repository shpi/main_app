# -*- coding: utf-8 -*-

import datetime
import logging
import sys

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot

from core.DataTypes import DataType
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix


class ThermostatModes:
    OFF = 0  # totally off
    AWAY = 1  # constant away temp
    ECO = 2  # reduced automatic temp
    AUTO = 3  # automatic temp regarding schedule
    PARTY = 4  # ignore schedule
    __valid_range = OFF, PARTY  # lowest and highest

    @classmethod
    def is_valid(cls, number) -> bool:
        min_, max_ = cls.__valid_range
        return min_ <= number <= max_


class Schedule:

    @staticmethod
    def seconds_since_midnight():
        now = datetime.datetime.now()
        return now.hour * 3600 + now.minute * 60 + now.second

    @staticmethod
    def minutes_since_midnight(day):
        return day.hour * 60 + day.minute

    @staticmethod
    def weekday(day=datetime.datetime.today()):
        return int(day.strftime('%w'))

        # 0 Sunday .. 1 Monday ...

    @staticmethod
    def get_desired_temp(schedule_map, mode, day):

        # schedule  [week:  [day [seconds,temp], ], ]
        # mode: 7 week,   2 workday weekend,  1 day, 0 none
        # day: datetime object
        # minutes_since_midnight

        weekday = Schedule.weekday(day)
        minutes_since_midnight = Schedule.minutes_since_midnight(day)

        if mode == 7:
            pass

        # reduce week to workday / weekend
        elif mode == 2:  # mon - friDAY 1..5 -> 1
            if weekday in (1, 2, 3, 4, 5):
                weekday = 1
            else:
                weekday = 0
        # reduce week to day
        elif mode == 1:
            weekday = 0

            # no offsets at all
        elif mode == 0:
            return 0, 0

        if len(schedule_map) <= weekday:
            return 0, 0

        if len(schedule_map[weekday]) == 0:
            return Schedule.get_desired_temp(schedule_map, mode,
                                             (day.replace(hour=23, minute=59, second=59) - datetime.timedelta(1)))

        else:
            temp = None
            since = None
            i = 0

            while len(schedule_map[weekday]) > i and minutes_since_midnight >= int(schedule_map[weekday][i][0]):
                temp = schedule_map[weekday][i][1]
                since = schedule_map[weekday][i][0]
                i += 1

            if temp is None:
                return Schedule.get_desired_temp(schedule_map, mode,
                                                 (day.replace(hour=23, minute=59, second=59) - datetime.timedelta(1)))
            else:
                return temp, since


class Thermostat(QObject):


    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()
        self.name = name
        self.settings = settings
        self.inputs = inputs.entries

        self._schedule_mode = int(settings.value("thermostat/" + self.name + '/schedule_mode', 7))
        self._schedule = self.convert_schedule(settings.value("thermostat/" + self.name + '/schedule', ''))
        # 0 off, 1 day, 2 workday/weekend,  7 week

        self._thermostat_mode = int(settings.value("thermostat/" + self.name + '/thermostat_mode', 3))
        self._heating_contact_path = settings.value("thermostat/" + self.name + '/heating_contact_path', '')
        self._temp_path = settings.value("thermostat/" + self.name + '/temp_path', '')
        self._auto_temp = float(settings.value("thermostat/" + self.name + '/auto_temp', 20))
        self._party_temp = float(settings.value("thermostat/" + self.name + '/party_temp', 25))
        self._eco_temp = float(settings.value("thermostat/" + self.name + '/eco_temp', 18))
        self._away_temp = float(settings.value("thermostat/" + self.name + '/away_temp', 16))

        self._hysteresis = int(settings.value("thermostat/" + self.name + '/hysteresis', 100))
        self._actual_temp = None
        self._offset = 0

        self._heating_state = EntityProperty(
                                      category='logic',
                                      name='thermostat_' + name + '_state',
                                      value=0,
                                      description='Thermostat heating state',
                                      type=DataType.BOOL,
                                      call=None,
                                      interval=-1)

        self._module = EntityProperty(
                                      category='module',
                                      name='thermostat_' + name,
                                      value='NOT_INITIALIZED',
                                      description='Thermostat Module for binary output',
                                      type=DataType.MODULE,
                                      call=self.update,
                                      interval=10)

    def get_inputs(self) -> list:
        return [self._module, self._heating_state]



    @Signal
    def offsetChanged(self):
        pass

    @Signal
    def tempChanged(self):
        pass

    @Signal
    def settingsChanged(self):
        pass

    @Signal
    def scheduleModeChanged(self):
        pass

    @Signal
    def thermostatModeChanged(self):
        pass

    @Signal
    def heatingStateChanged(self):
        pass

    @Signal
    def scheduleChanged(self):
        pass

    @Signal
    def pathChanged(self):
        pass

    @Property(int, notify=offsetChanged)
    def offset(self):
        return int(self._offset)

    @Property(float, notify=tempChanged)
    def actual_temp(self):
        if self._actual_temp is not None:
            return float(self._actual_temp / 1000)
        else:
            return None

    def set_temp(self):
        if self.thermostat_mode == ThermostatModes.OFF:
            return 'OFF'

        elif self.thermostat_mode == ThermostatModes.AWAY:
            return self._away_temp

        elif self.thermostat_mode == ThermostatModes.ECO:
            return self._eco_temp

        elif self.thermostat_mode == ThermostatModes.AUTO:
            return self._auto_temp

        elif self.thermostat_mode == ThermostatModes.PARTY:
            return self._party_temp

    @Pre_5_15_2_fix(float, set_temp, notify=settingsChanged)
    def set_temp(self, value):

        if self._thermostat_mode == ThermostatModes.AWAY:
            self.settings.setValue("thermostat/" + self.name + '/away_temp', value)
            self._away_temp = value

        elif self._thermostat_mode == ThermostatModes.ECO:
            self.settings.setValue("thermostat/" + self.name + '/eco_temp', value)
            self._eco_temp = value

        elif self._thermostat_mode == ThermostatModes.AUTO:
            self.settings.setValue("thermostat/" + self.name + '/auto_temp', value)
            self._auto_temp = value

        elif self._thermostat_mode == ThermostatModes.PARTY:
            self.settings.setValue("thermostat/" + self.name + '/party_temp', value)
            self._party_temp = value

        self.settingsChanged.emit()

    # @Property(int, notify=scheduleChanged)
    def schedule_mode(self):
        return int(self._schedule_mode)

    # @schedule_mode.setter
    @Pre_5_15_2_fix(int, schedule_mode, notify=scheduleModeChanged)
    def schedule_mode(self, value):
        logging.debug('setting schedule mode:' + str(value))
        self._schedule_mode = int(value)
        self.settings.setValue("thermostat/" + self.name + '/schedule_mode', value)
        self.scheduleModeChanged.emit()

    def hysteresis(self):
        return int(self._hysteresis)

    @Pre_5_15_2_fix(int, hysteresis, notify=settingsChanged)
    def hysteresis(self, value):
        logging.debug('setting hysteresis:' + str(value))
        self._hysteresis = int(value)
        self.settings.setValue("thermostat/" + self.name + '/hysteresis', value)
        self.settingsChanged.emit()

    # @Property(int, notify=thermostatModeChanged)
    def thermostat_mode(self):
        return int(self._thermostat_mode)

    # @thermostat_mode.setter
    @Pre_5_15_2_fix(int, thermostat_mode, notify=thermostatModeChanged)
    def thermostat_mode(self, value):
        if ThermostatModes.is_valid(value):
            logging.debug('setting thermostat mode:' + str(value))
            self._thermostat_mode = int(value)
            self.settings.setValue("thermostat/" + self.name + '/thermostat_mode', value)
            self.thermostatModeChanged.emit()
            self.settingsChanged.emit()

        else:
            logging.error('Requested thermostat mode not valid')

    def heating_contact_path(self):
        return str(self._heating_contact_path)

    @Pre_5_15_2_fix(str, heating_contact_path, notify=pathChanged)
    def heating_contact_path(self, value):
        self._heating_contact_path = str(value)
        self.settings.setValue("thermostat/" + self.name + '/heating_contact_path', self._heating_contact_path)
        self.pathChanged.emit()

    def temp_path(self):
        return str(self._temp_path)

    @Pre_5_15_2_fix(str, temp_path, notify=pathChanged)
    def temp_path(self, value):
        self._temp_path = str(value)
        self.settings.setValue("thermostat/" + self.name + '/temp_path', self._temp_path)
        self.pathChanged.emit()

    def heating_state(self):
        return str(self._heating_state.value)

    @Pre_5_15_2_fix(str, heating_state, notify=heatingStateChanged)
    def heating_state(self, value):
        self._heating_state.value = int(value)
        # self.settings.setValue("thermostat/" + self.name + '/heating_state', value)
        self.heatingStateChanged.emit()

    def set_state(self, value):
        if int(value) != self._heating_state.value:
            logging.info('set heating to ' + str(value))
            self._heating_state.value = int(value)
            self.inputs[self._heating_contact_path].set(bool(value))
            self.heatingStateChanged.emit()

    def update(self):

        if self._temp_path not in self.inputs:
            logging.error('temp path not in inputs')
            return 'ERROR'

        if self._heating_contact_path not in self.inputs:
            logging.error('heating contact path not in inputs')
            return 'ERROR'

        try:

           self._actual_temp = self.inputs[self._temp_path].value
           if self._actual_temp == None:
              return 'PENDING'
           else:
            self.tempChanged.emit()

            if self._thermostat_mode == ThermostatModes.OFF:  # totally off
                self.set_state(0)
                self._offset = 0
                self.offsetChanged.emit()
                return 'OK'

            elif self._thermostat_mode == ThermostatModes.AWAY:  # constant away temp
                set_temp = self._away_temp * 1000
                self._offset = 0
                self.offsetChanged.emit()

            elif self._thermostat_mode == ThermostatModes.ECO:  # reduced automatic temp
                offset, since = Schedule.get_desired_temp(self._schedule, self._schedule_mode,
                                                          datetime.datetime.today())
                set_temp = (self._eco_temp + offset - 1) * 1000
                self._offset = int(offset)
                self.offsetChanged.emit()
                logging.info('thermostat eco modus, actual schedule offset ' + str(offset))

            elif self._thermostat_mode == ThermostatModes.AUTO:  # automatic temp regarding schedule
                offset, since = Schedule.get_desired_temp(self._schedule, self._schedule_mode,
                                                          datetime.datetime.today())
                set_temp = (self._auto_temp + offset) * 1000
                self._offset = int(offset)
                self.offsetChanged.emit()
                logging.info('thermostat auto modus, actual schedule offset  ' + str(offset))

            elif self._thermostat_mode == ThermostatModes.PARTY:  # ignore schedule
                set_temp = self._party_temp * 1000
                self._offset = 0
                self.offsetChanged.emit()
                logging.info('thermostat party')

            else:
                logging.error('no thermostat mode detected, heating off')
                return 'ERROR'

            if (self._actual_temp + self._hysteresis) < set_temp:
                logging.info('set temp: ' + str(set_temp))
                logging.info('act temp: ' + str(self._actual_temp))
                self.set_state(1)

            elif (self._actual_temp + self._hysteresis) > set_temp:
                logging.info('set temp: ' + str(set_temp))
                logging.info('act temp: ' + str(self._actual_temp))
                self.set_state(0)

            return 'OK'

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line: {line_number}')
            return 'ERROR'

    def convert_schedule(self, value):
        if not value.strip():
            return []  # Return an empty array if input is empty

        schedule = []
        daily_schedules = value.strip().split('\n')

        for daily_schedule in daily_schedules:
            day_schedule = []
            for time_range in daily_schedule.strip(';').split(';'):
                if ':' in time_range:
                    try:
                        time_range_parts = list(map(int, time_range.split(':')))
                        if len(time_range_parts) == 2:
                            day_schedule.append(time_range_parts)
                    except ValueError:
                        # Handle the case where conversion to int fails
                        pass

            if day_schedule:
                try:
                     day_schedule = sorted(day_schedule, key=lambda tup: tup[0])
                     schedule.append(day_schedule)
                except IndexError:
                    # Handle cases where the tuple structure is not as expected
                    pass

        return schedule


    def convert_schedule_old(self, value):
        value = [i.strip(';').split(';') for i in value.strip().split('\n')]

        for a in range(0, len(value)):
            for b in range(0, len(value[a])):
                if ':' in value[a][b]:
                    value[a][b] = list(map(int, value[a][b].split(':')))  # tuple didnt work with qml

            if len(value[a]):
                try:
                    value[a] = sorted(value[a], key=lambda tup: tup[0])
                except IndexError:
                    pass

        return value

    @Slot(str)
    def save_schedule(self, value):
        self.settings.setValue("thermostat/" + self.name + '/schedule', value)
        self._schedule = self.convert_schedule(value)

    @Property('QVariantList', notify=scheduleChanged)
    def schedule(self):
        return self._schedule
