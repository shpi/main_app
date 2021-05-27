import logging
import struct
import sys
import time
from pathlib import Path
from typing import Generator, Optional

import numpy as np

# from ufunclab import minmax # https://github.com/WarrenWeckesser/ufunclab
# from core.CircularBuffer import CircularBuffer
from core.DataTypes import DataType
from core.Property import EntityProperty
from core.Settings import settings
from hardware.CPU import CPU
from interfaces.Module import ThreadModuleBase, ModuleCategories, IgnoreModuleException


class MLX90615(ThreadModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = "MLX90615"
    categories = (ModuleCategories.HARDWARE, )

    TEMP_RANGE_MIN = 0.1
    TEMP_RANGE_MAX = 45.

    iio_buffer_length = 100
    delta = 0.5 * 50
    fan_speed_mean = 1900

    @classmethod
    def iio_device_paths(cls, with_name_file=True, name_match: str = None) -> Generator[Path, None, None]:
        """Generator to iterate over iio devices by filesystem"""
        iio_devices = Path('/sys/bus/iio/devices')

        if not iio_devices.is_dir():
            return

        for device in iio_devices.iterdir():
            namefile = device / 'name'

            if name_match:
                if namefile.is_file():
                    if namefile.read_text().strip() == name_match:
                        yield device
            else:
                if namefile.is_file() or not with_name_file:
                    yield device

    def __init__(self):
        super().__init__()

        self.ospath: Optional[Path] = None

        devices = list(self.iio_device_paths(name_match='mlx90615'))
        if not devices:
            raise IgnoreModuleException("Hardware not found.")

        if len(devices) > 1:
            logging.warning('Multiple MLX90615 device found? Using first.')

        self.ospath = devices[0]  # Use first device. Should be one at maximum.

        self.id = (self.ospath / 'name').read_text().strip()  # iio device name

        self.buffer_enable(0)
        self.activate_channel()
        self.buffer_enable(1)

        # self.load = os.getloadavg()[2]
        # self.cpu_temp_mean = CPU.get_cpu_temp()

        self._backlight_path = settings.str('mlx/backlight_path', 'core/backlight/brightness')

        self.backlight_level_mean = self.get_input_value(self._backlight_path)
        self._fan_path = settings.str('mlx/fan_path', 'sensor/shpi/fan1_input')

        # self._backup_sensor_path = settings.str("mlx/" + self.name + '/backup_sensor_path')
        # self._current_sensor_path = settings.str("mlx/" + self.name + '/current_path')

        self.last_movement = 0

        self.sensor_temp_mean = self.single_shot('in_temp_ambient_raw')
        self.object_temperature = self.single_shot('in_temp_object_raw')

        self.object_mean = self.object_temperature

        # self.load = os.getloadavg()[2]
        self.cpu_temp_mean = CPU.get_cpu_temp()

        # self.current_consumption_mean = 0

        self.buffer = self._data = np.full(6000, self.object_temperature, dtype=np.int16)

        # np.full(self.buffer_size,fill_value=self.object_temperature, dtype=np.int16)
        # data = [startvalue] * size

        self._module = EntityProperty(parent=self,
                                      category='module',
                                      entity='sensor',
                                      name='mlx90615',
                                      value='NOT_INITIALIZED',
                                      description='Room temperature compensation module',
                                      type=DataType.MODULE,
                                      call=self.update,
                                      interval=10)

        # self._thread = ThreadProperty(entity='input_dev',
        #                              name='mlx90615',
        #                              category='module',
        #                              parent=self,
        #                              value=1,
        #                              description='Thread for MLX90615',
        #                              interval=60,
        #                              function=self.mlx_thread)

        self._temp = EntityProperty(parent=self,
                                    category='sensor',
                                    entity='mlx90615',
                                    name='room_temperature',
                                    value=self.object_temperature,
                                    description='Room temperature stabilized',
                                    type=DataType.TEMPERATURE,
                                    call=self.calc_temp,
                                    interval=60)

    def load(self):
        pass

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

        if 'core/input_dev/lastinput' in self.inputs.entries and self.inputs.entries[
            'core/input_dev/lastinput'].last_update + 30 > time.time():
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

        return 'OK'

    def get_input_value(self, path):
        if path not in self.inputs.entries:
            return 0
        else:
            return self.inputs.entries[path].value

    def buffer_enable(self, value):
        if value:
            length_file = self.ospath / 'buffer/length'
            if length_file.is_file():
                # with open(self.ospath + '/buffer/length', 'r+') as rf:
                #     rf.write(str(self.iio_buffer_length))
                length_file.write_text(str(self.iio_buffer_length))

        enable_file = self.ospath / '/buffer/enable'
        if enable_file.is_file():
            # with open(self.ospath + '/buffer/enable', 'r+') as rf:
            #     rf.write(str(value))
            enable_file.write_text(str(value))

    def activate_channel(self):
        try:
            # in_temp_ambient_en
            for channel in ('in_temp_object_en', 'in_timestamp_en'):
                file = self.ospath / 'scan_elements' / channel
                if file.is_file():
                    # with open(self.ospath + '/scan_elements/' + channel, 'r+') as rf:
                    #    rf.write('1')
                    file.write_text('1')

        except Exception as e:
            logging.error('Cannot activate IIO scan channels for MLX' + str(e), exc_info=True)

    def single_shot(self, channel='in_temp_object_raw'):
        channel_file = self.ospath / channel
        if channel_file.is_file():
            return int(channel_file.read_text().strip())

        return None

    def run(self):
        i = 0
        logging.info('starting MLX90615 thread')

        dev_file = Path('/dev') / self.id
        if not dev_file.exists():
            logging.error('File does not exist: ' + str(dev_file))
            return

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
                    for function in self.inputs.entries['module/input_dev/mlx90615'].events:
                        function('module/input_dev/mlx90615', abs(self.object_mean - tempobj))

                self.object_mean = (self.object_mean * 9 + tempobj) // 10

                try:
                    while (time.time() - self.inputs.entries['core/input_dev/lasttouch'].last_update) < 5:
                        logging.debug('halted mlx90615 thread due touch inputs')
                        self.buffer_enable(0)
                        time.sleep(6)

                    self.buffer_enable(1)
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    line_number = exception_traceback.tb_lineno
                    logging.error(f'error: {e} in line {line_number}')
