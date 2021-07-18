# -*- coding: utf-8 -*-

from logging import getLogger
from datetime import datetime, time
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
from enum import Enum

from PySide2.QtCore import Signal, Slot, Property as QtProperty

from interfaces.DataTypes import DataType
from interfaces.PropertySystem import PropertyDict, QtPropLink, Property, IntervalProperty, TimeoutProperty, \
    SelectProperty, QtPropLinkEnum, QtPropLinkSelect, ModuleInstancePropertyDict
from interfaces.Module import ModuleBase
from modules.InputDevs import InputDeviceProperty, InputDevs


logger = getLogger(__name__)


class NightModes(Enum):
    Off = "Always off"
    On = "Always On"
    FixTimeRange = "Fix time range"
    DynamicTimeRange = "Dynamic time range"


class DisplayStates(Enum):
    On = "On"
    Dim = "Dimmed"
    Sleep = "Sleep"


def in_timerange(start_time: time, stop_time: time, now_time: time) -> bool:
    if start_time < stop_time:
        # 18:00 - 23:00
        return start_time <= now_time < stop_time
    else:
        # 23:00 - 8:00
        return not (stop_time <= now_time < start_time)


class Appearance(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = 'Appearance control'
    categories = ()
    depends_on = InputDevs,

    range_changed = Signal()
    night_changed = Signal()
    night_mode_changed = Signal()
    backlight_changed = Signal()
    jump_home_timer_changed = Signal()
    jump_home = Signal()
    background_night_changed = Signal()
    dim_timer_changed = Signal()
    off_timer_changed = Signal()
    night_mode_start_changed = Signal()
    night_mode_end_changed = Signal()
    night_mode_start_select_changed = Signal()
    night_mode_end_select_changed = Signal()
    # input_activity_changed = Signal()
    display_state_changed = Signal()
    available_input_devices_changed = Signal()

    minbacklight = QtPropLink(int, path='min', notify=range_changed)
    maxbacklight = QtPropLink(int, path="max", notify=range_changed)
    minbacklight_night = QtPropLink(int, path='min_night', notify=range_changed)
    maxbacklight_night = QtPropLink(int, path='max_night', notify=range_changed)
    night_mode = QtPropLinkEnum(str, path='night_mode', notify=night_mode_changed)
    night_active = QtPropLink(bool, path='night_active', notify=night_changed)
    backlightlevel = QtPropLink(int, path='brightness_out', notify=backlight_changed)
    blackfilter = QtPropLink(int, path='blackfilter', notify=backlight_changed)
    background_night = QtPropLink(bool, path='background_night', notify=background_night_changed)
    dim_timer = QtPropLink(int, path='dim_timer', notify=dim_timer_changed)
    off_timer = QtPropLink(int, path='off_timer', notify=off_timer_changed)
    night_mode_start = QtPropLink(str, path='night_mode_start', notify=night_mode_start_changed)
    night_mode_end = QtPropLink(str, path='night_mode_end', notify=night_mode_end_changed)
    night_mode_start_select = QtPropLinkSelect(str, path='night_mode_start_select', notify=night_mode_start_select_changed)
    night_mode_end_select = QtPropLinkSelect(str, path='night_mode_end_select', notify=night_mode_end_select_changed)
    jump_home_timer = QtPropLink(int, path='jump_home_timer', notify=jump_home_timer_changed)
    # input_activity = QtPropLink(bool, path='input_activity', notify=input_activity_changed)
    display_state = QtPropLink(int, path='display_state', notify=display_state_changed)

    def _devices(self) -> List[str]:
        return list(self._epd_all_devices.paths()) if self._epd_all_devices else []
    devices = QtProperty('QVariantList', fget=_devices, notify=available_input_devices_changed)

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)
        self._pr_min = Property(DataType.PERCENT_INT, 60, desc='Backlight min')
        self._pr_max = Property(DataType.PERCENT_INT, 100, desc='Backlight max')
        self._pr_min_night = Property(DataType.PERCENT_INT, 30, desc='Backlight min during nightmode')
        self._pr_max_night = Property(DataType.PERCENT_INT, 100, desc='Backlight max during nightmode')
        self._pr_blackfilter = Property(DataType.INTEGER, 50., desc='Blackfilter', persistent=False)
        self._pr_brightness_out = Property(DataType.PERCENT_INT, 50, desc='Brightness control from Appearance', persistent=False)
        self._pr_dim_timer = TimeoutProperty(self._dim_timeout, 100., desc='Display dim timeout')
        self._pr_off_timer = TimeoutProperty(self._off_timeout, 300., desc='Display off timeout')
        self._pr_jump_home_timer = TimeoutProperty(self._jump_home, 20., desc='Inactivity time to jump into home screen')
        self._pr_display_state = Property(DataType.ENUM, DisplayStates.On, desc='Current state of display', persistent=False)
        self._pr_night_active = Property(DataType.BOOLEAN, False, desc='Nightmode is active', persistent=False)
        self._pr_night_mode = Property(DataType.ENUM, NightModes.FixTimeRange, desc='Night mode')
        self._pr_night_mode_start_select = SelectProperty(DataType.TIME_STR, desc='External start time of night mode')
        self._pr_night_mode_end_select = SelectProperty(DataType.TIME_STR, desc='External end time of night mode')
        self._pr_night_mode_start = Property(DataType.TIME_STR, '20:00', desc='Start time of night mode')
        self._pr_night_mode_end = Property(DataType.TIME_STR, '06:00', desc='End time of night mode')

        self.properties = ModuleInstancePropertyDict(
            min=self._pr_min,
            max=self._pr_max,
            min_night=self._pr_min_night,
            max_night=self._pr_max_night,
            night_mode=self._pr_night_mode,
            night_active=self._pr_night_active,
            interval=IntervalProperty(self.update, default_interval=5., desc='Check interval for Appearance', persistent_interval=False),
            brightness_out=self._pr_brightness_out,
            blackfilter=self._pr_blackfilter,
            background_night=Property(DataType.BOOLEAN, True, desc='Background night'),
            dim_timer=self._pr_dim_timer,
            off_timer=self._pr_off_timer,
            night_mode_start=self._pr_night_mode_start,
            night_mode_end=self._pr_night_mode_end,
            night_mode_start_select=self._pr_night_mode_start_select,
            night_mode_end_select=self._pr_night_mode_end_select,
            jump_home_timer=self._pr_jump_home_timer,
            display_state=self._pr_display_state,
        )

        self._epr_lasttouch: Optional[Property] = None
        self._epd_all_devices: Optional[PropertyDict] = None

    def qml_context_properties(self) -> Optional[Dict[str, Any]]:
        return {'appearance': self}

    def _dim_timeout(self):
        if self._pr_display_state.value == DisplayStates.On:
            self._pr_display_state.value = DisplayStates.Dim

    def _off_timeout(self):
        if self._pr_display_state.value != DisplayStates.Sleep:
            self._pr_display_state.value = DisplayStates.Sleep

    def _update_blackfilter(self, pr_brightness: Property):
        # ToDo: Move into qml?
        brightness = pr_brightness.value

        if 0 < brightness < 30:
            self._pr_blackfilter.value = ((100 - (brightness * 3.3)) / 100)

        elif brightness <= 100:
            self._pr_blackfilter.value = 0

    def load(self):
        # Couple brightness to blackfilter
        self._pr_brightness_out.events.subscribe(self._update_blackfilter, Property.UPDATED_AND_CHANGED)

        self._pr_night_mode.events.subscribe(self._check_night_active, Property.UPDATED_AND_CHANGED)
        self._pr_display_state.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)

        # min/max slider changes
        self._pr_min.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)
        self._pr_max.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)
        self._pr_min_night.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)
        self._pr_max_night.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)

        # Time ranges change
        self._pr_night_mode_start_select.events.subscribe(self._check_night_active, SelectProperty.UPDATED_AND_CHANGED)
        self._pr_night_mode_end_select.events.subscribe(self._check_night_active, SelectProperty.UPDATED_AND_CHANGED)
        self._pr_night_mode_start.events.subscribe(self._check_night_active, Property.UPDATED_AND_CHANGED)
        self._pr_night_mode_end.events.subscribe(self._check_night_active, Property.UPDATED_AND_CHANGED)

        # Track touches for sleep/off mode
        self._epr_lasttouch = self.properties.root().get('InputDevs/last_touch')
        if self._epr_lasttouch:
            self._epr_lasttouch.events.subscribe(self._touched, Property.UPDATED_AND_CHANGED)

        # self._epr_lastinput = self.properties.root().get('InputDevs/last_input')
        # if self._epr_lastinput:
        #    self._epr_lastinput.events.subscribe(self._touched, Property.UPDATED_AND_CHANGED)

        # Available devices access
        alldevs = self.properties.root().get('InputDevs/available_devices')
        if alldevs:
            self._epd_all_devices: PropertyDict = alldevs.value
            # Tell qml about available inputdev changes
            try:
                pass
                # todo: alldevs.events.subscribe(lambda: self.available_input_devices_changed.emit(), PropertyDict.CHANGED)
            except Exception as e:
                ev = self.available_input_devices_changed.emit
                logger.error('Could not subscribe available_input_devices_changed: %s', repr(e), exc_info=True)
                print("ev:", ev, type(ev))  # todo: remove

            # Trigger reload
            self.available_input_devices_changed.emit()

        # night cycle changes
        self._pr_night_active.events.subscribe(self._night_changed, Property.UPDATED_AND_CHANGED)

        # Start timers
        self._pr_dim_timer.restart()
        self._pr_off_timer.restart()
        self._pr_jump_home_timer.restart()

    def _night_changed(self):
        self.night_changed.emit()
        self._check_backlight()

    def _jump_home(self):
        pass

    def _touched(self):
        self._pr_display_state = DisplayStates.On
        # Restart timers
        self._pr_dim_timer.restart()
        self._pr_off_timer.restart()
        self._pr_jump_home_timer.restart()

    def unload(self):
        pass

    def _inputdev_prop(self, prop_or_path: Union[Property, str]) -> Optional[InputDeviceProperty]:
        # Get InputDeviceProperty from path or check given property to be an InputDeviceProperty
        if type(prop_or_path) is str:
            prop_or_path = self.properties.root().get(prop_or_path)
            if prop_or_path is None:
                return None

        if isinstance(prop_or_path, InputDeviceProperty):
            return prop_or_path

        logger.error('Wrong property class found: %r. Expecting InputDeviceProperty', prop_or_path)
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

    def _check_night_active(self):
        # Called by: night_mode_changed, start/end ranges, update()

        night_mode = self._pr_night_mode.value

        if night_mode in (NightModes.Off, NightModes.On):
            # Easy job
            self._pr_night_active.value = night_mode is NightModes.On
            return

        if night_mode is NightModes.DynamicTimeRange:
            # Read start/end from inputs

            if not self._pr_night_mode_start_select.is_selected or not self._pr_night_mode_end_select.is_selected:
                # No inputs selected
                return

            start_str = self._pr_night_mode_start_select.value
            end_str = self._pr_night_mode_end_select.value

        elif night_mode is NightModes.FixTimeRange:
            # Read start/stop from static values
            start_str = self._pr_night_mode_start.value
            end_str = self._pr_night_mode_end.value

        else:
            logger.error('Unknown NightMode: %s', night_mode)
            return

        # Working with pure times.
        try:
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
        except ValueError:
            # Some time is formatted badly
            start_time = time(0, 0)
            end_time = time(0, 0)

        if start_time == end_time:
            # Invalid config. Do nothing.
            return

        now_time = datetime.now().time()
        night_new = in_timerange(start_time, end_time, now_time)
        self._pr_night_active.value = night_new

    def _check_backlight(self):
        # Called by: min/max changes, night_changed, displaystate changes

        displaystate = self._pr_display_state.value

        if displaystate is DisplayStates.Sleep:
            self._pr_brightness_out.value = 0

        elif displaystate is DisplayStates.Dim:
            # Dim
            if self._pr_night_active.value:
                # night value
                self._pr_brightness_out.value = self._pr_min_night.value
            else:
                # day value
                self._pr_brightness_out.value = self._pr_min.value

        elif displaystate is DisplayStates.On:
            # Normal brighness
            if self._pr_night_active.value:
                # night value
                self._pr_brightness_out.value = self._pr_max_night.value
            else:
                # day value
                self._pr_brightness_out.value = self._pr_max.value

        else:
            logger.warning('Unknown displaystate: %s', displaystate)

    def update(self):
        self._check_night_active()


def _test_timerange():
    # Simple 8-22
    t1 = time(8, 0)
    t2 = time(22, 0)

    assert in_timerange(t1, t2, time(7, 0)) is False
    assert in_timerange(t1, t2, time(8, 0)) is True
    assert in_timerange(t1, t2, time(9, 0)) is True
    assert in_timerange(t1, t2, time(22, 0)) is False
    assert in_timerange(t1, t2, time(23, 0)) is False

    # Over night 22-6
    t1 = time(22, 0)
    t2 = time(6, 0)

    assert in_timerange(t1, t2, time(21, 0)) is False
    assert in_timerange(t1, t2, time(22, 0)) is True
    assert in_timerange(t1, t2, time(23, 0)) is True
    assert in_timerange(t1, t2, time(1, 0)) is True
    assert in_timerange(t1, t2, time(6, 0)) is False
    assert in_timerange(t1, t2, time(7, 0)) is False
