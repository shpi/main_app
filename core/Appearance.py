# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property
import time
import os
import logging
import threading
from datetime import datetime
from core.DataTypes import DataType
from core.Toolbox import Pre_5_15_2_fix
from core.Property import EntityProperty
from functools import partial


class NightModes:
    Off = 0
    On = 1
    FromTimer = 2  # Static configured start stop times
    FromTimer_StartStopInput = 3  # Fallback to FromInput if not in self.inputs
    # FromInput = 4
    __valid_range = Off, FromTimer_StartStopInput  # lowest and highest

    @classmethod
    def is_valid(cls, number) -> bool:
        min_, max_ = cls.__valid_range
        return min_ <= number <= max_


class Appearance(QObject):
    def __init__(self, inputs, settings: QSettings):
        super().__init__()

        self.path = 'appearance'
        self.inputs = inputs.entries
        self._backlightlevel = 0
        self._blackfilter = 0
        self.settings = settings
        self._module = EntityProperty(parent=self,
                                      category='module',
                                      entity='core',
                                      name='appearance',
                                      value='NOT_INITIALIZED',
                                      description='Appearance Module for Backlight / Nightmode etc.',
                                      type=DataType.MODULE,
                                      call=self.update,
                                      interval=int(settings.value("appearance/interval", 5)))

        self._background_night = int(settings.value("appearance/background_night", 1))
        self._min_backlight = int(settings.value("appearance/min", 60))
        self._max_backlight = int(settings.value("appearance/max", 100))
        self._min_backlight_night = int(settings.value("appearance/min_night", 30))
        self._max_backlight_night = int(settings.value("appearance/max_night", 100))

        self._start_input_key = str(settings.value("appearance/start_input_key", ''))
        self._stop_input_key = str(settings.value("appearance/stop_input_key", ''))

        self._night_mode = int(settings.value("appearance/night_mode", 0))
        self._night_mode_start = settings.value("appearance/night_mode_start", '00:00')
        self._night_mode_end = settings.value("appearance/night_mode_end", '00:00')

        self._jump_timer = int(settings.value("appearance/jump_timer", 20))
        self._jump_state = 0
        self._dim_timer = int(settings.value("appearance/dim_timer", 100))
        self._off_timer = int(settings.value("appearance/off_timer", 300))
        self.lastuserinput = time.time()
        self.state = 'ACTIVE'  # Enum('ACTIVE','SLEEP','OFF')
        self._night = False

        self.possible_devs = list()

        inputs.entries['core/input_dev/lasttouch'].events.append(self.tinterrupt)

        for key in self.inputs.keys():
            if key.startswith('module/input_dev') and self.inputs[key].type == DataType.THREAD:
                logging.debug(f"add to possible_devs: {key}")
                self.possible_devs.append(key)
                active = int(settings.value("appearance/" + key, 1))
                if active:
                    logging.debug(f"add to dev interrupt: {key}")
                    inputs.entries[key].events.append(self.interrupt)

    @Slot(str, result=str)
    def device_description(self, path) -> str:
        return self.inputs[path].description

    @Slot(str, result=bool)
    def selected_device(self, path) -> str:
        return bool(int(self.settings.value("appearance/" + path, 1)))

    @Signal
    def dim_timer_changed(self):
        pass

    @Signal
    def blackChanged(self):
        pass

    def get_inputs(self):
        return [self._module]

    # @Property(int, notify=dim_timer_changed)
    def dim_timer(self):
        return int(self._dim_timer)

    @Pre_5_15_2_fix(int, dim_timer, notify=dim_timer_changed)
    def dim_timer(self, seconds):
        self._dim_timer = int(seconds)
        self.settings.setValue("appearance/dim_timer", seconds)

    @Signal
    def start_input_changed(self):
        pass

    # @Property(str, notify=start_input_changed)
    def start_input_key(self):
        return self._start_input_key

    # @night_mode_start.setter
    @Pre_5_15_2_fix(str, start_input_key, notify=start_input_changed)
    def start_input_key(self, time_):
        self._start_input_key = time_
        self.settings.setValue("appearance/start_input_key", time_)

    @Signal
    def stop_input_changed(self):
        pass

    # @Property(str, notify=stop_input_changed)
    def stop_input_key(self):
        return self._stop_input_key

    # @night_mode_start.setter
    @Pre_5_15_2_fix(str, stop_input_key, notify=stop_input_changed)
    def stop_input_key(self, time_):
        self._stop_input_key = time_
        self.settings.setValue("appearance/stop_input_key", time_)

    @Signal
    def night_mode_start_changed(self):
        pass

    # @Property(str, notify=night_mode_start_changed)
    def night_mode_start(self):
        return self._night_mode_start

    # @night_mode_start.setter
    @Pre_5_15_2_fix(str, night_mode_start, notify=night_mode_start_changed)
    def night_mode_start(self, time_):
        self._night_mode_start = time_
        self.settings.setValue("appearance/night_mode_start", time_)

    @Signal
    def night_mode_end_changed(self):
        pass

    # @Property(str, notify=night_mode_end_changed)
    def night_mode_end(self):
        return self._night_mode_end

    # @night_mode_end.setter
    @Pre_5_15_2_fix(str, night_mode_end, notify=night_mode_end_changed)
    def night_mode_end(self, time_):
        self._night_mode_end = time_
        self.settings.setValue("appearance/night_mode_end", time_)

    @Slot(str)
    def delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)

    @Signal
    def jump_timer_changed(self):
        pass

    # @Property(int, notify=jump_timer_changed)
    def jump_timer(self):
        return int(self._jump_timer)

    # @jump_timer.setter
    @Pre_5_15_2_fix(int, jump_timer, notify=jump_timer_changed)
    def jump_timer(self, seconds):
        self._jump_timer = int(seconds)
        self.settings.setValue("appearance/jump_timer", seconds)

    @Signal
    def nightmodeChanged(self):
        pass

    # @Property(int, notify=nightmodeChanged)
    def night_mode(self):
        return self._night_mode

    @Pre_5_15_2_fix(int, night_mode, notify=nightmodeChanged)  # XXX
    def night_mode(self, value):
        self._night_mode = int(value)
        self.settings.setValue("appearance/night_mode", value)
        self.nightmodeChanged.emit()
        self.check_nightmode()

    @Signal
    def off_timer_changed(self):
        pass

    # @Property(int, notify=off_timer_changed)
    def off_timer(self):
        return int(self._off_timer)

    # @off_timer.setter
    @Pre_5_15_2_fix(int, off_timer, notify=off_timer_changed)
    def off_timer(self, seconds):
        self._off_timer = int(seconds)
        self.settings.setValue("appearance/off_timer", seconds)

    @Signal
    def background_Night_Changed(self):
        pass

    # @Property(bool, notify=background_Night_Changed)
    def background_night(self):
        return int(self._background_night)

    @Pre_5_15_2_fix(bool, background_night, notify=background_Night_Changed)  # XXX
    def background_night(self, bg_night):
        self._background_night = int(bg_night)
        self.settings.setValue("appearance/background_night", self._background_night)
        self.background_Night_Changed.emit()

    @Signal
    def rangeChanged(self):
        pass

    # @Property(int, notify=rangeChanged)
    def minbacklight(self):
        return int(self._min_backlight)

    # @minbacklight.setter
    @Pre_5_15_2_fix(int, minbacklight, notify=rangeChanged)
    def minbacklight(self, min_):
        self._min_backlight = int(min_)
        self.settings.setValue("appearance/min", self._min_backlight)
        self.rangeChanged.emit()

    # @Property(int, notify=rangeChanged)
    def minbacklight_night(self):
        return int(self._min_backlight_night)

    # @minbacklight_night.setter
    @Pre_5_15_2_fix(int, minbacklight_night, notify=rangeChanged)
    def minbacklight_night(self, min_):
        self._min_backlight_night = int(min_)
        self.settings.setValue("appearance/min_night", self._min_backlight_night)
        self.rangeChanged.emit()

    # @Property(int, notify=rangeChanged)
    def maxbacklight(self):
        return int(self._max_backlight)

    # @maxbacklight.setter
    @Pre_5_15_2_fix(int, maxbacklight, notify=rangeChanged)
    def maxbacklight(self, max_):
        self._max_backlight = int(max_)
        self.rangeChanged.emit()
        self.settings.setValue("appearance/max", self._max_backlight)
        self.set_backlight(self._max_backlight)
        self.rangeChanged.emit()

    # @Property(int, notify=rangeChanged)
    def maxbacklight_night(self):
        return int(self._max_backlight_night)

    # @maxbacklight_night.setter
    @Pre_5_15_2_fix(int, maxbacklight_night, notify=rangeChanged)
    def maxbacklight_night(self, max_):
        self._max_backlight_night = int(max_)
        self.rangeChanged.emit()
        self.settings.setValue("appearance/max_night", self._max_backlight_night)
        self.set_backlight(self._max_backlight_night)
        self.rangeChanged.emit()

    @Signal
    def nightChanged(self):
        pass

    @Property(int, notify=nightChanged)
    def night(self):
        return int(self._night)

    def check_nightmode(self):

        status = 'OK'

        if not NightModes.is_valid(self._night_mode):
            logging.debug(f"unknown nightmode: {self._night_mode}")
            return 'ERROR'

        if self._night_mode in (NightModes.Off, NightModes.On):
            # Easy job
            if self._night != self._night_mode:
                self._night = bool(self._night_mode)
                self.nightChanged.emit()
            return 'OK'

        if self._night_mode == NightModes.FromTimer_StartStopInput:

            # Read start/end from inputs
            if self._start_input_key not in self.inputs or self._stop_input_key not in self.inputs:
                logging.debug('Missing start and/or stop for automatic nightmode. Resetting to FromTimer.')
                # self.night_mode = NightModes.FromTimer
                return 'ERROR'

            start_input = self.inputs[self._start_input_key]
            stop_input = self.inputs[self._stop_input_key]

            if start_input.type != DataType.TIME or stop_input.type != DataType.TIME:
                logging.debug('Unknown start/stop type. Resetting to FromTimer.')
                # self.night_mode = NightModes.FromTimer
                return 'ERROR'

            start_str = start_input.value
            stop_str = stop_input.value

        if self._night_mode == NightModes.FromTimer:
            # Read start/stop from static values
            start_str = self._night_mode_start
            stop_str = self._night_mode_end

        # Working with pure times.
        try:
            start_time = datetime.strptime(start_str, '%H:%M').time()
            stop_time = datetime.strptime(stop_str, '%H:%M').time()
        except ValueError:
            start_time = datetime.strptime("00:00", '%H:%M').time()
            stop_time = datetime.strptime("00:00", '%H:%M').time()
            status = 'ERROR'

        if start_time == stop_time:
            # Invalid config. Do nothing.
            return 'ERROR'

        now_time = datetime.now().time()

        if start_time < stop_time:
            # 18:00 - 23:00
            night_new = start_time < now_time < stop_time
        else:
            # 23:00 - 8:00
            night_new = not (stop_time < now_time < start_time)

        if night_new != self._night:
            self._night = night_new
            self.nightChanged.emit()

        return status

    def update(self):

        status = 'OK'

        status = self.check_nightmode()

        if self.state in ('SLEEP',) and self._off_timer > 0 and (self.lastuserinput + self._off_timer < time.time()):
            logging.debug(f"changing nightmode to OFF, old state: {self.state}, lastinput: {self.lastuserinput}")
            self.set_backlight(0)
            self.state = 'OFF'

        elif self.state in ('ACTIVE',) and (self.lastuserinput + self._dim_timer < time.time()):
            logging.debug(f"changing nightmode to SLEEP, old state: {self.state}, lastinput: {self.lastuserinput}")
            if self._night:
                self.set_backlight(self._min_backlight_night)
            else:
                self.set_backlight(self._min_backlight)
            self.state = 'SLEEP'

        elif self.state in (
        'SLEEP', 'OFF') and self._dim_timer > 0 and self.lastuserinput + self._dim_timer > time.time():
            logging.debug(f"changing nightmode to ACTIVE, old state: {self.state}, lastinput: {self.lastuserinput}")
            if self._night:
                self.set_backlight(self._max_backlight_night)
            else:
                self.set_backlight(self._max_backlight)
            self.state = 'ACTIVE'

        if self._jump_state == 0 and self._jump_timer + self.lastuserinput < time.time():
            logging.debug(f"jump to home, timer: {self._jump_timer}, lastuserinput: {self.lastuserinput}")
            self._jump_state = 1
            self.jump_stateChanged.emit()

        return status

    @Signal
    def jump_stateChanged(self):
        pass

    @Property(int, notify=blackChanged)
    def backlightlevel(self):
        return int(self._backlightlevel)

    @Property(bool, notify=jump_stateChanged)
    def jump_state(self):
        return bool(self._jump_state)

    def set_backlight(self, value):
        setthread = threading.Thread(target=self._set_backlight, args=(value,))
        setthread.start()

    def _set_backlight(self, value):
        value = int(value)
        if value != self._backlightlevel:
            if value < 1:
                self.inputs['core/backlight/brightness'].set(0)

            elif value < 30:
                self.inputs['core/backlight/brightness'].set(1)
                self._blackfilter = ((100 - (value * 3.3)) / 100)

            elif value <= 100:
                self.inputs['core/backlight/brightness'].set(value)
                # mapping happens in backlight class int(self.mapFromTo(value, 30, 100, 1, 100)))
                self._blackfilter = 0

            self.blackChanged.emit()
            self._backlightlevel = value

    def interrupt(self, key, value):
        #logging.debug(f"interrupt key: {key}, value: {value}")
        if value > 0:
                if self.state == 'OFF':
                    self.lastuserinput = time.time() - self._dim_timer
                    logging.debug(
                        f"changing nightmode to SLEEP, old state: {self.state}, lastinput: {self.lastuserinput}")
                    self.state = 'SLEEP'
                    if self._night:
                        self.set_backlight(self._min_backlight_night)
                    else:
                        self.set_backlight(self._min_backlight)


    def tinterrupt(self, key, value):
        #logging.debug(f"tinterrupt key: {key}, value: {value}")
        self.lastuserinput = time.time()
        self._jump_state = 0
        self.jump_stateChanged.emit()
        if self.state in ('OFF', 'SLEEP'):
                logging.debug(
                        f"changing nightmode to ACTIVE, old state: {self.state}, lastinput: {self.lastuserinput}")
                self.state = 'ACTIVE'
                if self._night:
                    self.set_backlight(self._max_backlight_night)
                else:
                    self.set_backlight(self._max_backlight)


    @Slot(str, int)
    def setDeviceTrack(self, path, value):
        value = int(value)
        self.settings.setValue("appearance/" + path, value)
        if value == 1:
            self.inputs[path].events.append(self.interrupt)
        else:
            i = 0
            for interrupt in self.inputs[path].events:
                if interrupt == self.interrupt:
                    self.inputs[path].events.pop(i)
                i += 1

    @Property(float, notify=blackChanged)
    def blackfilter(self):
        return self._blackfilter

    # Workaround for https://bugreports.qt.io/browse/PYSIDE-1426
    # @Property("QVariantMap", constant=True)
    def devices(self) -> list:
        return self.possible_devs

    devices = Property("QVariantList", devices, constant=True)
