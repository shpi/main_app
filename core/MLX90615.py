import os
import glob
import logging
import time
import struct

import threading
import numpy as np
# from ufunclab import minmax # https://github.com/WarrenWeckesser/ufunclab
from core.CircularBuffer import CircularBuffer
from core.DataTypes import DataType
from PySide2.QtCore import QSettings


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

                        self._fan_path = settings.value('mlx/fan_path', 'hwmon/shpi/fan1_input')
                        self._backlight_path = settings.value('mlx/backlight_path', 'backlight/brightness')
                        # self._backup_sensor_path = settings.value("mlx/" + self.name + '/backup_sensor_path', '')
                        # self._current_sensor_path = settings.value("mlx/" + self.name + '/current_path', '')

                        self.last_movement = 0
                        self.last_roomtemp = 0

                        self.sensor_temp_mean = self.single_shot('in_temp_ambient_raw')
                        self.object_temperature = self.single_shot('in_temp_object_raw')

                        self.object_mean = self.object_temperature

                        # self.load = os.getloadavg()[2]
                        self.cpu_temp_mean = self.get_cpu_temp()
                        self.fan_speed_mean = self.get_input_value(self._fan_path)
                        self.backlight_level_mean = self.get_input_value(self._backlight_path)

                        # self.current_consumption_mean = 0

                        self.buffer = CircularBuffer(6000, dtype=np.int16)

                        # np.full(self.buffer_size,fill_value=self.object_temperature, dtype=np.int16)
                        # data = [startvalue] * size

                        self._module = {'description': 'Room temperature compensation module',
                                        'value': 'NOT_INITIALIZED',
                                        'type': DataType.MODULE,
                                        'lastupdate': 0,
                                        'interval': 10,
                                        'call': self.update}

                        self._temp = {'description': 'Room temperature stabilized',
                                      'value': 0,
                                      'type': DataType.TEMPERATURE,
                                      'lastupdate': 0,
                                      'interval': 60,
                                      'call': self.calc_temp}

                        break

        else:
            logging.error('No MLX90615 found')

    def get_inputs(self) -> dict:

        if self.ospath:

            return {'roomtemp/module': self._module,
                    'roomtemp/temp': self._temp
                    }
        else:
            return {}

    def calc_temp(self):

        if self.last_movement + 30 < time.time():

            object_temp = (self.object_mean - 13657.5) * 20
            sensor_temp = (self.sensor_temp_mean - 13657.5) * 20

            logging.info('objekt temperatur gemittelt: ' + str(object_temp))
            logging.info('sensor temperatur gemittelt: ' + str(sensor_temp))

            if sensor_temp > object_temp:
                temp = object_temp - ((object_temp - sensor_temp) / 6)
                logging.info('raumtemperatur einfach korrigiert: ' + str(temp))

            else:
                temp = object_temp
                logging.info('raumptemperatur ohne korrektur: ' + str(temp))

            if self.cpu_temp_mean > sensor_temp:
                temp -= (self.cpu_temp_mean - sensor_temp) / 60
                logging.info('raumtemperatur korrigiert cpu: ' + str(temp))

            if self.fan_speed_mean < 1800:
                temp -= 1000
                logging.info('vent off, temp corrected: ' + str(temp))

            if self.backlight_level_mean > 0:
                temp -= self.backlight_level_mean * 3
                logging.info('raumptemperatur corrected backlight: ' + str(temp))

            self._temp['value'] = temp

            self.last_roomtemp = time.time()

        else:
            logging.info('skipping room temp calculation due to movement')

        return self._temp['value']

    def update(self):

        self.cpu_temp_mean *= 0.95
        self.cpu_temp_mean += self.get_cpu_temp() // 20

        self.sensor_temp_mean *= 0.95
        self.sensor_temp_mean += self.single_shot('in_temp_ambient_raw') // 20

        self.fan_speed_mean *= 0.95
        self.fan_speed_mean += self.get_input_value(self._fan_path) // 20

        self.backlight_level_mean *= 0.95
        self.backlight_level_mean += self.get_input_value(self._backlight_path) // 20

        return 'OK'

    def get_input_value(self, path):

        if path not in self.inputs.entries:
            return 0
        else:
            return self.inputs[path]['value']

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
        if os.path.isfile(self.ospath + channel):
            # print(sensor + '/in_temp_object_raw')
            with open(self.ospath + '/in_temp_object_raw', 'r') as rf:
                return int(rf.read().rstrip())

        return 0

    def get_cpu_temp(self):  # only for now

        path = '/sys/class/thermal/thermal_zone0/temp'

        if os.path.isfile(path):
            with open(path, 'r') as rf:
                return int(rf.read().rstrip())

        return 0

    def mlx_thread(self):

        if os.path.exists('/dev/' + self.id):
            with open('/dev/' + self.id, 'rb') as devfile:
                while True:

                    line = devfile.read(16)
                    (tempobj, tempamb, _, timestamp) = struct.unpack('<HHiq', line)

                    self.buffer.append(tempobj)

                    # temp2 -= 13657.5
                    # temp2 *= 20
                    # timestamp = timestamp / 1000000000
                    # a = minmax(data)
                    # if (a[1] - a[0]) > self.delta:

                    if (self.object_mean - tempobj) < -self.delta:
                        print('SCHNELLE ABKÜHLUNG: ' + str((self.object_mean - tempobj)))
                        self.last_movement = time.time()

                    if (self.object_mean - tempobj) > self.delta:
                        print('SCHNELLE AUFWÄRMUNG: ' + str((self.object_mean - tempobj)))
                        self.last_movement = time.time()

                    self.object_mean *= 0.95
                    self.object_mean += tempobj // 20

                    # while (time.time() - lastuserinput) < 2:

                    #         buffer_enable(0)
                    #         time.sleep(2)

                    # buffer_enable(1)
