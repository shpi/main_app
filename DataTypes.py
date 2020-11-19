class DataType(Enum):
    """
    Define property values with a data type allows them to get announced and accessed easier.
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
    TIMESTAMP = 9 # seconds since poch

    # Fix range types
    PERCENT_FLOAT = 10  # float, 0.-100.
    PERCENT_INT = 11  # int, 0-100
    FRAC = 12  # float 0.-1.
    BYTE = 13  # int, 0-255
    WORD = 14  # int, 0-65535

    # Special types (from sensors)
    TEMPERATURE = 20  # float, Celsius
    ILLUMINATION = 21  # float, Lux
    PRESSURE = 22  # float, hPa
    HUMIDITY = 23  # float, 0-100
    PRESENCE = 24  # bool
    ONOFF = 25  # bool
    COUNT = 26 # integer
    FAN = 27 # rpm
    ACCELERATION = 28 # m seconds squared
    VELOCITY = 29 # meter per second
    MAGNETOMETER = 30 # milli gauss
    ROTATION = 31 # degrees
    PROXIMITY = 32 # meters
    PHINDEX = 33 # -1.0  ... 15.0
    CONCENTRATION = 34 # parts per million
    UVINDEX = 35 #
    GRAVITY = 36 #

    # Electricity (from sensors)
    CURRENT = 40  # float, Ampere
    VOLTAGE = 41  # float, Volt
    RESISTANCE = 42  # float, Ohms
    CAPACITANCE = 43  # float, Farad
    INDUCTANCE = 44  # float, Henry
    POWER = 45  # float, mW (Watts)
    WORK = 46  # float, Wh (Watt-Hours)
    ENERGY = 47 # microjoule
    CONDUCTIVITY = 48 #

    # Filesystem sizes
    BYTES = 50

    # Others
    GPS_COORDS = 51
    LATITUDE = 52
    LONGITUDE = 53

    # Too special
    WEBREQUEST = 60


from iio import ChannelType

class Convert:

    _mapping_iio_shpi = {


ChannelType.IIO_VOLTAGE : DataType.VOLTAGE,
ChannelType.IIO_CURRENT = 1
ChannelType.IIO_POWER = 2
ChannelType.IIO_ACCEL = 3
ChannelType.IIO_MAGN = 5
ChannelType.IIO_LIGHT = 6     ??
ChannelType.IIO_INTENSITY = 7 ??
ChannelType.IIO_PROXIMITY = 8
    IIO_TEMP = 9
    IIO_ROT = 11
    IIO_ANGL = 12
    IIO_TIMESTAMP = 13
    IIO_CAPACITANCE = 14
    IIO_PRESSURE = 17
    IIO_HUMIDITYRELATIVE = 18
    IIO_STEPS = 20
    IIO_ENERGY = 21
    IIO_DISTANCE = 22
    IIO_VELOCITY = 23
    IIO_CONCENTRATION = 24
    IIO_RESISTANCE = 25
    IIO_PH = 26
    IIO_UVINDEX = 27
    IIO_ELECTRICALCONDUCTIVITY = 28
    IIO_COUNT = 29
    IIO_GRAVITY = 31

