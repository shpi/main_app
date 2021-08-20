# -*- coding: utf-8 -*-

from logging import getLogger
from datetime import datetime, time
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
from enum import Enum

from PySide2.QtCore import Signal, Slot, Property as QtProperty

from interfaces.DataTypes import DataType
from interfaces.PropertySystem import PropertyDict, QtPropLink, Property, IntervalProperty, TimeoutProperty, \
    QtPropLinkEnum, QtPropLinkSelect, Input, Output
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
    display_state_changed = Signal()
    available_input_devices_changed = Signal()

    minbacklight = QtPropLink(int, path='min', notify=range_changed)
    maxbacklight = QtPropLink(int, path="max", notify=range_changed)
    minbacklight_night = QtPropLink(int, path='min_night', notify=range_changed)
    maxbacklight_night = QtPropLink(int, path='max_night', notify=range_changed)
    night_mode = QtPropLinkEnum(str, path='night_mode', notify=night_mode_changed)
    dim_timer = QtPropLink(int, path='dim_timer', notify=dim_timer_changed)
    off_timer = QtPropLink(int, path='off_timer', notify=off_timer_changed)
    night_mode_start = QtPropLink(str, path='night_mode_start', notify=night_mode_start_changed)
    night_mode_end = QtPropLink(str, path='night_mode_end', notify=night_mode_end_changed)
    night_mode_start_select = QtPropLinkSelect(str, path='night_mode_start_select', notify=night_mode_start_select_changed)
    night_mode_end_select = QtPropLinkSelect(str, path='night_mode_end_select', notify=night_mode_end_select_changed)
    jump_home_timer = QtPropLink(int, path='jump_home_timer', notify=jump_home_timer_changed)
    display_state = QtPropLinkEnum(str, path='display_state', notify=display_state_changed)
    night_active = QtPropLink(bool, path='night_active', notify=night_changed)
    backlightlevel = QtPropLink(int, path='brightness', notify=backlight_changed)
    blackfilter = QtPropLink(float, path='blackfilter', notify=backlight_changed)
    background_night = QtPropLink(bool, path='background_night', notify=background_night_changed)

    def _devices(self) -> List[str]:
        return list(self._epd_all_devices.paths()) if self._epd_all_devices else []
    devices = QtProperty('QVariantList', fget=_devices, notify=available_input_devices_changed)

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)

        # Inputs
        self._pr_min = Property(Input, DataType.PERCENT_INT, 60, desc='Backlight min')
        self._pr_max = Property(Input, DataType.PERCENT_INT, 100, desc='Backlight max')
        self._pr_min_night = Property(Input, DataType.PERCENT_INT, 30, desc='Backlight min during nightmode')
        self._pr_max_night = Property(Input, DataType.PERCENT_INT, 100, desc='Backlight max during nightmode')
        self._pr_night_mode = Property(Input, DataType.ENUM, NightModes.FixTimeRange, desc='Night mode')
        self._pr_night_mode_start_select = Property(Input, DataType.TIME, desc='External start time of night mode')
        self._pr_night_mode_end_select = Property(Input, DataType.TIME, desc='External end time of night mode')
        self._pr_night_mode_start = Property(Input, DataType.TIME, time(20, 0), desc='Start time of night mode')
        self._pr_night_mode_end = Property(Input, DataType.TIME, time(6, 0), desc='End time of night mode')

        self._pr_dim_timer = TimeoutProperty(self._dim_timeout, 100., desc='Display dim timeout')
        self._pr_off_timer = TimeoutProperty(self._off_timeout, 300., desc='Display off timeout')
        self._pr_jump_home_timer = TimeoutProperty(self._jump_home, 10., desc='Inactivity time to jump into home screen')

        # Outputs
        self._pr_display_state_out = Property(Output, DataType.ENUM, DisplayStates.On, desc='Current state of display', persistent=False)
        self._set_display_state = self._pr_display_state_out.get_setvalue_func()

        self._pr_brightness_out = Property(Output, DataType.PERCENT_INT, 50, desc='Brightness control from Appearance', persistent=False)
        self._set_brightness = self._pr_brightness_out.get_setvalue_func()

        pr_blackfilter_out = Property(Output, DataType.FLOAT, 0.5, desc='Blackfilter factor', persistent=False)
        self._set_blackfilter = pr_blackfilter_out.get_setvalue_func()

        self._pr_night_active_out = Property(Output, DataType.BOOLEAN, False, desc='Nightmode is active', persistent=False)
        self._set_night_active = self._pr_night_active_out.get_setvalue_func()

        self.properties.update(
            min=self._pr_min,
            max=self._pr_max,
            min_night=self._pr_min_night,
            max_night=self._pr_max_night,
            night_mode=self._pr_night_mode,
            interval=IntervalProperty(self.update, default_interval=5., desc='Check interval for Appearance module'),
            background_night=Property(Input, DataType.BOOLEAN, True, desc='Use background in nightmode'),
            dim_timer=self._pr_dim_timer,
            off_timer=self._pr_off_timer,
            night_mode_start=self._pr_night_mode_start,
            night_mode_end=self._pr_night_mode_end,
            night_mode_start_select=self._pr_night_mode_start_select,
            night_mode_end_select=self._pr_night_mode_end_select,
            jump_home_timer=self._pr_jump_home_timer,

            display_state=self._pr_display_state_out,
            brightness=self._pr_brightness_out,
            blackfilter=pr_blackfilter_out,
            night_active=self._pr_night_active_out,
        )

        self._epr_lasttouch: Optional[Property] = None
        self._epr_lastinput: Optional[Property] = None
        self._epd_all_devices: Optional[PropertyDict] = None

    def qml_context_properties(self) -> Optional[Dict[str, Any]]:
        return {'appearance': self}

    def update(self):
        self._check_night_active()

    def _dim_timeout(self):
        if self._pr_display_state_out.value == DisplayStates.On:
            self._set_display_state(DisplayStates.Dim)

    def _off_timeout(self):
        if self._pr_display_state_out.value != DisplayStates.Sleep:
            self._set_display_state(DisplayStates.Sleep)

    def load(self):
        # min/max slider changes
        self._pr_min.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)
        self._pr_max.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)
        self._pr_min_night.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)
        self._pr_max_night.events.subscribe(self._check_backlight, Property.UPDATED_AND_CHANGED)

        # Time ranges change
        self._pr_night_mode_start_select.events.subscribe(self._check_night_active, Property.UPDATED_AND_CHANGED)
        self._pr_night_mode_end_select.events.subscribe(self._check_night_active, Property.UPDATED_AND_CHANGED)
        self._pr_night_mode_start.events.subscribe(self._check_night_active, Property.UPDATED_AND_CHANGED)
        self._pr_night_mode_end.events.subscribe(self._check_night_active, Property.UPDATED_AND_CHANGED)

        # Track touches for sleep/off mode
        self._epr_lasttouch = self.properties.root().get('InputDevs/last_touch')
        if self._epr_lasttouch:
            self._epr_lasttouch.events.subscribe(self._touched, Property.UPDATED_AND_CHANGED)

        self._epr_lastinput = self.properties.root().get('InputDevs/last_input')
        if self._epr_lastinput:
            self._epr_lastinput.events.subscribe(self._touched, Property.UPDATED_AND_CHANGED)

        # Available devices access
        alldevs = self.properties.root().get('InputDevs/available_devices')
        if alldevs is not None:
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
        self._pr_night_active_out.events.subscribe(self._night_changed, Property.UPDATED)  # _AND_CHANGED

        # Start timers
        self._pr_dim_timer.restart()
        self._pr_off_timer.restart()
        self._pr_jump_home_timer.restart()

    def _night_changed(self):
        self.night_changed.emit()
        self._check_backlight()

    def _jump_home(self):
        print("jumping home now")
        self.jump_home.emit()

    def _touched(self):
        self._set_display_state(DisplayStates.On)
        # Restart timers
        self._pr_dim_timer.restart()
        self._pr_off_timer.restart()
        self._pr_jump_home_timer.restart()

    def unload(self):
        if self._epr_lasttouch is not None:
            self._epr_lasttouch.events.unsubscribe(self._touched, Property.UPDATED_AND_CHANGED)

        if self._epr_lastinput is not None:
            self._epr_lastinput.events.unsubscribe(self._touched, Property.UPDATED_AND_CHANGED)

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

        if night_mode in {NightModes.Off, NightModes.On}:
            # Easy job
            self._set_night_active(night_mode is NightModes.On)
            return

        if night_mode is NightModes.DynamicTimeRange:
            # Read start/end from inputs

            if not self._pr_night_mode_start_select.is_linked or not self._pr_night_mode_end_select.is_linked:
                # No inputs selected
                return

            start_time = self._pr_night_mode_start_select.value
            end_time = self._pr_night_mode_end_select.value

        elif night_mode is NightModes.FixTimeRange:
            # Read start/stop from static values
            start_time = self._pr_night_mode_start.value
            end_time = self._pr_night_mode_end.value

        else:
            logger.error('Unknown NightMode: %s', night_mode)
            return

        # Working with pure times.
        if start_time == end_time:
            # Invalid config. Do nothing.
            return

        now_time = datetime.now().time()
        night_new = in_timerange(start_time, end_time, now_time)
        self._set_night_active(night_new)

    def _check_backlight(self):
        # Called by: min/max changes, night_changed, displaystate changes

        displaystate = self._pr_display_state_out.value

        if displaystate is DisplayStates.Sleep:
            self._set_brightness(0)

        elif displaystate is DisplayStates.Dim:
            # Dim
            if self._pr_night_active_out.value:
                # night value
                self._set_brightness(self._pr_min_night.value)
            else:
                # day value
                self._set_brightness(self._pr_min.value)

        elif displaystate is DisplayStates.On:
            # Normal brighness
            if self._pr_night_active_out.value:
                # night value
                self._set_brightness(self._pr_max_night.value)
            else:
                # day value
                self._set_brightness(self._pr_max.value)

        else:
            logger.warning('Unknown displaystate: %s', displaystate)

        # Calculate blackfilter
        brightness = self._pr_brightness_out.value

        if 0 < brightness < 30:
            self._set_blackfilter((100 - (brightness * 3.3)) / 100)

        elif brightness <= 100:
            self._set_blackfilter(0.)

        self.backlight_changed.emit()


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
