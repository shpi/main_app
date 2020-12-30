# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import os
# from enum import Enum for self.state later
import threading
from datetime import datetime
from core.DataTypes import DataType


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

        self.inputs = inputs.entries
        self.backlightlevel = 0
        self._blackfilter = 0
        self.settings = settings
        self._background_night = int(settings.value("appearance/background_night", 1))
        self._min_backlight = int(settings.value("appearance/min", 20))
        self._max_backlight = int(settings.value("appearance/max", 100))
        self._min_backlight_night = int(settings.value("appearance/min_night", 20))
        self._max_backlight_night = int(settings.value("appearance/max_night", 100))

        self._night_mode = int(settings.value("appearance/night_mode", 0))
        self._night_mode_start = settings.value("appearance/night_mode_start", '00:00')
        self._night_mode_end = settings.value("appearance/night_mode_end", '00:00')

        self._jump_timer = int(settings.value("appearance/jump_timer", 20))
        self.jump_state = 0
        self._dim_timer = int(settings.value("appearance/dim_timer", 100))
        self._off_timer = int(settings.value("appearance/off_timer", 300))
        self.lastuserinput = time.time()
        self.state = 'ACTIVE'  # Enum('ACTIVE','SLEEP','OFF')
        self._night = False

        self.possible_devs = dict()
        self.possible_devs['list'] = list()

        for key in self.inputs.keys():
            if key.startswith('dev/') and key.find('/', 4) == -1:
                self.possible_devs['list'].append(key)
                try:
                    self.possible_devs[key] = int(
                        settings.value("appearance/" + key, 1))
                except KeyError:
                    self.possible_devs[key] = 1
                if self.possible_devs[key] == 1:
                    inputs.entries[key]['interrupts'].append(self.interrupt)

    @Signal
    def dim_timer_changed(self):
        pass

    @Property(int, notify=dim_timer_changed)
    def dim_timer(self):
        return int(self._dim_timer)

    @dim_timer.setter
    def dim_timer(self, seconds):
        self._dim_timer = int(seconds)
        self.settings.setValue("appearance/dim_timer", seconds)

    @Signal
    def night_mode_start_changed(self):
        pass

    @Property(str, notify=night_mode_start_changed)
    def night_mode_start(self):
        return self._night_mode_start

    @night_mode_start.setter
    def night_mode_start(self, time_):
        self._night_mode_start = time_
        self.settings.setValue("appearance/night_mode_start", time_)

    @Signal
    def night_mode_end_changed(self):
        pass

    @Property(str, notify=night_mode_end_changed)
    def night_mode_end(self):
        return self._night_mode_end

    @night_mode_end.setter
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

    @Property(int, notify=jump_timer_changed)
    def jump_timer(self):
        return int(self._jump_timer)

    @jump_timer.setter
    def jump_timer(self, seconds):
        self._jump_timer = int(seconds)
        self.settings.setValue("appearance/jump_timer", seconds)

    @Signal
    def nightmodeChanged(self):
        self.check_nightmode()

    @Property(int, notify=nightmodeChanged)
    def night_mode(self):
        return self._night_mode

    @night_mode.setter
    def night_mode(self, value):
        self._night_mode = int(value)
        self.settings.setValue("appearance/night_mode", value)
        self.nightmodeChanged.emit()

    @Signal
    def off_timer_changed(self):
        pass

    @Property(int, notify=off_timer_changed)
    def off_timer(self):
        return int(self._off_timer)

    @off_timer.setter
    def off_timer(self, seconds):
        self._off_timer = int(seconds)
        self.settings.setValue("appearance/off_timer", seconds)

    @Signal
    def background_Night_Changed(self):
        pass

    @Property(bool, notify=background_Night_Changed)
    def background_night(self):
        return bool(self._background_night)

    @background_night.setter
    def background_night(self, min_):
        self._background_night = int(min_)
        self.settings.setValue("appearance/background_night", self._background_night)
        self.background_Night_Changed.emit()

    @Signal
    def rangeChanged(self):
        pass

    @Property(int, notify=rangeChanged)
    def minbacklight(self):
        return int(self._min_backlight)

    @minbacklight.setter
    def minbacklight(self, min_):
        self._min_backlight = int(min_)
        self.settings.setValue("appearance/min", self._min_backlight)
        self.rangeChanged.emit()

    @Property(int, notify=rangeChanged)
    def minbacklight_night(self):
        return int(self._min_backlight_night)

    @minbacklight_night.setter
    def minbacklight_night(self, min_):
        self._min_backlight_night = int(min_)
        self.settings.setValue("appearance/min_night", self._min_backlight_night)
        self.rangeChanged.emit()

    @Property(int, notify=rangeChanged)
    def maxbacklight(self):
        return int(self._max_backlight)

    @maxbacklight.setter
    def maxbacklight(self, max_):
        self._max_backlight = int(max_)
        self.rangeChanged.emit()
        self.settings.setValue("appearance/max", self._max_backlight)
        self.set_backlight(self._max_backlight)
        self.rangeChanged.emit()

    @Property(int, notify=rangeChanged)
    def maxbacklight_night(self):
        return int(self._max_backlight_night)

    @maxbacklight_night.setter
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
        if not NightModes.is_valid(self._night_mode):
            print('Unknown nightmode:', self._night_mode)
            return

        if self._night_mode in (NightModes.Off, NightModes.On):
            # Easy job
            if self._night != self._night_mode:
                self._night = bool(self._night_mode)
                self.nightChanged.emit()
            return

        if self._night_mode == NightModes.FromTimer_StartStopInput:
            return  # not yet supported

            # Read start/end from inputs
            if self._start_input_key not in self.inputs or self._stop_input_key not in self.inputs:
                # print('Missing start and/or stop for automatic nightmode. Resetting to FromTimer.')
                # self.night_mode = NightModes.FromTimer
                return

            start_input = self.inputs[self._start_input_key]
            stop_input = self.inputs[self._stop_input_key]

            if start_input['type'] != DataType.TIME or stop_input['type'] != DataType.TIME:
                # print('Unknown start/stop type. Resetting to FromTimer.')
                # self.night_mode = NightModes.FromTimer
                return

            start_str = start_input['value']
            stop_str = stop_input['value']

        else:  # self._night_mode == NightModes.FromTimer
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

        if start_time == stop_time:
            # Invalid config. Do nothing.
            return

        now_time = datetime.now().time()

        # Expect 18 - 23:00
        night_new = start_time < now_time < stop_time
        if start_time > stop_time:  # 18 - 23:00
            # Just invert
            night_new = not night_new

        if night_new != self._night:
            self._night = night_new
            self.nightChanged.emit()

    def update(self):
        self.check_nightmode()

        if self.state in ('SLEEP',) and self._off_timer > 0 and (self.lastuserinput + self._off_timer < time.time()):
            self.set_backlight(0)
            self.state = 'OFF'

        elif self.state in ('ACTIVE',) and self.lastuserinput + self._dim_timer < time.time():
            if self._night:
                self.set_backlight(self._min_backlight_night)
            else:
                self.set_backlight(self._min_backlight)
            self.state = 'SLEEP'

        elif self.state in ('SLEEP', 'OFF') and self._dim_timer > 0 and self.lastuserinput + self._dim_timer > time.time():
            if self._night:
                self.set_backlight(self._max_backlight_night)
            else:
                self.set_backlight(self._max_backlight)
            self.state = 'ACTIVE'

        if self.jump_state == 0 and self._jump_timer + self.lastuserinput < time.time():
            self.jump_state = 1
            self.jumpHome.emit()

    @Signal
    def jumpHome(self):
        pass

    def set_backlight(self, value):
        setthread = threading.Thread(target=self._set_backlight, args=(value,))
        setthread.start()

    def _set_backlight(self, value):
        value = int(value)
        if value != self.backlightlevel:
            if value < 1:
                self.inputs['backlight/brightness']['set'](0)

            elif value < 30:
                self.inputs['backlight/brightness']['set'](1)
                self._blackfilter = ((100 - (value * 3.3)) / 100)
                self.blackChanged.emit()

            elif value <= 100:
                self.inputs['backlight/brightness']['set'](
                    int(self.mapFromTo(value, 30, 100, 1, 100)))
                self._blackfilter = 0
                self.blackChanged.emit()

            self.backlightlevel = (value)

    def mapFromTo(self, x, a, b, c, d):
        y = (x-a)/(b-a)*(d-c)+c
        return y

    def interrupt(self, key, value):
        self.lastuserinput = time.time()
        self.jump_state = 0

        if self.state in ('OFF', 'SLEEP'):
            self.state = 'ACTIVE'
            self.set_backlight(self._max_backlight)

    @Signal
    def blackChanged(self):
        pass

    @Slot(str, int)
    def setDeviceTrack(self, path, value):
        value = int(value)
        if value != self.possible_devs[path]:
            self.possible_devs[path] = value
            self.settings.setValue("appearance/" + path, value)

            if self.possible_devs[path] == 1:
                self.inputs[path]['interrupts'].append(self.interrupt)

            else:
                i = 0
                for interrupt in self.inputs[path]['interrupts']:
                    if interrupt == self.interrupt:
                        self.inputs[path]['interrupts'].pop(i)
                    i += 1

    @Property(float, notify=blackChanged)
    def blackfilter(self):
        return self._blackfilter

    # Workaround for https://bugreports.qt.io/browse/PYSIDE-1426
    # @Property("QVariantMap", constant=True)
    def devices(self) -> dict:
        return dict(self.possible_devs)
    devices = Property("QVariantMap", devices, constant=True)
