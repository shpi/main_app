# -*- coding: utf-8 -*-

import struct
import time
from pathlib import Path
from typing import Optional
from logging import getLogger

# from ufunclab import minmax # https://github.com/WarrenWeckesser/ufunclab
# from core.CircularBuffer import CircularBuffer
from interfaces.DataTypes import DataType
from interfaces.Module import ThreadModuleBase
from interfaces.PropertySystem import FunctionProperty, IntervalProperty, Property
from core.Settings import settings
from core.Toolbox import MeanWindow
from modules.CPU import CPU
from modules.IIO import IIO
from modules.HWMon import HWMon
from modules.InputDevs import InputDevs
from modules.Appearance import Appearance
from modules.Presence import Presence, PresenceHandlerSlot

logger = getLogger(__name__)


class MLX90615(ThreadModuleBase):  # Non Thread?
    allow_maininstance = True
    allow_instances = False
    description = "MLX90615 temperature sensor"
    categories = 'Sensors', 'Temperature', 'Hardware'
    depends_on = Appearance, IIO, CPU, HWMon, InputDevs, Presence

    # TEMP_RANGE_MIN = 0.1
    # TEMP_RANGE_MAX = 45.
    iio_buffer_length = 100
    MEAN_COUNT = 10

    @classmethod
    def available(cls) -> bool:
        if not super().available():
            return False

        found = tuple(IIO.iio_find_device_paths(name_match='mlx90615'))
        return bool(found)

    def __init__(self, parent, instancename: str = None):
        ThreadModuleBase.__init__(self, parent=parent, instancename=instancename)

        self.mean_backlight_level = MeanWindow(window_size=self.MEAN_COUNT)
        self.mean_cpu_temp = MeanWindow(window_size=self.MEAN_COUNT, func=CPU.get_cpu_temp)
        self.mean_fan_speed = MeanWindow(1900., window_size=self.MEAN_COUNT)

        # Updated often in run(), used in calc_compensated_temp()
        self.mean_sensor_temp_raw = MeanWindow(window_size=self.MEAN_COUNT)

        # Updated often in run(), used in calc_compensated_temp()
        self.mean_object_temp_raw = MeanWindow(window_size=self.MEAN_COUNT)

        # Updated often in run(), used in calc_compensated_temp()
        self.mean_room_temp_raw = MeanWindow(window_size=self.MEAN_COUNT)

        # Updated fewer by interval, used in calc_compensated_temp()
        self.mean_compensated_room_temp = MeanWindow(window_size=self.MEAN_COUNT)

        self._pr_interval = IntervalProperty(self.update_means, 10., desc='Interval of calculating mean values')

        self._pr_temp_room = FunctionProperty(
            datatype=DataType.TEMPERATURE,
            getterfunc=self._get_room_temp,
            maxage=1.,
            desc='Room temperature (stabilized)'
        )

        self._pr_temp = FunctionProperty(
            datatype=DataType.TEMPERATURE,
            getterfunc=self.calc_compensated_temp,
            maxage=1.,
            desc='Temperature of room or object'
        )

        self._pr_last_movement = Property(datatype=DataType.TIMESTAMP,
                                          initial_value=0.,
                                          desc='Last movement detection by fast temperature change',
                                          persistent=False)

        self._pr_delta = Property(datatype=DataType.TEMPERATURE,
                                  initial_value=3.,
                                  desc='Temp difference to interrupt calculation of room temp (human detected)')
        self._delta_raw = 0.

        self._pr_human_detect = Property(datatype=DataType.PRESENCE,
                                         initial_value=False,
                                         desc='Detecting a human by significant temperature increase',
                                         persistent=False)

        self.properties.update(
            room_temperature=self._pr_temp_room,
            temperature=self._pr_temp,
            interval=self._pr_interval,
            last_movement=self._pr_last_movement,
            human_detect_delta=self._pr_delta,
            human_detected=self._pr_human_detect,
        )

        self._epr_fan_rpm: Optional[Property] = None

        self._epr_backlight_brightness: Optional[Property] = None
        self._epr_mlx_bufferlength: Optional[Property] = None
        self._epr_mlx_temp_object_scan_elements_enable: Optional[Property] = None
        self._epr_mlx_timestamp_scan_elements_enable: Optional[Property] = None

        self._epr_human_detect: Optional[Property] = None
        self._announce_human_handler: Optional[PresenceHandlerSlot] = None
        self._presence_maininstance: Optional[Presence] = None

        self._object_temp_offset: Optional[float] = 0.
        self._object_temp_scale: Optional[float] = 1.

        self._sensor_temp_offset: Optional[float] = 0.
        self._sensor_temp_scale: Optional[float] = 1.
        self._devfile: Optional[Path] = None

    def _new_delta(self):
        self._delta_raw = self._pr_delta.value / self._object_temp_scale

    def load(self):
        self._epr_fan_rpm = self.properties.get('/HWMon/shpi/pwm1')
        self._epr_backlight_brightness = self.properties.get('/Appearance/brightness_out')
        self._epr_mlx_bufferlength = self.properties.get('/IIO/mlx90615/buffer/length')

        self._epr_mlx_temp_object_scan_elements_enable = self.properties.get('/IIO/mlx90615/channels/temp_object/scan_elements_enable')
        self._epr_mlx_timestamp_scan_elements_enable = self.properties.get('/IIO/mlx90615/channels/timestamp/scan_elements_enable')

        self._epr_human_detect = self.properties.get('/Presence/detecting_human')

        self._object_temp_offset = self.properties.get('/IIO/mlx90615/channels/temp_object/offset').value
        self._object_temp_scale = self.properties.get('/IIO/mlx90615/channels/temp_object/scale').value
        self._sensor_temp_offset = self.properties.get('/IIO/mlx90615/channels/temp_ambient/offset').value
        self._sensor_temp_scale = self.properties.get('/IIO/mlx90615/channels/temp_ambient/scale').value

        self._pr_delta.events.subscribe(self._new_delta, Property.UPDATED)
        self._new_delta()

        self._devfile = Path(self.properties.get('/IIO/mlx90615/rawdevice').value)

        self._presence_maininstance: Presence = Presence.instances().get(None)
        if self._presence_maininstance:
            self._announce_human_handler \
                = self._presence_maininstance.register_handler(self.__class__, 'rapid_temp_increase', 60.)

    def unload(self):
        if self._presence_maininstance and self._announce_human_handler:
            self._presence_maininstance.unregister_handler(self._announce_human_handler)
        self._announce_human_handler = None

    def stop(self):
        pass

    def calc_compensated_temp(self) -> float:
        object_temp = (self.mean_object_temp_raw.mean + self._object_temp_offset) * self._object_temp_scale
        sensor_temp = (self.mean_sensor_temp_raw.mean + self._sensor_temp_offset) * self._sensor_temp_scale

        logger.debug('object temperature mean: %s', object_temp)
        logger.debug('sensor temperature mean: %s', sensor_temp)

        if sensor_temp > object_temp:
            temp = object_temp - ((sensor_temp - object_temp) / 6)
            logger.debug('sensor self correction: %s', temp)
        else:
            temp = object_temp

        if self.mean_cpu_temp.mean > sensor_temp:
            temp -= (self.mean_cpu_temp.mean - sensor_temp) / 60
            logger.debug('sensor cpu correction: %s', temp)

        if self.mean_fan_speed.mean < 1790:
            # temp -= 1000  todo: fan speed correction
            logger.debug('sensor fan correction: %s', temp)

        if self.mean_backlight_level.mean > 0:
            temp -= self.mean_backlight_level.mean * 3
            logger.debug('sensor backlight correction: %s', temp)

        return temp / 1000

    def update_means(self):
        self.mean_cpu_temp.update()
        self.mean_fan_speed.update(self._epr_fan_rpm.value)
        self.mean_backlight_level.update(self._epr_backlight_brightness.value)
        if not self._epr_human_detect.value:
            self.mean_compensated_room_temp.update(self.calc_compensated_temp())

        # If room temp changes rapidly without human interference update mean into current object temp
        self.mean_room_temp_raw.update(self.mean_object_temp_raw.mean)

    def buffer_enable(self, value: bool):
        try:
            self._epr_mlx_bufferlength.value = self.iio_buffer_length if value else 0
        except Exception as e:
            logger.error('Could not set buffer_enable to %s: %s', value, repr(e))

    def activate_channel(self):
        for channel in self._epr_mlx_temp_object_scan_elements_enable, self._epr_mlx_timestamp_scan_elements_enable:
            try:
                channel.value = True
            except Exception as e:
                logger.error('Could not activate channel %s: %s' + repr(channel), repr(e))

    def _get_room_temp(self) -> float:
        return self.mean_compensated_room_temp.mean or 0.

    def run(self):
        self.buffer_enable(False)
        self.activate_channel()
        self.buffer_enable(True)

        with self._devfile.open('rb') as devfile:
            line = devfile.read(16)
            (tempobj, tempamb, _, timestamp) = struct.unpack('<HHiq', line)

            # pre initialize to get an early mean value
            self.mean_object_temp_raw.update(tempobj)
            self.mean_sensor_temp_raw.update(tempamb)
            self.update_means()

            while self.module_is_running():
                line = devfile.read(16)
                (tempobj, tempamb, _, timestamp) = struct.unpack('<HHiq', line)

                if tempobj > self.mean_room_temp_raw.mean + self._delta_raw:
                    # Human in front of sensor
                    self._pr_last_movement.value = time.time()
                    self._pr_human_detect.value = True
                    self._announce_human_handler.trigger()
                else:
                    # No human
                    self.mean_room_temp_raw.update(tempobj)

                    if self._announce_human_handler.is_triggered:
                        # Release trigger
                        self._pr_human_detect.value = False
                        self._announce_human_handler.untrigger()

                self.mean_object_temp_raw.update(tempobj)
                self.mean_sensor_temp_raw.update(tempamb)

        self.buffer_enable(False)
