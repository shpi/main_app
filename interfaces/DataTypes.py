# -*- coding: utf-8 -*-

import locale
from typing import Union, Type
from enum import Enum, EnumMeta
from datetime import datetime, date, time
from re import compile


from core.iio import ChannelType

_re_time_str = compile(r'(2[0-3]|[01]?[0-9]):([0-5]?[0-9])')


class _Localization:
    _bytype = {
        datetime: 0,
        date: 1,
        time: 2,
    }

    def __init__(self):
        self._fmts = [
            locale.nl_langinfo(locale.D_T_FMT),
            locale.nl_langinfo(locale.D_FMT),
            locale.nl_langinfo(locale.T_FMT)
        ]

    def to_local_string(self, obj: Union[datetime, date, time]) -> str:
        index = self._bytype.get(type(obj))
        if index is None:
            return 'None'

        return obj.strftime(self._fmts[index])


localization = _Localization()


class DataType(Enum):
    """
    Define property values with a data type allows them to
    get announced and accessed easier.
    Also checks and conversions may rely on that.
    """

    # Fallback
    UNDEFINED = 0  # Bad idea. Always specify.

    # Generic types
    FLOAT = 1  # any undefined float
    INTEGER = 2  # any undefined int
    BOOLEAN = 3  # bool (off/on)
    STRING = 4  # string representation of a state
    LIST_OF_STRINGS = 5  # List of strings

    # Correct interpretation of datetime objects
    DATE = 7  # date object (without time)
    TIME = 8  # time object (without date)
    DATETIME = 9  # datetime object

    TIMEDELTA = 11  # Range between two times (seconds, float)
    TIMESTAMP = 12  # Seconds since unix epoch (utc, float)

    # Fix range types
    PERCENT_FLOAT = 15  # float, 0.-100.
    PERCENT_INT = 16  # int, 0-100
    FRACTION = 17  # float 0.-1.
    BYTE = 18  # int, 0-255
    WORD = 19  # int, 0-65535

    # Special types (from sensors)
    TEMPERATURE = 20  # float, Celsius
    ILLUMINATION = 21  # float, Lux
    PRESSURE = 22  # float, hPa
    HUMIDITY = 23  # float, 0-100
    PRESENCE = 24  # bool
    ONOFF = 25  # bool
    COUNT = 26  # integer
    RPM = 27  # rpm, int
    ACCELERATION = 28  # m seconds squared
    VELOCITY = 29  # meter per second
    MAGNETOMETER = 30  # milli gauss
    ROTATION = 31  # degrees
    PROXIMITY = 32  # meters
    PHINDEX = 33  # -1.0  ... 15.0
    CONCENTRATION = 34  # parts per million
    UVINDEX = 35  #
    GRAVITY = 36  #
    DIRECTION = 37  # degrees 0-360°
    LENGTH = 38  # mm
    FREQUENCY = 39  # Hz, float

    # Electricity (from sensors)
    CURRENT = 40  # float, Ampere
    VOLTAGE = 41  # float, Volt
    RESISTANCE = 42  # float, Ohms
    CAPACITANCE = 43  # float, Farad
    INDUCTANCE = 44  # float, Henry
    POWER = 45  # float, W (Watts)
    WORK = 46  # float, Wh (Watt-Hours)
    CONDUCTIVITY = 47  # S/m Siemens per meter

    # Filesystem sizes
    BYTES = 50

    # Others
    GPS_COORDS = 51
    LATITUDE = 52
    LONGITUDE = 53

    # Too special
    PROPERTYDICT = 60
    ENUM = 61  # Value should be displayable text.

    @classmethod
    def type_to_str(cls, datatype: "DataType"):
        return datatype.name.lower()

    @classmethod
    def str_to_type(cls, datatype: str) -> "DataType":
        try:
            return cls[datatype.upper()]
        except TypeError:
            return cls.UNDEFINED

    @staticmethod
    def str_to_tight_datatype(numeric: str):
        try:
            if "." in numeric:
                # Seems to be a float.
                return float(numeric)

            return int(numeric)

        except ValueError:
            # Use the string
            return numeric

        # else raise error
        # except TypeError:
        #    # No string provided?
        #    return str(numeric)


_valid_check = {
    # ToDo: use validity checks
    DataType.PERCENT_FLOAT: lambda x: 0. <= x <= 100.,
    DataType.PERCENT_INT: lambda x: x in range(101),
    DataType.FRACTION: lambda x: 0. <= x <= 1.,
    DataType.BYTE: lambda x: x in range(256),
    DataType.WORD: lambda x: x in range(65536),
    DataType.BYTES: lambda x: x >= 0,
}


_to_basic_type = {
    # default: float
    DataType.INTEGER: int,
    DataType.BOOLEAN: bool,
    DataType.STRING: str,

    DataType.DATE: date,
    DataType.TIME: time,
    DataType.DATETIME: datetime,

    DataType.PERCENT_INT: int,
    DataType.BYTE: int,
    DataType.WORD: int,

    DataType.PRESENCE: bool,
    DataType.ONOFF: bool,
    DataType.COUNT: int,
    DataType.RPM: int,

    DataType.BYTES: int,
    DataType.ENUM: str,

    DataType.LIST_OF_STRINGS: list,
    DataType.PROPERTYDICT: None,
}


_mapping_iio_shpi = {
    ChannelType.IIO_VOLTAGE: DataType.VOLTAGE,
    ChannelType.IIO_CURRENT: DataType.CURRENT,
    ChannelType.IIO_POWER: DataType.POWER,
    ChannelType.IIO_ACCEL: DataType.ACCELERATION,
    ChannelType.IIO_MAGN: DataType.MAGNETOMETER,
    ChannelType.IIO_LIGHT: DataType.ILLUMINATION,
    ChannelType.IIO_INTENSITY: DataType.ILLUMINATION,
    ChannelType.IIO_PROXIMITY: DataType.PROXIMITY,
    ChannelType.IIO_TEMP: DataType.TEMPERATURE,
    ChannelType.IIO_ROT: DataType.ROTATION,
    ChannelType.IIO_ANGL: DataType.ROTATION,
    ChannelType.IIO_TIMESTAMP: DataType.TIMESTAMP,
    ChannelType.IIO_CAPACITANCE: DataType.CAPACITANCE,
    ChannelType.IIO_PRESSURE: DataType.PRESSURE,
    ChannelType.IIO_HUMIDITYRELATIVE: DataType.HUMIDITY,
    ChannelType.IIO_STEPS: DataType.INTEGER,
    ChannelType.IIO_ENERGY: DataType.WORK,
    ChannelType.IIO_DISTANCE: DataType.LENGTH,
    ChannelType.IIO_VELOCITY: DataType.VELOCITY,
    ChannelType.IIO_CONCENTRATION: DataType.CONCENTRATION,
    ChannelType.IIO_RESISTANCE: DataType.RESISTANCE,
    ChannelType.IIO_PH: DataType.PHINDEX,
    ChannelType.IIO_UVINDEX: DataType.UVINDEX,
    ChannelType.IIO_ELECTRICALCONDUCTIVITY: DataType.CONDUCTIVITY,
    ChannelType.IIO_COUNT: DataType.INTEGER,
    ChannelType.IIO_GRAVITY: DataType.GRAVITY
}


def _celsius(value):
    if not isinstance(value, (float, int)):
        return str(value)
    return str(value) + ' °C'


def _enum(value):
    if type(type(value)) is EnumMeta:
        return str(value)
    return value.name


def _bytes(value):
    if not isinstance(value, (float, int)):
        return str(value)

    if value < 1024:  # less than 1kB
        return str(value)

    if value < 1048576:  # less than 1MB
        return str(round(value / 1024, 2)) + ' KiB'

    if value < 1073741824:  # less than 1GB
        return str(round(value / 1048576, 2)) + ' MiB'

    if value < 1099511627776:  # less than 1TB
        return str(round(value / 1073741824, 4)) + ' GiB'

    # >= 1 TeraByte
    return str(round(value / 1099511627776, 4)) + ' TiB'


def _list_of_strings(value):
    if not isinstance(value, (list, tuple, set, frozenset)):
        return str(value)

    return ', '.join(value)


def _percent(value):
    if not isinstance(value, (int, float)):
        return str(value)

    if type(value) is float:
        value = round(value, 2)

    return str(value) + '%'


def _append_unit(unit: str):
    def _append(value):
        return str(value) + ' ' + unit
    return _append


def _append_autobase_unit(unit: str):
    def _append(value):
        if value == 0:
            return '0 ' + unit

        neg = '-' if value < 0 else ''
        value = abs(value)

        if value > 1:
            if value < 1000:
                return neg + str(round(value, 2)) + ' ' + unit

            if value < 1000000:
                return neg + str(round(value / 1000, 2)) + ' k' + unit

            if value < 1000000000:
                return neg + str(round(value / 1000000, 4)) + ' M' + unit

            return neg + str(round(value / 1000000000, 6)) + ' G' + unit

        else:
            # less than 1
            if value > 0.001:
                return neg + str(round(value * 1000)) + ' m' + unit

            if value > 0.000001:
                return neg + str(round(value * 1000000)) + ' µ' + unit

            if value > 0.000000001:
                return neg + str(round(value * 1000000000)) + ' n' + unit

            return neg + str(round(value * 1000000000000)) + ' p' + unit

    return _append


def _from_timestamp(ts: float) -> str:
    if not isinstance(ts, (int, float)):
        return str(ts)

    dt = datetime.fromtimestamp(ts)
    return localization.to_local_string(dt)


datatype_tohuman_func = {
    DataType.TEMPERATURE: _append_unit('°C'),
    DataType.RPM: _append_unit('rpm'),
    DataType.ENUM: _enum,
    DataType.BYTES: _bytes,
    DataType.LIST_OF_STRINGS: _list_of_strings,
    DataType.PERCENT_FLOAT: _percent,
    DataType.PERCENT_INT: _percent,
    DataType.FREQUENCY: _append_autobase_unit('Hz'),
    DataType.VOLTAGE: _append_autobase_unit('V'),
    DataType.CURRENT: _append_autobase_unit('A'),
    DataType.POWER: _append_autobase_unit('W'),
    DataType.WORK: _append_autobase_unit('Wh'),
    DataType.TIMESTAMP: _from_timestamp,
    DataType.DATETIME: localization.to_local_string,
    DataType.TIME: localization.to_local_string,
    DataType.DATE: localization.to_local_string,
}


def datatype_from_iio(iio: ChannelType) -> "DataType":
    return _mapping_iio_shpi.get(iio, DataType.UNDEFINED)


def datatype_to_basic_type(datatype: "DataType") -> Type[Union[int, str, bool, float, date, time, datetime, list]]:
    return _to_basic_type.get(datatype, float)
