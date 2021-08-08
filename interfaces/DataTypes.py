# -*- coding: utf-8 -*-

from typing import Union, Type
from enum import Enum
from datetime import datetime, date, time
from re import compile

from core.iio import ChannelType

_re_time_str = compile(r'(2[0-3]|[01]?[0-9]):([0-5]?[0-9])')


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
    TIME_STR = 9  # time as string "14:00"
    DATETIME = 10  # datetime object
    TIMEDELTA = 11  # Range between two times (seconds, float)
    TIMEDELTA_INT = 12  # Range between two times (seconds, int)
    TIMESTAMP = 13  # Seconds since unix epoch (float)

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
    DataType.TIME_STR: _re_time_str.fullmatch,
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
    DataType.TIME_STR: str,
    DataType.DATETIME: datetime,

    DataType.TIMEDELTA_INT: int,

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


def datatype_from_iio(iio: ChannelType) -> "DataType":
    return _mapping_iio_shpi.get(iio, DataType.UNDEFINED)


def datatype_to_basic_type(datatype: "DataType") -> Type[Union[int, str, bool, float, date, time, datetime, list]]:
    return _to_basic_type.get(datatype, float)
