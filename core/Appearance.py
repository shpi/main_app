# -*- coding: utf-8 -*-

from logging import getLogger
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from PySide2.QtCore import Signal, Slot, Property as QtProperty

from interfaces.DataTypes import DataType
from interfaces.PropertySystem import PropertyDict, QtPropLink, Property, IntervalProperty, TimeoutProperty, SelectProperty
from core.Settings import settings
from interfaces.Module import ModuleBase, ModuleCategories
from hardware.InputDevs import InputDeviceProperty


logger = getLogger(__name__)


NightModes = {
    0: "Off",
    1: "On",
    2: "Time range",
}


class Appearance(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = 'Appearance control'
    categories = ModuleCategories.UI, ModuleCategories._AUTOLOAD, ModuleCategories._INTERNAL

    rangeChanged = Signal()
    nightChanged = Signal()
    night_mode_changed = Signal()
    backlight_changed = Signal()
    jump_home_timer_changed = Signal()
    jump_home = Signal()
    background_night_changed = Signal()
    dim_timer_changed = Signal()
    off_timer_changed = Signal()
    night_mode_start_changed = Signal()
    night_mode_end_changed = Signal()
    night_mode_start_key_changed = Signal()
    night_mode_end_key_changed = Signal()
    input_activity_changed = Signal()
    display_state_changed = Signal()
    available_input_devices_changed = Signal()

    minbacklight = QtPropLink(int, path='min', notify=rangeChanged)
    maxbacklight = QtPropLink(int, path="max", notify=rangeChanged)
    minbacklight_night = QtPropLink(int, path='min_night', notify=rangeChanged)
    maxbacklight_night = QtPropLink(int, path='max_night', notify=rangeChanged)
    night_mode = QtPropLink(int, path='night_mode', notify=night_mode_changed)
    night = QtPropLink(bool, path='night_active', notify=nightChanged)
    backlightlevel = QtPropLink(int, path='brightness_out', notify=backlight_changed)
    blackfilter = QtPropLink(int, path='blackfilter', notify=backlight_changed)
    background_night = QtPropLink(bool, path='background_night', notify=background_night_changed)
    dim_timer = QtPropLink(int, path='dim_timer', notify=dim_timer_changed)
    off_timer = QtPropLink(int, path='off_timer', notify=off_timer_changed)
    night_mode_start = QtPropLink(str, path='night_mode_start', notify=night_mode_start_changed)
    night_mode_end = QtPropLink(str, path='night_mode_end', notify=night_mode_end_changed)
    night_mode_start_key = QtPropLink(str, path='night_mode_start_key', notify=night_mode_start_key_changed)
    night_mode_end_key = QtPropLink(str, path='night_mode_end_key', notify=night_mode_end_key_changed)
    jump_home_timer = QtPropLink(int, path='jump_home_timer', notify=jump_home_timer_changed)
    input_activity = QtPropLink(bool, path='input_activity', notify=input_activity_changed)
    display_state = QtPropLink(int, path='display_state', notify=display_state_changed)

    def _devices(self) -> List[str]:
        return self._all_input_devices
    devices = QtProperty('QVariantList', fget=_devices, notify=available_input_devices_changed)

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)
        self._pr_blackfilter = Property(DataType.INTEGER, 50., desc='Blackfilter', persistent=False)
        self._pr_brightness_out = Property(DataType.PERCENT_INT, 50, desc='Brightness control from Appearance', persistent=False)
        self._pr_dim_timer = TimeoutProperty(self._dim_timeout, 100., desc='Dim timer')
        self._pr_off_timer = TimeoutProperty(self._off_timeout, 300., desc='Off timer')
        self._pr_set_backlight = TimeoutProperty(self._set_backlight, 0., desc='Set backlight by other thread', persistent_timeout=False)
        self._pr_jump_home = TimeoutProperty(self._jump_home, 20., desc='Inactivity time to jump into home screen')
        self._pr_display_state = Property(DataType.INTEGER, 0, desc='State of display: Off, sleep, on', persistent=False)

        self.properties = PropertyDict(
            min=Property(DataType.PERCENT_INT, 60, desc='Backlight min'),
            max=Property(DataType.PERCENT_INT, 100, desc='Backlight max'),
            min_night=Property(DataType.PERCENT_INT, 30, desc='Backlight min in nightmode'),
            max_night=Property(DataType.PERCENT_INT, 100, desc='Backlight max in nightmode'),
            night_mode=Property(DataType.INTEGER, 2, valuepool=NightModes, desc='Night mode'),
            night_active=Property(DataType.BOOLEAN, False, desc='Nightmode is active', persistent=False),
            interval=IntervalProperty(self.update, default_interval=5., desc='Check interval for Appearance', persistent_interval=False),
            brightness_out=self._pr_brightness_out,
            blackfilter=self._pr_blackfilter,
            background_night=Property(DataType.BOOLEAN, True, desc='Background night'),
            dim_timer=self._pr_dim_timer,
            off_timer=self._pr_off_timer,
            night_mode_start=Property(DataType.TIME_STR, '20:00', desc='Start time of night mode'),
            night_mode_end=Property(DataType.TIME_STR, '06:00', desc='End time of night mode'),
            night_mode_start_key=SelectProperty(DataType.TIME_STR, desc='External start time of night mode'),
            night_mode_end_key=SelectProperty(DataType.TIME_STR, desc='External end time of night mode'),
            jump_home_timer=self._pr_jump_home,
            display_state=self._pr_display_state,
        )
        # self._epr_input_activity: Optional[Property] = None
        self._epr_lastinput: Optional[Property] = None
        self._epr_all_devices: Optional[Property] = None
        self._all_devices: List[str] = []

    def _update_blackfilter(self, pr_brightness: Property):
        # ToDo: Move into qml?
        brightness = pr_brightness.value

        if 0 < brightness < 30:
            self._pr_blackfilter.value = ((100 - (brightness * 3.3)) / 100)

        elif brightness <= 100:
            self._pr_blackfilter.value = 0

    def _updated_devices_list(self, pr_devlist: Property):
        self._all_devices[:] = (prop.path for prop in self._epr_all_devices.values())
        self.available_input_devices_changed.emit()

    def load(self):
        self._pr_brightness_out.events.subscribe(self._update_blackfilter, Property.UPDATED_AND_CHANGED)

        self._epr_lastinput = self.properties.root().get('InputDevs/lastinput')
        if self._epr_lastinput:
            self._epr_lastinput.events.subscribe(self._touched, Property.UPDATED_AND_CHANGED)

        self._epr_all_devices = self.properties.root().get('InputDevs/available_devices')
        if self._epr_all_devices:
            self._updated_devices_list(self._epr_all_devices)  # Read now if already populated
            self._epr_all_devices.events.subscribe(
                self._updated_devices_list, PropertyDict.CHANGED
            )  # If populated later

    def unload(self):
        pass

    def _inputdev_prop(self, prop_or_path: Union[Property, str]) -> Optional[InputDeviceProperty]:
        if type(prop_or_path) is str:
            prop_or_path = self.properties.root().get(prop_or_path)
            if prop_or_path is None:
                return None

        if isinstance(prop_or_path, InputDeviceProperty):
            return prop_or_path

        logger.error('Wrong property class found: %r. Expecting InputDeviceProperty', (prop_or_path, ))
        return None

    @Slot(str, result=str)
    def device_description(self, path: str) -> str:
        prop = self._inputdev_prop(path)
        return (prop and prop.desc) or 'No description'

    @Slot(str, result=bool)
    def is_device_selected(self, path) -> bool:
        prop = self._inputdev_prop(path)
        return (prop and prop.use_device) or False

    @Slot(str, bool)
    def set_device_selected(self, path, value):
        prop = self._inputdev_prop(path)
        if not prop:
            return
        prop.use_device = bool(value)

    @Slot(str)
    def delete_file(self, path):
        file = Path(path)
        if file.exists():
            file.unlink()

    @Signal
    def jump_timer_changed(self):
        pass

    def check_nightmode(self):
        status = 'OK'
        if not NightModes.is_valid(self._night_mode):
            logger.debug(f"unknown nightmode: {self._night_mode}")
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
                logger.debug('Missing start and/or stop for automatic nightmode. Resetting to FromTimer.')
                # self.night_mode = NightModes.FromTimer
                return 'ERROR'

            start_input = self.inputs[self._start_input_key]
            stop_input = self.inputs[self._stop_input_key]

            if start_input.type != DataType.TIME or stop_input.type != DataType.TIME:
                logger.debug('Unknown start/stop type. Resetting to FromTimer.')
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
        status = self.check_nightmode()

        if self.state in ('SLEEP',) and self._off_timer > 0 and (self.lastuserinput + self._off_timer < time.time()):
            logger.debug(f"changing nightmode to OFF, old state: {self.state}, lastinput: {self.lastuserinput}")
            self.set_backlight(0)
            self.state = 'OFF'

        elif self.state in ('ACTIVE',) and (self.lastuserinput + self._dim_timer < time.time()):
            logger.debug(f"changing nightmode to SLEEP, old state: {self.state}, lastinput: {self.lastuserinput}")
            if self._night:
                self.set_backlight(self._min_backlight_night)
            else:
                self.set_backlight(self._min_backlight)
            self.state = 'SLEEP'

        elif self.state in (
                'SLEEP', 'OFF') and self._dim_timer > 0 and self.lastuserinput + self._dim_timer > time.time():
            logger.debug(f"changing nightmode to ACTIVE, old state: {self.state}, lastinput: {self.lastuserinput}")
            if self._night:
                self.set_backlight(self._max_backlight_night)
            else:
                self.set_backlight(self._max_backlight)
            self.state = 'ACTIVE'

        if self._jump_state == 0 and self._jump_timer > 0 and self._jump_timer + self.lastuserinput < time.time():
            logger.debug(f"jump to home, timer: {self._jump_timer}, lastuserinput: {self.lastuserinput}")
            self._jump_state = 1
            self.jump_stateChanged.emit()

        return status

    @Property(int, notify=blackChanged)
    def backlightlevel(self):
        return int(self._backlightlevel)

    @Property(bool, notify=jump_stateChanged)
    def jump_state(self):
        return bool(self._jump_state)

    def set_backlight(self, value):
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
        # logger.debug(f"interrupt key: {key}, value: {value}")
        if self.state != 'ACTIVE' and value > 0:
            self.lastuserinput = time.time() - self._dim_timer
            if self.state == 'OFF':
                logger.debug(f"changing nightmode to SLEEP, old state: {self.state}, lastinput: {self.lastuserinput}")
                self.state = 'SLEEP'
                if self._night:
                    self.set_backlight(self._min_backlight_night)
                else:
                    self.set_backlight(self._min_backlight)

    def _touched(self, pr_last_touched: Property):
        # logger.debug(f"tinterrupt key: {key}, value: {value}")
        self.lastuserinput = time.time()
        self._jump_state = 0
        self.jump_stateChanged.emit()
        if self.state in ('OFF', 'SLEEP'):
            logger.debug(
                f"changing nightmode to ACTIVE, old state: {self.state}, lastinput: {self.lastuserinput}")
            self.state = 'ACTIVE'
            if self._night:
                self.set_backlight(self._max_backlight_night)
            else:
                self.set_backlight(self._max_backlight)
