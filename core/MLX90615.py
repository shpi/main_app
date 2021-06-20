import logging
import struct
import time
from pathlib import Path
from typing import Optional

import numpy as np

# from ufunclab import minmax # https://github.com/WarrenWeckesser/ufunclab
# from core.CircularBuffer import CircularBuffer
from interfaces.DataTypes import DataType
from core.Settings import settings
from hardware.CPU import CPU
from hardware.IIO import IIO
from core.Appearance import Appearance
from interfaces.Module import ThreadModuleBase, ModuleCategories, IgnoreModuleException
from interfaces.PropertySystem import PropertyDict, FunctionProperty, IntervalProperty, Property


class MLX90615(ThreadModuleBase):  # Non Thread?
    allow_maininstance = True
    allow_instances = False
    description = "MLX90615 temperature sensor"
    categories = ModuleCategories.HARDWARE,
    depends_on = Appearance, IIO, CPU

    TEMP_RANGE_MIN = 0.1
    TEMP_RANGE_MAX = 45.
    iio_buffer_length = 100
    delta = 0.5 * 50
    fan_speed_mean = 1900

    def __init__(self, parent, instancename: str = None):
        ThreadModuleBase.__init__(self, parent=parent, instancename=instancename)

        devices = list(IIO.iio_find_device_paths(name_match='mlx90615'))
        if not devices:
            raise IgnoreModuleException("Hardware not found.")

        if len(devices) > 1:
            logging.warning('Multiple MLX90615 device found? Using first.')

        self.iio_device_file = devices[0]  # Use first device. Should be one at maximum.
        self.iio_device_file_name = self.iio_device_file.name
        self.dev_file = Path('/dev') / self.iio_device_file_name


        self.backlight_level_mean = self.get_input_value(self._backlight_path)
        self._fan_path = settings.str('mlx/fan_path', 'sensor/shpi/fan1_input')

        self.last_movement = 0

        self.sensor_temp_mean = self.single_shot('in_temp_ambient_raw')
        self.object_temperature = self.single_shot('in_temp_object_raw')

        self.object_mean = self.object_temperature

        # self.load = os.getloadavg()[2]
        self.cpu_temp_mean = CPU.get_cpu_temp()

        # self.current_consumption_mean = 0

        self.buffer = self._data = np.full(6000, self.object_temperature, dtype=np.int16)

        self._pr_interval = IntervalProperty(self.update, 10., desc="")
        self._pr_temp = FunctionProperty(
            datatype=DataType.TEMPERATURE,
            getterfunc=self.calc_temp,
            maxage=60.,
            desc='Room temperature stabilized'
        )

        self.properties = PropertyDict(
            room_temperature=self._pr_temp,
            interval=self._pr_interval
        )
        self._epr_backlight_brightness: Optional[Property] = None

    def load(self):
        self._epr_backlight_brightness = self.properties.root().get('Appearance/brightness_out')

        self.buffer_enable(False)
        self.activate_channel()
        self.buffer_enable(True)

    def unload(self):
        pass

    def stop(self):
        pass

    def get_inputs(self) -> list:
        if self.ospath and self.ospath.is_file():
            return [self._module, self._temp]

        return []

    def calc_temp(self):
        if self.last_movement + 30 > time.time():
            logging.info('skipping room temp calculation due to movement')
            return self._temp.value

        if 'core/input_dev/lastinput' in self.inputs and \
                self.inputs['core/input_dev/lastinput'].last_update + 30 > time.time():
            logging.info('skipping room temp calculation due to input')
            return self._temp.value

        object_temp = (self.object_mean - 13657.5) * 20
        sensor_temp = (self.sensor_temp_mean - 13657.5) * 20

        logging.debug('object temperature mean: ' + str(object_temp))
        logging.debug('sensor temperature mean: ' + str(sensor_temp))

        if sensor_temp > object_temp:
            temp = object_temp - ((sensor_temp - object_temp) / 6)
            logging.debug('sensor self correction: ' + str(temp))

        else:
            temp = object_temp

        if self.cpu_temp_mean > sensor_temp:
            temp -= (self.cpu_temp_mean - sensor_temp) / 60
            logging.debug('sensor cpu correction: ' + str(temp))

        if self.fan_speed_mean < 1790:
            temp -= 1000
            logging.debug('sensor fan correction: ' + str(temp))

        if self.backlight_level_mean > 0:
            temp -= self.backlight_level_mean * 3
            logging.debug('sensor backlight correction: ' + str(temp))

        self._temp.value = temp

        return self._temp.value

    def update(self):
        self.cpu_temp_mean = (self.cpu_temp_mean * 9 + CPU.get_cpu_temp()) / 10
        self.sensor_temp_mean = (self.sensor_temp_mean * 9 + (
                self.single_shot('in_temp_ambient_raw') or self.sensor_temp_mean)) / 10

        self.fan_speed_mean = (self.fan_speed_mean * 9 + self.get_input_value(self._fan_path)) / 10
        logging.debug('fan spead mean:' + str(self.fan_speed_mean))

        self.backlight_level_mean *= 9
        self.backlight_level_mean += self.get_input_value(self._backlight_path)
        self.backlight_level_mean /= 10
        logging.debug('backlight mean: ' + str(self.backlight_level_mean))

    def buffer_enable(self, value: bool):
        if value:
            length_file = self.ospath / 'buffer/length'
            if not length_file.is_file():
                raise FileNotFoundError("buffer/length missing in FS.")
            # with open(self.ospath + '/buffer/length', 'r+') as rf:
            #     rf.write(str(self.iio_buffer_length))
            length_file.write_text(str(self.iio_buffer_length))

        enable_file = self.ospath / 'buffer/enable'
        if not enable_file.is_file():
            raise FileNotFoundError("buffer/enable missing in FS.")
        # with open(self.ospath + '/buffer/enable', 'r+') as rf:
        #     rf.write(str(value))
        enable_file.write_text(str(int(value)))

    def activate_channel(self):
        try:
            # in_temp_ambient_en
            for channel in ('in_temp_object_en', 'in_timestamp_en'):
                file = self.ospath / 'scan_elements' / channel
                if not file.is_file():
                    raise FileNotFoundError(str(file))
                # with open(self.ospath + '/scan_elements/' + channel, 'r+') as rf:
                #    rf.write('1')
                file.write_text('1')

        except Exception as e:
            logging.error('Cannot activate IIO scan channels for MLX' + str(e), exc_info=True)

    def single_shot(self, channel='in_temp_object_raw') -> int:
        channel_file = self.ospath / channel
        if not channel_file.is_file():
            raise FileNotFoundError(channel_file)

        return int(channel_file.read_text().strip())

    def run(self):
        i = 0
        logging.info('starting MLX90615 thread')

        dev_file = Path('/dev') / self.iio_devname
        if not dev_file.exists():
            raise FileNotFoundError('File does not exist: ' + str(dev_file))

        with dev_file.open('rb') as devfile:
            while self.module_is_running():
                line = devfile.read(16)
                (tempobj, tempamb, _, timestamp) = struct.unpack('<HHiq', line)

                self.buffer[i] = tempobj
                i += 1
                if i > 5999:
                    i = 0

                # temp2 -= 13657.5
                # temp2 *= 20
                # timestamp = timestamp / 1000000000
                # a = minmax(data)
                # if (a[1] - a[0]) > self.delta:

                if abs(tempobj - self.object_mean) > self.delta:
                    logging.info('fast temp change: ' + str((self.object_mean - tempobj) * 50 / 1000))
                    self.last_movement = time.time()
                    for function in self.inputs['module/input_dev/mlx90615'].events:
                        function('module/input_dev/mlx90615', abs(self.object_mean - tempobj))

                self.object_mean = (self.object_mean * 9 + tempobj) // 10

                try:
                    while time.time() - self.inputs['core/input_dev/lasttouch'].last_update < 5:
                        logging.debug('halted mlx90615 thread due touch inputs')
                        self.buffer_enable(False)
                        time.sleep(6)

                    self.buffer_enable(True)
                except Exception as e:
                    logging.error(str(e), exc_info=True)
