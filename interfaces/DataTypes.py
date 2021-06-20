# -*- coding: utf-8 -*-

from typing import Union, Type
from enum import Enum
from datetime import datetime, date, time
from re import compile


from hardware.iio import ChannelType

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

    # Correct interpretation of datetime objects
    DATE = 5  # date object (without time)
    TIME = 6  # time object (without date)
    TIME_STR = 7  # time as string "14:00"
    DATETIME = 8  # datetime object
    TIMERANGE = 9  # Range between two times (seconds, float)
    TIMERANGE_INT = 10  # Range between two times (seconds, int)
    TIMESTAMP = 11  # Seconds since unix epoch (float)

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
    FAN = 27  # rpm
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

    @classmethod
    def type_to_str(cls, datatype: "DataType"):
        return datatype.name.lower()

    @classmethod
    def str_to_type(cls, datatype: str) -> "DataType":
        try:
            return cls[datatype.upper()]
        except TypeError:
            return cls.UNDEFINED

    _to_basic_type = {
        # default: float
        INTEGER: int,
        BOOLEAN: bool,
        STRING: str,

        DATE: date,
        TIME: time,
        TIME_STR: str,
        DATETIME: datetime,

        TIMERANGE_INT: int,

        PERCENT_INT: int,
        BYTE: int,
        WORD: int,

        PRESENCE: bool,
        ONOFF: bool,
        COUNT: int,

        BYTES: int,
        # GPS_COORDS = 51
    }

    _mapping_iio_shpi = {
        ChannelType.IIO_VOLTAGE: VOLTAGE,
        ChannelType.IIO_CURRENT: CURRENT,
        ChannelType.IIO_POWER: POWER,
        ChannelType.IIO_ACCEL: ACCELERATION,
        ChannelType.IIO_MAGN: MAGNETOMETER,
        ChannelType.IIO_LIGHT: ILLUMINATION,
        ChannelType.IIO_INTENSITY: ILLUMINATION,
        ChannelType.IIO_PROXIMITY: PROXIMITY,
        ChannelType.IIO_TEMP: TEMPERATURE,
        ChannelType.IIO_ROT: ROTATION,
        ChannelType.IIO_ANGL: ROTATION,
        ChannelType.IIO_TIMESTAMP: TIMESTAMP,
        ChannelType.IIO_CAPACITANCE: CAPACITANCE,
        ChannelType.IIO_PRESSURE: PRESSURE,
        ChannelType.IIO_HUMIDITYRELATIVE: HUMIDITY,
        ChannelType.IIO_STEPS: INTEGER,
        ChannelType.IIO_ENERGY: WORK,
        ChannelType.IIO_DISTANCE: LENGTH,
        ChannelType.IIO_VELOCITY: VELOCITY,
        ChannelType.IIO_CONCENTRATION: CONCENTRATION,
        ChannelType.IIO_RESISTANCE: RESISTANCE,
        ChannelType.IIO_PH: PHINDEX,
        ChannelType.IIO_UVINDEX: UVINDEX,
        ChannelType.IIO_ELECTRICALCONDUCTIVITY: CONDUCTIVITY,
        ChannelType.IIO_COUNT: INTEGER,
        ChannelType.IIO_GRAVITY: GRAVITY
    }

    _valid_check = {
        TIME_STR: _re_time_str.fullmatch,
        PERCENT_FLOAT: lambda x: 0. <= x <= 100.,
        PERCENT_INT: lambda x: x in range(101),
        FRACTION: lambda x: 0. <= x <= 1.,
        BYTE: lambda x: x in range(256),
        WORD: lambda x: x in range(65536),
        BYTES: lambda x: x >= 0,
    }

    @classmethod
    def iio_to_shpi(cls, iio: ChannelType) -> "DataType":
        return cls._mapping_iio_shpi.value.get(iio.value, DataType.UNDEFINED)

    @classmethod
    def to_basic_type(cls, type_: "DataType") -> Type[Union[int, str, bool, float, date, time, datetime]]:
        return cls._to_basic_type.value.get(type_.value, float)

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
