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
        found = tuple(IIO.iio_find_device_paths(name_match='mlx90615'))
        return bool(found)

    def __init__(self, parent, instancename: str = None):
        ThreadModuleBase.__init__(self, parent=parent, instancename=instancename)

        self._fan_path = settings.str('mlx/fan_path', 'sensor/shpi/fan1_input')  # todo as property

        self.backlight_level_mean = MeanWindow(window_size=self.MEAN_COUNT)
        self.sensor_temp_mean = MeanWindow(window_size=self.MEAN_COUNT)
        self.object_temp_mean = MeanWindow(window_size=self.MEAN_COUNT)
        self.cpu_temp_mean = MeanWindow(window_size=self.MEAN_COUNT, func=CPU.get_cpu_temp)
        self.fan_speed_mean = MeanWindow(1900., window_size=self.MEAN_COUNT)

        self._pr_interval = IntervalProperty(self.update_means, 10., desc='Interval of calculating mean values')
        self._pr_temp = FunctionProperty(
            datatype=DataType.TEMPERATURE,
            getterfunc=self.calc_temp,
            maxage=60.,
            desc='Room temperature stabilized'
        )
        self._pr_last_movement = Property(datatype=DataType.TIMESTAMP,
                                          initial_value=0.,
                                          desc='Last movement detection by fast temperature change',
                                          persistent=False)

        self._pr_delta = Property(datatype=DataType.TEMPERATURE,
                                  initial_value=25.,
                                  desc='Temp difference to trigger movement detection')

        self.properties.update(
            room_temperature=self._pr_temp,
            interval=self._pr_interval,
            last_movement=self._pr_last_movement,
            delta_movement=self._pr_delta
        )

        self._epr_backlight_brightness: Optional[Property] = None
        self._epr_mlx_bufferlength: Optional[Property] = None
        self._epr_mlx_temp_ambient_raw: Optional[Property] = None
        self._epr_mlx_temp_object_raw: Optional[Property] = None
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

    def load(self):
        self._epr_backlight_brightness = self.properties.get('/Appearance/brightness_out')
        self._epr_mlx_bufferlength = self.properties.get('/IIO/mlx90615/buffer/length')
        self._epr_mlx_temp_ambient_raw = self.properties.get('/IIO/mlx90615/channels/temp_ambient/raw')
        self._epr_mlx_temp_object_raw = self.properties.get('/IIO/mlx90615/channels/temp_object/raw')

        self._epr_mlx_temp_object_scan_elements_enable = self.properties.get('/IIO/mlx90615/channels/temp_object/scan_elements_enable')
        self._epr_mlx_timestamp_scan_elements_enable = self.properties.get('/IIO/mlx90615/channels/timestamp/scan_elements_enable')

        self._epr_human_detect = self.properties.get('/Presence/detecting_human')

        self._object_temp_offset = self.properties.get('/IIO/mlx90615/channels/temp_object/offset').value
        self._object_temp_scale = self.properties.get('/IIO/mlx90615/channels/temp_object/scale').value

        self._sensor_temp_offset = self.properties.get('/IIO/mlx90615/channels/temp_ambient/offset').value
        self._sensor_temp_scale = self.properties.get('/IIO/mlx90615/channels/temp_ambient/scale').value

        self._devfile = Path(self.properties.get('/IIO/mlx90615/rawdevice').value)

        self._presence_maininstance: Presence = Presence.instances().get(None)
        if self._presence_maininstance:
            self._announce_human_handler \
                = self._presence_maininstance.register_handler(self.__class__, 'rapid_temp_increase', 60.)

        self.buffer_enable(False)
        self.activate_channel()
        self.buffer_enable(True)
        self.update_means()

    def unload(self):
        if self._presence_maininstance and self._announce_human_handler:
            self._presence_maininstance.unregister_handler(self._announce_human_handler)
        self._announce_human_handler = None

    def stop(self):
        pass

    def calc_temp(self):
        clear_time = time.time() - 30.  # time since no interaction allowed

        if self._pr_last_movement.value > clear_time:
            logger.info('Skipping room temp calculation due to movement')
            return Property.value.fget(self._pr_temp) or 0.

        if self._epr_last_input.value > clear_time:
            logger.info('skipping room temp calculation due to input')
            return Property.value.fget(self._pr_temp) or 0.

        if self._epr_last_touch.value > clear_time:
            logger.info('skipping room temp calculation due to touch')
            return Property.value.fget(self._pr_temp) or 0.

        object_temp = (self.object_temp_mean.mean + self._object_temp_offset) * self._object_temp_scale
        sensor_temp = (self.sensor_temp_mean.mean + self._sensor_temp_offset) * self._sensor_temp_scale

        logger.debug('object temperature mean: %s', object_temp)
        logger.debug('sensor temperature mean: %s', sensor_temp)

        if sensor_temp > object_temp:
            temp = object_temp - ((sensor_temp - object_temp) / 6)
            logger.debug('sensor self correction: %s', temp)
        else:
            temp = object_temp

        if self.cpu_temp_mean.mean > sensor_temp:
            temp -= (self.cpu_temp_mean.mean - sensor_temp) / 60
            logger.debug('sensor cpu correction: %s', temp)

        if self.fan_speed_mean.mean < 1790:
            temp -= 1000
            logger.debug('sensor fan correction: %s', temp)

        if self.backlight_level_mean.mean > 0:
            temp -= self.backlight_level_mean.mean * 3
            logger.debug('sensor backlight correction: ' + str(temp))

        return temp

    def update_means(self):
        self.cpu_temp_mean.update()
        self.sensor_temp_mean.update(self._get_temp_ambient_raw())
        self.fan_speed_mean.update(1900)  # ToDO fan input!
        self.backlight_level_mean.update(self.get_input_value(self._backlight_path))

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

    def _get_temp_object_raw(self) -> float:
        return self._epr_mlx_temp_object_raw.value

    def _get_temp_ambient_raw(self) -> float:
        return self._epr_mlx_temp_ambient_raw.value

    def run(self):
        logger.info('starting MLX90615 thread')

        with self._devfile.open('rb') as devfile:
            while self.module_is_running():
                line = devfile.read(16)
                (tempobj, tempamb, _, timestamp) = struct.unpack('<HHiq', line)

                if abs(tempobj - self.object_temp_mean.mean) > self._pr_delta.value:
                    logger.info('fast temp change: ' + str((self.object_temp_mean.mean - tempobj) * 50 / 1000))
                    self._pr_last_movement.value = time.time()
                    for function in self.inputs['module/input_dev/mlx90615'].events:
                        function('module/input_dev/mlx90615', abs(self.object_temp_mean.mean - tempobj))

                self.object_temp_mean.update(tempobj)

                try:
                    while time.time() - self.inputs['core/input_dev/lasttouch'].last_update < 5:
                        logger.debug('halted mlx90615 thread due touch inputs')
                        self.buffer_enable(False)
                        time.sleep(6)

                    self.buffer_enable(True)
                except Exception as e:
                    logger.error(repr(e), exc_info=True)
