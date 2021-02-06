# -*- coding: utf-8 -*-

from hardware.iio import ChannelType
from enum import Enum


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
    INT = 2  # any undefined int
    BOOL = 3  # bool (off/on)
    STRING = 4  # string representation of a state

    # Correct interpretation of datetime objects
    DATE = 5  # date object (without time)
    TIME = 6  # time object (without date)
    DATETIME = 7  # datetime object
    TIMERANGE = 8  # Range between two times (timedelta)
    TIMESTAMP = 9  # Seconds since poch

    # Fix range types
    PERCENT_FLOAT = 10  # float, 0.-100.
    PERCENT_INT = 11  # int, 0-100
    FRAC = 12  # float 0.-1.
    BYTE = 13  # int, 0-255
    WORD = 14  # int, 0-65535
    ENUM = 15
    MODULE = 16  # 'ok', 'error', 'not_initialized'

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
    DIRECTION = 37  # degrees 0-360′
    HEIGHT = 38  # mm

    # Electricity (from sensors)
    CURRENT = 40  # float, Ampere
    VOLTAGE = 41  # float, Volt
    RESISTANCE = 42  # float, Ohms
    CAPACITANCE = 43  # float, Farad
    INDUCTANCE = 44  # float, Henry
    POWER = 45  # float, mW (Watts)
    WORK = 46  # float, Wh (Watt-Hours)
    ENERGY = 47  # microjoule
    CONDUCTIVITY = 48  #

    # Filesystem sizes
    BYTES = 50

    # Others
    GPS_COORDS = 51
    LATITUDE = 52
    LONGITUDE = 53

    # Too special
    WEBREQUEST = 60


class Convert:
    @staticmethod
    def iio_to_shpi(iio: ChannelType):
        if iio in Convert._mapping_iio_shpi:
            return Convert._mapping_iio_shpi[iio]
        else:
            return DataType.UNDEFINED

    @staticmethod
    def type_to_str(datatype: DataType):
        if datatype in Convert._mapping_type_str:
            return Convert._mapping_type_str[datatype]
        else:
            return 'unknown'

    @staticmethod
    def str_to_type(datatype: str):

        if datatype in Convert._mapping_str_type:
            return Convert._mapping_str_type[datatype]
        else:
            return DataType.UNDEFINED

    _mapping_type_str = {DataType.UNDEFINED: 'undefined',
                         DataType.MODULE: 'module',
                         DataType.FLOAT: 'float',
                         DataType.INT: 'integer',
                         DataType.BOOL: 'boolean',
                         DataType.STRING: 'string',
                         DataType.DATE: 'date',
                         DataType.ENUM: 'enum',
                         DataType.TIME: 'time',
                         DataType.DATETIME: 'datetime',
                         DataType.TIMERANGE: 'timerange',
                         DataType.TIMESTAMP: 'timestamp',
                         DataType.PERCENT_FLOAT: 'percent_float',
                         DataType.PERCENT_INT: 'percent_int',
                         DataType.FRAC: 'fracment',
                         DataType.BYTE: 'byte',
                         DataType.WORD: 'word',
                         DataType.TEMPERATURE: 'temperature',
                         DataType.ILLUMINATION: 'illumination',
                         DataType.PRESSURE: 'pressure',
                         DataType.HUMIDITY: 'humidity',
                         DataType.PRESENCE: 'presence',
                         DataType.ONOFF: 'on_off',
                         DataType.COUNT: 'count',
                         DataType.FAN: 'fan',
                         DataType.ACCELERATION: 'acceleration',
                         DataType.VELOCITY: 'velocity',
                         DataType.MAGNETOMETER: 'magnetometer',
                         DataType.ROTATION: 'rotation',
                         DataType.PROXIMITY: 'proximity',
                         DataType.PHINDEX: 'phindex',
                         DataType.CONCENTRATION: 'concentration',
                         DataType.UVINDEX: 'uvindex',
                         DataType.GRAVITY: 'gravity',
                         DataType.CURRENT: 'current',
                         DataType.VOLTAGE: 'voltage',
                         DataType.RESISTANCE: 'resistance',
                         DataType.CAPACITANCE: 'capacitance',
                         DataType.INDUCTANCE: 'inductance',
                         DataType.POWER: 'power',
                         DataType.WORK: 'work',
                         DataType.ENERGY: 'energy',
                         DataType.CONDUCTIVITY: 'conductivity',
                         DataType.BYTES: 'bytes',
                         DataType.GPS_COORDS: 'gps_coordinates',
                         DataType.LATITUDE: 'latitude',
                         DataType.LONGITUDE: 'longitude',
                         DataType.WEBREQUEST: 'webrequest'}

    _mapping_str_type = {value: key for (key, value) in _mapping_type_str.items()}

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
        ChannelType.IIO_STEPS: DataType.COUNT,
        ChannelType.IIO_ENERGY: DataType.ENERGY,
        ChannelType.IIO_DISTANCE: DataType.PROXIMITY,  # ??
        ChannelType.IIO_VELOCITY: DataType.VELOCITY,
        ChannelType.IIO_CONCENTRATION: DataType.CONCENTRATION,
        ChannelType.IIO_RESISTANCE: DataType.RESISTANCE,
        ChannelType.IIO_PH: DataType.PHINDEX,
        ChannelType.IIO_UVINDEX: DataType.UVINDEX,
        ChannelType.IIO_ELECTRICALCONDUCTIVITY: DataType.CONDUCTIVITY,
        ChannelType.IIO_COUNT: DataType.COUNT,
        ChannelType.IIO_GRAVITY: DataType.GRAVITY
    }
