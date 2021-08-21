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
from interfaces.PropertySystem import IntervalProperty, Property, Function, Input, Output
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
        self.mean_cpu_temp = MeanWindow(window_size=self.MEAN_COUNT)
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

        pr_temp_room = Property(Output, DataType.TEMPERATURE, 0.,
                                desc='Room temperature (stabilized)', persistent=False)
        self._set_roomtemp = pr_temp_room.get_setvalue_func()

        pr_temp = Property(
            Output, DataType.TEMPERATURE, 0., desc='Temperature of room or object'
        )
        self._set_temp = pr_temp.get_setvalue_func()

        pr_last_movement = Property(Output, DataType.TIMESTAMP, 0.,
                                    desc='Last movement detection by fast temperature change',
                                    persistent=False)
        self._set_last_movement = pr_last_movement.get_setvalue_func()

        self._pr_delta = Property(Input, DataType.TEMPERATURE, 1.5,
                                  desc='Temp difference to interrupt calculation of room temp (human detected)')
        self._delta_raw = 0.

        pr_human_detect = Property(Output, DataType.PRESENCE, False,
                                   desc='Detecting a human by significant temperature increase',
                                   persistent=False)
        self._set_human_detect = pr_human_detect.get_setvalue_func()

        self.properties.update(
            room_temperature=pr_temp_room,
            temperature=pr_temp,
            interval=self._pr_interval,
            last_movement=pr_last_movement,
            human_detect_delta=self._pr_delta,
            human_detected=pr_human_detect,
        )

        self._epr_fan_rpm: Optional[Property] = None

        self._epr_backlight_brightness: Optional[Property] = None
        self._epr_mlx_bufferlength: Optional[Property] = None
        self._epr_mlx_temp_object_scan_elements_enable: Optional[Property] = None
        self._epr_mlx_timestamp_scan_elements_enable: Optional[Property] = None
        self._epr_cputemp: Optional[Property] = None

        self._epr_human_detect: Optional[Property] = None
        self._announce_human_handler: Optional[PresenceHandlerSlot] = None
        self._presence_maininstance: Optional[Presence] = None

        self._object_temp_offset: Optional[float] = 0.
        self._object_temp_scale: Optional[float] = 1.

        self._sensor_temp_offset: Optional[float] = 0.
        self._sensor_temp_scale: Optional[float] = 1.
        self._devfile: Optional[Path] = None

    def _new_delta(self):
        # object_temp = (self.mean_object_temp_raw.mean + self._object_temp_offset) * self._object_temp_scale
        self._delta_raw = (self._pr_delta.value * 1000 / self._object_temp_scale)

    def load(self):
        self._epr_fan_rpm = self.properties.get('/HWMon/shpi/fan1_input')
        self._epr_backlight_brightness = self.properties.get('/Appearance/brightness')
        self._epr_mlx_bufferlength = self.properties.get('/IIO/mlx90615/buffer/length')
        self._epr_cputemp = self.properties.get('/CPU/cpu_temp')
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

    def calc_compensated_live_temp(self) -> float:
        object_temp = (self.mean_object_temp_raw.mean + self._object_temp_offset) * self._object_temp_scale
        sensor_temp = (self.mean_sensor_temp_raw.mean + self._sensor_temp_offset) * self._sensor_temp_scale

        logger.debug('object temperature mean: %s', object_temp)
        logger.debug('sensor temperature mean: %s', sensor_temp)

        if sensor_temp > object_temp:
            temp = object_temp - ((sensor_temp - object_temp) / 6)
            logger.debug('sensor self correction: %s', temp)
        else:
            temp = object_temp

        if self.mean_cpu_temp.mean and self.mean_cpu_temp.mean > sensor_temp:
            temp -= (self.mean_cpu_temp.mean - sensor_temp) / 60
            logger.debug('sensor cpu correction: %s', temp)

        if self.mean_fan_speed.mean and self.mean_fan_speed.mean < 1790:
            # temp -= 1000  todo: fan speed correction
            logger.debug('sensor fan correction: %s', temp)

        if self.mean_backlight_level.mean and self.mean_backlight_level.mean > 0:
            temp -= self.mean_backlight_level.mean * 3
            logger.debug('sensor backlight correction: %s', temp)

        return temp / 1000

    def update_means(self):
        if self._epr_cputemp:
            self.mean_cpu_temp.update(self._epr_cputemp.value)

        if self._epr_fan_rpm:
            self.mean_fan_speed.update(self._epr_fan_rpm.value)

        if self._epr_backlight_brightness:
            self.mean_backlight_level.update(self._epr_backlight_brightness.value)

        if self._epr_human_detect.value or self.mean_room_temp_raw.mean is None:
            # Human. Ignore live temp.
            # But if room temp changes rapidly without human interference update room mean raw into current object temp
            self.mean_room_temp_raw.update(self.mean_object_temp_raw.mean)
        else:
            # No human. Add live temp to room temp mean.
            self.mean_compensated_room_temp.update(self.calc_compensated_live_temp())

        self._set_roomtemp(self.mean_compensated_room_temp.mean or 0.)

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

                room_mean = self.mean_room_temp_raw.mean
                # print("mlx", tempobj, room_mean, self._delta_raw)
                if abs(tempobj - room_mean) > self._delta_raw:
                    # Fast temp change
                    # Human in front of sensor
                    self._set_last_movement(time.time())
                    self._set_human_detect(True)
                    self._announce_human_handler.trigger()
                else:
                    # No human

                    if self._announce_human_handler.is_triggered:
                        # Release trigger
                        self._set_human_detect(False)
                        self._announce_human_handler.untrigger()

                self.mean_object_temp_raw.update(tempobj)
                self.mean_sensor_temp_raw.update(tempamb)

                # Fast temperature
                self._set_temp(self.calc_compensated_live_temp())

            # while (time.time() - self.inputs.entries['core/input_dev/lasttouch'].last_update) < 5:
            #     logging.debug('halted mlx90615 thread due touch inputs')
            #     self.buffer_enable(0)
            #     time.sleep(6)
            #
            # self.buffer_enable(1)

        self.buffer_enable(False)
