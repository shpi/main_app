# -*- coding: utf-8 -*-

from typing import Union, Type
from enum import Enum
from datetime import datetime, date, time

from hardware.iio import ChannelType


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
    DATETIME = 7  # datetime object
    TIMERANGE = 8  # Range between two times (seconds, float)
    TIMESTAMP = 9  # Seconds since poch

    # Fix range types
    PERCENT_FLOAT = 10  # float, 0.-100.
    PERCENT_INT = 11  # int, 0-100
    FRACTION = 12  # float 0.-1.
    BYTE = 13  # int, 0-255
    WORD = 14  # int, 0-65535

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
    CONDUCTIVITY = 47  # S/m Siemsns per meter

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
        DATETIME: datetime,

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

    @classmethod
    def iio_to_shpi(cls, iio: ChannelType) -> "DataType":
        return cls._mapping_iio_shpi.value.get(iio.value, DataType.UNDEFINED)

    @classmethod
    def to_basic_type(cls, type_: "DataType") -> Type[Union[int, str, bool, float]]:
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
