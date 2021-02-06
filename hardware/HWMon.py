import glob
import os
import logging
from functools import partial
from core.DataTypes import DataType


class HWMon:

    def __init__(self):

        super(HWMon, self).__init__()
        self._hwmon = dict()

        for sensors in glob.iglob('/sys/class/hwmon/hwmon*', recursive=False):
            sensor = dict()

            if os.path.isfile(sensors + '/name'):
                with open(sensors + '/name', 'r') as rf:
                    sensor['name'] = (rf.read().rstrip())

            sensors = sensors.split('/')
            sensor['id'] = sensors[-1]

            for channeltype in ('input', 'alarm', 'enable'):
                for filename in glob.iglob(f"/sys/class/hwmon/{sensor['id']}/*_{channeltype}"):

                    channel = sensor.copy()
                    channel['description'] = ''
                    if os.path.isfile(filename[0:-len(channeltype)] + "label"):
                        with open(filename[0:-len(channeltype)] + "label", 'r') as rf:
                            channel['description'] = (rf.read().rstrip())
                    channel['type'] = DataType.UNDEFINED
                    channel['path'] = filename
                    channel['rights'] = (os.stat(filename).st_mode & 0o777)
                    filename = filename.split('/')
                    channel['channel'] = filename[-1]
                    self._hwmon[f"{channel['name']}/{filename[-1]}"] = channel

                    if channeltype == 'input':
                        if channel['channel'].startswith('temp'):
                            channel['type'] = DataType.TEMPERATURE
                        elif channel['channel'].startswith('curr'):
                            channel['type'] = DataType.CURRENT
                        elif channel['channel'].startswith('in'):
                            channel['type'] = DataType.VOLTAGE
                        elif channel['channel'].startswith('power'):
                            channel['type'] = DataType.POWER
                        elif channel['channel'].startswith('humidity'):
                            channel['type'] = DataType.HUMIDITY
                        elif channel['channel'].startswith('fan'):
                            channel['type'] = DataType.FAN

                    if channeltype == 'enable':
                        channel['type'] = DataType.BOOL
                    if channeltype == 'alarm':
                        channel['type'] = DataType.BOOL

            for channeltype in ('pwm', 'buzzer', 'relay'):
                for filename in glob.iglob(f"/sys/class/hwmon/{sensor['id']}/{channeltype}[0-9]"):
                    channel = sensor.copy()
                    channel['description'] = ''
                    if os.path.isfile(filename + "_label"):
                        with open(filename + "_label", 'r') as rf:
                            channel['description'] = (rf.read().rstrip())
                    channel['type'] = DataType.BYTE if (
                            channeltype == 'pwm') else DataType.BOOL
                    channel['path'] = filename
                    channel['rights'] = (os.stat(filename).st_mode & 0o777)
                    filename = filename.split('/')
                    channel['channel'] = filename[-1]
                    self._hwmon[f"{channel['name']}/{filename[-1]}"] = channel

    def get_inputs(self) -> dict:
        hwmoninputs = dict()
        for key, value in self._hwmon.items():

            if value['rights'] & 0o444 == 0o444:
                hwmoninputs[f"hwmon/{value['name']}/{value['channel']}"] = {"description": value['description'],
                                                                            # "rights": value['rights'],
                                                                            "interval": 20,
                                                                            "type": value['type'],
                                                                            "call": partial(self.read_hwmon,
                                                                                            value['id'],
                                                                                            value['channel'])}

            if value['rights'] == 0o644:
                hwmoninputs[f"hwmon/{value['name']}/{value['channel']}"]["set"] = partial(
                    self.write_hwmon, value['id'], value['channel'])

        return hwmoninputs

    @staticmethod
    def read_hwmon(channelid, channel):

        if os.path.isfile(f'/sys/class/hwmon/{channelid}/{channel}'):
            try:
                with open(f'/sys/class/hwmon/{channelid}/{channel}', 'r') as rf:
                    value = int(rf.read().rstrip())
                    logging.debug(f' reading channel: {channel} value: {value}')
                    return value

            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                line_number = exception_traceback.tb_lineno
                logging.error('error: {}'.format(e))
                logging.error('error in line: {}'.format(line_number))
                logging.error(f'reading channel: {channel} failed with error {e}')

        else:
            return None

    def write_hwmon(self, channelid, channel, value, retries=0):
        logging.debug(f' writing {value} to output')
        value = str(int(value))
        if os.path.isfile(f'/sys/class/hwmon/{channelid}/{channel}'):
            try:
                with open(f'/sys/class/hwmon/{channelid}/{channel}', 'r+') as rf:
                    rf.write(value)
                    rf.seek(0)
                    newvalue = rf.read().rstrip()
                    logging.debug(f'reading back {newvalue}')
                    if value == newvalue:
                        return True
                    else:
                        if retries < 5:
                            retries += 1
                            return self.write_hwmon(channelid, channel, value, retries)
                        else:
                            return False
            except Exception as e:
                if retries < 5:
                    retries += 1
                    return self.write_hwmon(channelid, channel, value, retries)
                else:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    line_number = exception_traceback.tb_lineno
                    logging.error('error: {}'.format(e))
                    logging.error('error in line: {}'.format(line_number))
                    return False
        else:
            return False
