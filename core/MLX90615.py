import os
import glob
import sys
import logging
import time
import struct
import numpy as np
# from ufunclab import minmax # https://github.com/WarrenWeckesser/ufunclab
from core.CircularBuffer import CircularBuffer
from core.DataTypes import DataType
from PySide2.QtCore import QSettings
from core.Property import EntityProperty, ThreadProperty


class MLX90615:
    TEMP_RANGE_MIN = 0.1
    TEMP_RANGE_MAX = 45

    def __init__(self, inputs, settings):

        super(MLX90615, self).__init__()

        self.ospath = None

        for sensor in glob.iglob('/sys/bus/iio/devices/*', recursive=False):
            if os.path.isfile(sensor + '/name'):
                with open(sensor + '/name', 'r') as rf:
                    if 'mlx90615' == (rf.read().rstrip()):
                        self.ospath = sensor
                        self.id = sensor[len('/sys/bus/iio/devices/'):]
                        self.iio_buffer_length = 100
                        self.buffer_enable(0)
                        self.activate_channel()
                        self.buffer_enable(1)
                        self.delta = 0.5 * 50

                        self.inputs = inputs
                        self.settings = settings

                        # self.load = os.getloadavg()[2]

                        self.cpu_temp_mean = self.get_cpu_temp()
                        self.fan_speed_mean = 1900
                        self._backlight_path = settings.value('mlx/backlight_path', 'backlight/brightness')

                        self.backlight_level_mean = self.get_input_value(self._backlight_path)
                        self._fan_path = settings.value('mlx/fan_path', 'hwmon/shpi/fan1_input')

                        # self._backup_sensor_path = settings.value("mlx/" + self.name + '/backup_sensor_path', '')
                        # self._current_sensor_path = settings.value("mlx/" + self.name + '/current_path', '')

                        self.last_movement = 0

                        self.sensor_temp_mean = self.single_shot('in_temp_ambient_raw')
                        self.object_temperature = self.single_shot('in_temp_object_raw')

                        self.object_mean = self.object_temperature


                        # self.load = os.getloadavg()[2]
                        self.cpu_temp_mean = self.get_cpu_temp()
                        self.fan_speed_mean = 1900
                        self.backlight_level_mean = self.get_input_value(self._backlight_path)

                        # self.current_consumption_mean = 0

                        self.buffer = CircularBuffer(6000, dtype=np.int16)

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

                        self._thread = ThreadProperty(entity='input_dev',
                                                      name='mlx90615',
                                                      category='module',
                                                      parent=self,
                                                      value=1,
                                                      description='Thread for MLX90615',
                                                      interval=60,
                                                      function=self.mlx_thread)

                        self._temp = EntityProperty(parent=self,
                                                    category='sensor',
                                                    entity='mlx90615',
                                                    name='room_temperature',
                                                    description='Room temperature stabilized',
                                                    type=DataType.TEMPERATURE,
                                                    call=self.calc_temp,
                                                    interval=60)

                        break

        else:
            logging.error('No MLX90615 found')

    def get_inputs(self) -> tuple:

        if self.ospath:

            return self._module, self._temp, self._thread

        else:
            return ()

    def calc_temp(self):

        if self.last_movement + 60 > time.time():
            logging.info('skipping room temp calculation due to movement')
            return self._temp.value

        if 'core/input_dev/lastinput' in self.inputs.entries and self.inputs.entries['core/input_dev/lastinput'].last_update + 60 > time.time():
            logging.info('skipping room temp calculation due to input')
            return self._temp.value

        object_temp = (self.object_mean - 13657.5) * 20
        sensor_temp = (self.sensor_temp_mean - 13657.5) * 20

        logging.debug('object temperature mean: ' + str(object_temp))
        logging.debug('sensor temperature mean: ' + str(sensor_temp))

        if sensor_temp > object_temp:
            temp = object_temp - ((sensor_temp - object_temp) / 6)

        else:
            temp = object_temp

        if self.cpu_temp_mean > sensor_temp:
            temp -= (self.cpu_temp_mean - sensor_temp) / 60

        if self.fan_speed_mean < 1800:
            temp -= 1000

        if self.backlight_level_mean > 0:
            temp -= self.backlight_level_mean * 3

        self._temp.value = temp

        return self._temp.value

    def update(self):

        self.cpu_temp_mean = (self.cpu_temp_mean * 9 + self.get_cpu_temp()) / 10
        self.sensor_temp_mean = (self.sensor_temp_mean * 9 + (
                self.single_shot('in_temp_ambient_raw') or self.sensor_temp_mean)) / 10
        self.fan_speed_mean = (self.fan_speed_mean * 9 + self.get_input_value(self._fan_path)) / 10

        self.backlight_level_mean *= 9
        self.backlight_level_mean += self.get_input_value(self._backlight_path)
        self.backlight_level_mean /= 10

        return 'OK'

    def get_input_value(self, path):

        if path not in self.inputs.entries:
            return 0
        else:
            return self.inputs.entries[path].value

    def buffer_enable(self, value):

        if value:
            if os.path.isfile(self.ospath + '/buffer/length'):
                with open(self.ospath + '/buffer/length', 'r+') as rf:
                    rf.write(str(self.iio_buffer_length))

        if os.path.isfile(self.ospath + '/buffer/enable'):
            with open(self.ospath + '/buffer/enable', 'r+') as rf:
                rf.write(str(value))

    def activate_channel(self):
        try:
            # in_temp_ambient_en
            for channel in ('in_temp_object_en', 'in_timestamp_en'):
                if os.path.isfile(self.ospath + '/scan_elements/' + channel):
                    with open(self.ospath + '/scan_elements/' + channel, 'r+') as rf:
                        rf.write('1')
        except Exception as e:
            logging.error('Cannot activate IIO scan channels for MLX ' + str(e))

    def single_shot(self, channel='/in_temp_object_raw'):

        if os.path.isfile(self.ospath + '/' + channel):
            with open(self.ospath + '/' + channel, 'r') as rf:
                return int(rf.read().rstrip())

        return None

    def get_cpu_temp(self):  # only for now

        path = '/sys/class/thermal/thermal_zone0/temp'

        if os.path.isfile(path):
            with open(path, 'r') as rf:
                return int(rf.read().rstrip())

        return 0

    def mlx_thread(self):

        logging.info('starting MLX90615 thread')

        if os.path.exists('/dev/' + self.id):
            with open('/dev/' + self.id, 'rb') as devfile:
                while self._thread.value:

                    line = devfile.read(16)
                    (tempobj, tempamb, _, timestamp) = struct.unpack('<HHiq', line)

                    self.buffer.append(tempobj)

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
                       pass
