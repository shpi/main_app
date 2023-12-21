import glob
import logging
import os
import sys
from functools import partial

from core.DataTypes import Convert, DataType
from core.Property import EntityProperty

class HWMon:

    def __init__(self):
        super(HWMon, self).__init__()
        self._hwmon = list()

        for sensors in glob.iglob('/sys/class/hwmon/hwmon*', recursive=False):
            sensor_name = self._read_sensor_name(sensors)
            if sensor_name is None:
                continue

            sensor_id = sensors.split('/')[-1]
            self._process_sensor(sensor_id, sensor_name)

    def _read_sensor_name(self, sensor_path):
        try:
            with open(os.path.join(sensor_path, 'name'), 'r') as rf:
                return rf.read().rstrip()
        except OSError as e:
            logging.error(f'Error reading sensor name from {sensor_path}: {e}')
            return None

    def _process_sensor(self, sensor_id, sensor_name):
        for channeltype in ('input', 'alarm', 'enable', 'pwm', 'buzzer', 'relay'):
            self._process_sensor_channels(sensor_id, sensor_name, channeltype)

    def _process_sensor_channels(self, sensor_id, sensor_name, channel_type):
        channel_glob = f"/sys/class/hwmon/{sensor_id}/*_{channel_type}"
        for filename in glob.iglob(channel_glob):
            try:
                channel_desc = self._read_channel_description(filename, channel_type)
                channel_data_type = self._determine_channel_data_type(filename, channel_type)
                channel_is_output = (os.stat(filename).st_mode & 0o444 == 0o444)
                channel_channel = filename.split('/')[-1]

                entity_property = EntityProperty(
                    parent=self,
                    category='sensor' if channel_type in ('input', 'alarm', 'enable') else 'output',
                    entity=sensor_name,
                    name=channel_channel,
                    description=channel_desc,
                    type=channel_data_type,
                    set=partial(self.write_hwmon, sensor_id, channel_channel) if channel_is_output else None,
                    call=partial(self.read_hwmon, sensor_id, channel_channel),
                    interval=20
                )
                self._hwmon.append(entity_property)
            except OSError as e:
                logging.error(f'Error processing channel {filename}: {e}')

    def _read_channel_description(self, filename, channel_type):
        label_file = filename[0:-len(channel_type)] + "label"
        if os.path.isfile(label_file):
            with open(label_file, 'r') as rf:
                return rf.read().rstrip()
        return ''

    def _determine_channel_data_type(self, filename, channel_type):
        if channel_type == 'input':
            if 'temp' in filename:
                return DataType.TEMPERATURE
            elif 'curr' in filename:
                return DataType.CURRENT
            elif 'in' in filename:
                return DataType.VOLTAGE
            elif 'power' in filename:
                return DataType.POWER
            elif 'humidity' in filename:
                return DataType.HUMIDITY
            elif 'fan' in filename:
                return DataType.FAN
        elif channel_type in ('enable', 'alarm'):
            return DataType.BOOL
        elif channel_type == 'pwm':
            return DataType.BYTE
        elif channel_type in ('buzzer', 'relay'):
            return DataType.BOOL
        else:
            return DataType.UNDEFINED

    def get_inputs(self):
        return [prop for prop in self._hwmon if prop.category == 'sensor']

    def read_hwmon(self, channelid, channel):
        try:
            with open(f'/sys/class/hwmon/{channelid}/{channel}', 'r') as rf:
                value = rf.read().strip()
                return Convert.str_to_tight_datatype(value)
        except OSError as e:
            logging.error(f'Error reading from channel {channel}: {e}')
            return None

    def write_hwmon(self, channelid, channel, value, retries=0):
        try:
            with open(f'/sys/class/hwmon/{channelid}/{channel}', 'w') as rf:
                rf.write(str(value))
                return True
        except OSError as e:
            if retries < 5:
                return self.write_hwmon(channelid, channel, value, retries + 1)
            else:
                logging.error(f'Error writing to channel {channel}: {e}')
                return False

# Example usage
# hwmon = HWMon()
# sensors = hwmon.get_inputs()
# for sensor in sensors:
#
