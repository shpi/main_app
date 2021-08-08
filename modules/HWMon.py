from logging import getLogger
from pathlib import Path
from typing import Any

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import PropertyDict, Property


logger = getLogger(__name__)

_hwmon_devices_path = Path('/sys/class/hwmon')


def _to_bool(source: str) -> bool:
    source = source.strip()
    return source != '0'


def _from_bool(source: bool) -> str:
    return '1' if source else '0'


def _from_milli(source: str) -> float:
    return float(source) / 1000


def _to_milli(source: float) -> str:
    return str(source * 1000)


def _to_byte(source: int) -> str:
    source = int(source)

    if source < 0:
        return '0'

    if source > 255:
        return '255'

    return str(source)


def _no_write(source: Any):
    logger.error('Cannot write to this HWMon channel')


class HWMonChannel(Property):
    __slots__ = '_channel_path', '_channel_name', '_channel_type', '_from_str_func', '_to_str_func'

    def __init__(self, channel_path: Path, channel_type: str):
        self._channel_path = channel_path.resolve()
        self._channel_name = self._channel_path.name

        # '*_input', '*_alarm', '*_enable', 'pwm*', 'buzzer*', 'relay*'
        self._channel_type = channel_type

        # Defaults conversion
        self._to_str_func = str
        self._from_str_func = str

        # Define datatype
        if channel_type == '*_input':
            if self._channel_name.startswith('temp'):
                self._from_str_func = _from_milli
                channel_type = DataType.TEMPERATURE
            elif self._channel_name.startswith('curr'):
                self._from_str_func = _from_milli
                channel_type = DataType.CURRENT
            elif self._channel_name.startswith('in'):
                self._from_str_func = _from_milli
                channel_type = DataType.VOLTAGE
            elif self._channel_name.startswith('power'):
                self._from_str_func = _from_milli
                channel_type = DataType.POWER
            elif self._channel_name.startswith('humidity'):
                self._from_str_func = _from_milli
                channel_type = DataType.HUMIDITY
            elif self._channel_name.startswith('fan'):
                self._from_str_func = int
                channel_type = DataType.RPM

        elif channel_type in {'*_enable', '*_alarm', 'buzzer*', 'relay*'}:
            self._from_str_func = _to_bool
            self._to_str_func = _from_bool
            channel_type = DataType.BOOLEAN

        elif channel_type == 'pwm*':
            self._from_str_func = int
            self._to_str_func = _to_byte
            channel_type = DataType.BYTE

        else:
            self._from_str_func = str
            self._from_str_func = _no_write
            channel_type = DataType.UNDEFINED

        # Find description
        desc = channel_path.name
        parent = channel_path.parent
        labelfile = parent / (self._channel_name + '_label')
        if labelfile.is_file():
            desc = labelfile.read_text().strip()
        elif '_' in self._channel_name:
            pos = self._channel_name.rindex('_')
            labelfile = parent / (self._channel_name[:pos] + '_label')
            if labelfile.is_file():
                desc = labelfile.read_text().strip()

        Property.__init__(self, datatype=channel_type, desc=desc, persistent=False)

    def _read(self):
        try:
            return self._from_str_func(self._channel_path.read_text())

        except Exception as e:
            logger.error('Failed to read from HWMon channel %s: %s', self._channel_path, repr(e))

    def _cached_value(self) -> Any:
        # Just return previously written (cached) value
        return super().value

    def _write(self, value, attempt=1):
        try:
            self._channel_path.write_text(str(value))
            Property.value.fset(self, value)

        except Exception as e:
            logger.error('Failed to write to HWMon channel %s: %s', self._channel_path, repr(e))

        if attempt > 5:
            raise IOError('Writing to HWMon channel failed 5 times: ' + str(self._channel_path))

        # Retry
        self._write(value, attempt+1)


class HWMonChannelInput(HWMonChannel):
    value = property(fget=HWMonChannel._read)


class HWMonChannelOutput(HWMonChannel):
    value = property(fget=HWMonChannel._read, fset=HWMonChannel._write)


class HWMonDevice(Property):
    __slots__ = ()

    def __init__(self, sensor_dir: Path):
        pd = PropertyDict()

        Property.__init__(self, datatype=DataType.PROPERTYDICT, initial_value=pd, desc='HWMon compatible device')

        for channel_type in ('*_input', '*_alarm', '*_enable', 'pwm*', 'buzzer*', 'relay*'):
            for channel_file in sensor_dir.glob(channel_type):
                if channel_file.name.endswith('_label'):
                    continue

                hwm_class = HWMonChannelOutput if channel_file.stat().st_mode & 0o222 else HWMonChannelInput
                pd[channel_file.name] = hwm_class(channel_file, channel_type)


class HWMon(ModuleBase):
    """HWMon interface module"""

    allow_maininstance = True
    allow_instances = False
    description = 'HWMon interface'
    categories = 'Sensors', 'Hardware'

    @classmethod
    def available(cls) -> bool:
        return _hwmon_devices_path.is_dir()

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)

        for sensor_dir in _hwmon_devices_path.glob('hwmon*'):
            name_file = sensor_dir / 'name'
            if not name_file.is_file():
                logger.error('File not found: %s', name_file)
                continue

            sensor_name = name_file.read_text().strip()
            self.properties[sensor_name] = HWMonDevice(sensor_dir)

    def load(self):
        pass

    def unload(self):
        pass
