import glob
import logging
import os
import sys
from functools import partial
import fnmatch

from core.DataTypes import Convert, DataType
from core.Property import EntityProperty


class HWMon:
    _properties = []

    @staticmethod
    def get_inputs() -> list:
        if HWMon._properties:
            return HWMon._properties  # schon geladen

        base_map = {
            'temp': 'Temperature',
            'curr': 'Current',
            'in': 'Voltage',
            'power': 'Power',
            'energy': 'Energy',
            'charge': 'Charge',
            'humidity': 'Humidity',
            'fan': 'Fan speed',
            'freq': 'Frequency',
            'pwm': 'PWM output',
            'buzzer': 'Buzzer control',
            'relay': 'Relay control',
            'beep': 'Beep control',
            'intrusion': 'Chassis intrusion',
            'vrm': 'VRM version'
        }

        suffix_map = [
            ('*_lcrit_alarm', 'lower critical alarm status'),
            ('*_crit_alarm', 'critical alarm status'),
            ('*_min_alarm', 'minimum alarm status'),
            ('*_max_alarm', 'maximum alarm status'),
            ('*_cap_alarm', 'cap alarm status'),
            ('*_alarm', 'alarm status'),
            ('*_fault', 'fault status'),
            ('*_beep', 'beep control'),
            ('*_hyst', 'hysteresis value'),
            ('*_cap_hyst', 'cap hysteresis'),
            ('*_cap_max', 'maximum cap limit'),
            ('*_cap_min', 'minimum cap limit'),
            ('*_cap', 'cap limit'),
            ('*_offset', 'offset'),
            ('*_target', 'target setting'),
            ('*_pulses', 'tach pulses per revolution'),
            ('*_div', 'clock divisor'),
            ('*_average_interval', 'averaging interval'),
            ('*_average_highest', 'historical average high'),
            ('*_average_lowest', 'historical average low'),
            ('*_average', 'average value'),
            ('*_highest', 'historical maximum'),
            ('*_lowest', 'historical minimum'),
            ('*_reset_history', 'reset history'),
            ('*_lcrit', 'lower critical limit'),
            ('*_crit', 'critical limit'),
            ('*_min', 'minimum limit'),
            ('*_max', 'maximum limit'),
            ('*_enable', 'enable switch'),
            ('*_input', 'input'),
            ('beep_enable', 'master beep enable'),
        ]

        def make_desc(name: str, label: str = '') -> str:
            base_desc = ''
            for key, desc in base_map.items():
                if name.startswith(key):
                    base_desc = desc
                    break

            suffix_desc = ''
            for pattern, desc in suffix_map:
                if fnmatch.fnmatch(name, pattern):
                    suffix_desc = desc
                    break

            result = ' '.join(filter(None, [base_desc, suffix_desc])).strip()
            if label:
                return f"{result} ({label})" if result else label
            return result

        for sensors in glob.iglob('/sys/class/hwmon/hwmon*', recursive=False):
            if os.path.isfile(sensors + '/name'):
                with open(sensors + '/name', 'r') as rf:
                    sensor_name = (rf.read().rstrip())
            else:
                break

            sensors = sensors.split('/')
            sensor_id = sensors[-1]

            for channeltype in (
                'input', 'alarm', 'enable', 'fault', 'beep',
                'max', 'min', 'crit', 'lcrit', 'hyst', 'offset',
                'cap', 'cap_alarm', 'cap_hyst'):

                for filename in glob.iglob(f"/sys/class/hwmon/{sensor_id}/*_{channeltype}"):
                    channel_type = DataType.UNDEFINED
                    channel_is_output = (os.stat(filename).st_mode & 0o200 == 0o200)
                    channel_channel = os.path.basename(filename)

                    label = ''
                    if os.path.isfile(filename[0:-len(channeltype)] + "label"):
                        try:
                            with open(filename[0:-len(channeltype)] + "label", 'r') as rf:
                                label = rf.read().rstrip()
                        except Exception:
                            label = "read error"

                    channel_desc = make_desc(channel_channel, label)

                    if channeltype == 'input':
                        if channel_channel.startswith('temp'):
                            channel_type = DataType.TEMPERATURE
                        elif channel_channel.startswith('curr'):
                            channel_type = DataType.CURRENT
                        elif channel_channel.startswith('in'):
                            channel_type = DataType.VOLTAGE
                        elif channel_channel.startswith('power'):
                            channel_type = DataType.POWER
                        elif channel_channel.startswith('energy'):
                            channel_type = DataType.ENERGY
                        elif channel_channel.startswith('charge'):
                            channel_type = DataType.WORK
                        elif channel_channel.startswith('humidity'):
                            channel_type = DataType.HUMIDITY
                        elif channel_channel.startswith('fan'):
                            channel_type = DataType.FAN
                        elif channel_channel.startswith('freq'):
                            channel_type = DataType.FREQUENCY

                    if channeltype in ('enable', 'alarm', 'fault', 'beep', 'cap_alarm'):
                        channel_type = DataType.BOOL
                    if channeltype in ('max', 'min', 'crit', 'lcrit', 'hyst', 'offset', 'cap', 'cap_hyst'):
                        if channel_channel.startswith('temp'):
                            channel_type = DataType.TEMPERATURE
                        elif channel_channel.startswith('curr'):
                            channel_type = DataType.CURRENT
                        elif channel_channel.startswith('in'):
                            channel_type = DataType.VOLTAGE
                        elif channel_channel.startswith('power'):
                            channel_type = DataType.POWER
                        elif channel_channel.startswith('energy'):
                            channel_type = DataType.ENERGY
                        elif channel_channel.startswith('charge'):
                            channel_type = DataType.WORK
                        elif channel_channel.startswith('humidity'):
                            channel_type = DataType.HUMIDITY
                        elif channel_channel.startswith('fan'):
                            channel_type = DataType.FAN
                        elif channel_channel.startswith('freq'):
                            channel_type = DataType.FREQUENCY

                    HWMon._properties.append(EntityProperty(
                        category='sensor/' + sensor_name,
                        name=channel_channel,
                        description=channel_desc,
                        type=channel_type,
                        set=partial(HWMon.write_hwmon, sensor_id, channel_channel) if channel_is_output else None,
                        call=partial(HWMon.read_hwmon, sensor_id, channel_channel),
                        interval=60))

            for channeltype in ('pwm', 'buzzer', 'relay'):
                for filename in glob.iglob(f"/sys/class/hwmon/{sensor_id}/{channeltype}[0-9]"):
                    channel_type = DataType.BYTE if (channeltype == 'pwm') else DataType.BOOL
                    channel_is_output = (os.stat(filename).st_mode & 0o200 == 0o200)
                    channel_channel = os.path.basename(filename)

                    label = ''
                    if os.path.isfile(filename + "_label"):
                        try:
                            with open(filename + "_label", 'r') as rf:
                                label = rf.read().rstrip()
                        except Exception:
                            label = "read error"

                    channel_desc = make_desc(channel_channel, label)
                    min = 0
                    step = 1
                    maxval = 255 if channeltype == 'pwm' else 1

                    HWMon._properties.append(EntityProperty(
                        category='output/' + sensor_name,
                        min=min,
                        step=step,
                        max=maxval,
                        name=channel_channel,
                        description=channel_desc,
                        type=channel_type,
                        set=partial(HWMon.write_hwmon, sensor_id, channel_channel) if channel_is_output else None,
                        call=partial(HWMon.read_hwmon, sensor_id, channel_channel),
                        interval=60))

        return HWMon._properties

    @staticmethod
    def read_hwmon(channelid, channel):
        path = f'/sys/class/hwmon/{channelid}/{channel}'
        if not os.path.isfile(path):
            return None

        try:
            with open(path, 'r') as rf:
                value = rf.read().strip()
                return Convert.str_to_tight_datatype(value)
        except Exception as e:
            _, _, tb = sys.exc_info()
            logging.error(f'channel: {channel} error: {e} in line {tb.tb_lineno}')
            return None

    @staticmethod
    def write_hwmon(channelid, channel, value, retries=0):
        logging.debug(f'writing {value} to hwmon channel {channel}')
        path = f'/sys/class/hwmon/{channelid}/{channel}'
        value = str(int(value))

        if not os.path.isfile(path):
            logging.error(f'{path} does not exist')
            return False

        try:
            with open(path, 'r+') as rf:
                rf.write(value)
                return True
        except Exception as e:
            if retries < 5:
                return HWMon.write_hwmon(channelid, channel, value, retries + 1)
            else:
                _, _, tb = sys.exc_info()
                logging.error(f'channel: {channel} write error: {e} in line {tb.tb_lineno}')
                return False
