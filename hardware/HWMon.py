import glob
import logging
import os
import sys
from functools import partial

from core.DataTypes import DataType
from core.Property import EntityProperty


class HWMon:
    def __init__(self):
        self._hwmon = []

        for sensors in glob.iglob('/sys/class/hwmon/hwmon*', recursive=False):
            if os.path.isfile(sensors + '/name'):
                with open(sensors + '/name', 'r') as rf:
                    sensor_name = (rf.read().rstrip())
            else:
                break

            sensors = sensors.split('/')
            sensor_id = sensors[-1]

            for channeltype in ('input', 'alarm', 'enable'):
                for filename in glob.iglob(f"/sys/class/hwmon/{sensor_id}/*_{channeltype}"):

                    channel_desc = ''
                    if os.path.isfile(filename[0:-len(channeltype)] + "label"):
                        with open(filename[0:-len(channeltype)] + "label", 'r') as rf:
                            channel_desc = (rf.read().rstrip())
                    channel_type = DataType.UNDEFINED
                    channel_is_output = (os.stat(filename).st_mode & 0o444 == 0o444)

                    filename = filename.split('/')
                    channel_channel = filename[-1]

                    if channeltype == 'input':
                        if channel_channel.startswith('temp'):
                            channel_type = DataType.TEMPERATURE
                        elif channel_channel.startswith('curr'):
                            channel_type = DataType.CURRENT
                        elif channel_channel.startswith('in'):
                            channel_type = DataType.VOLTAGE
                        elif channel_channel.startswith('power'):
                            channel_type = DataType.POWER
                        elif channel_channel.startswith('humidity'):
                            channel_type = DataType.HUMIDITY
                        elif channel_channel.startswith('fan'):
                            channel_type = DataType.FAN

                    if channeltype == 'enable':
                        channel_type = DataType.BOOLEAN
                    if channeltype == 'alarm':
                        channel_type = DataType.BOOLEAN

                    self._hwmon.append(EntityProperty(parent=self,
                                                      category='sensor',
                                                      entity=sensor_name,
                                                      name=channel_channel,
                                                      description=channel_desc,
                                                      type=channel_type,
                                                      set=partial(self.write_hwmon, sensor_id,
                                                                  channel_channel) if channel_is_output else None,
                                                      call=partial(self.read_hwmon, sensor_id, channel_channel),
                                                      interval=20))

            for channeltype in ('pwm', 'buzzer', 'relay'):
                for filename in glob.iglob(f"/sys/class/hwmon/{sensor_id}/{channeltype}[0-9]"):
                    channel_desc = ''
                    if os.path.isfile(filename + "_label"):
                        with open(filename + "_label", 'r') as rf:
                            channel_desc = (rf.read().rstrip())
                    channel_type = DataType.BYTE if (channeltype == 'pwm') else DataType.BOOLEAN
                    channel_is_output = (os.stat(filename).st_mode & 0o444 == 0o444)
                    filename = filename.split('/')
                    channel_channel = filename[-1]
                    self._hwmon.append(EntityProperty(parent=self,
                                                      category='output',
                                                      entity=sensor_name,
                                                      name=channel_channel,
                                                      description=channel_desc,
                                                      type=channel_type,
                                                      set=partial(self.write_hwmon, sensor_id,
                                                                  channel_channel) if channel_is_output else None,
                                                      call=partial(self.read_hwmon, sensor_id, channel_channel),
                                                      interval=20))

    def get_inputs(self) -> list:
        return self._hwmon

    @staticmethod
    def read_hwmon(channelid, channel):
        if not os.path.isfile(f'/sys/class/hwmon/{channelid}/{channel}'):
            return None

        try:
            with open(f'/sys/class/hwmon/{channelid}/{channel}', 'r') as rf:
                value = rf.read().strip()
                # logging.debug(f' reading channel: {channel} value: {value}')
                return DataType.str_to_tight_datatype(value)

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'channel: {channel} error: {e} in line {line_number}')

    def write_hwmon(self, channelid, channel, value, retries=0):
        logging.debug(f' writing {value} to output')
        value = str(int(value))
        if not os.path.isfile(f'/sys/class/hwmon/{channelid}/{channel}'):
            return False

        try:
            with open(f'/sys/class/hwmon/{channelid}/{channel}', 'r+') as rf:
                rf.write(value)
                return True

        except Exception as e:
            if retries < 5:
                retries += 1
                return self.write_hwmon(channelid, channel, value, retries)
            else:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                line_number = exception_traceback.tb_lineno
                logging.error(f'channel: {channel} error: {e} in line {line_number}')
                return False
