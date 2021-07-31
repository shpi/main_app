# -*- coding: utf-8 -*-

# https://elinux.org/images/b/ba/ELC_2017_-_Industrial_IO_and_You-_Nonsense_Hacks%21.pdf

from logging import getLogger
from pathlib import Path
from typing import Generator, Dict, Any, List, Type

import core.iio as iio
from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import PropertyDict, Property, ROProperty


logger = getLogger(__name__)


"""
=== dev: mlx90615 <class 'core.iio.Device'> ===
  attr: name= current_timestamp_clock <class 'core.iio.DeviceAttr'> = realtime <class 'str'>
  channel: id= temp_ambient <class 'core.iio.Channel'>
    attr: offset <class 'core.iio.ChannelAttr'> = -13657.500000 <class 'str'>
    attr: raw <class 'core.iio.ChannelAttr'> = 15433 <class 'str'>
    attr: scale <class 'core.iio.ChannelAttr'> = 20 <class 'str'>
  channel: id= temp_object <class 'core.iio.Channel'>
    attr: calibemissivity <class 'core.iio.ChannelAttr'> = 1.000000000 <class 'str'>
    attr: filter_low_pass_3db_frequency <class 'core.iio.ChannelAttr'> = 1.000000 <class 'str'>
    attr: filter_low_pass_3db_frequency_available <class 'core.iio.ChannelAttr'> = 1.0 0.5 0.33 0.25 0.2 0.16 0.14 <class 'str'>
    attr: offset <class 'core.iio.ChannelAttr'> = -13657.500000 <class 'str'>
    attr: raw <class 'core.iio.ChannelAttr'> = 15176 <class 'str'>
    attr: scale <class 'core.iio.ChannelAttr'> = 20 <class 'str'>
  channel: id= timestamp <class 'core.iio.Channel'>
=== dev: bh1750 <class 'core.iio.Device'> ===
  attr: name= integration_time_available <class 'core.iio.DeviceAttr'> = 0.053940 0.055680 0.057420 0.059160 0.060900 0.062640 0.064380 0.066120 0.067860 0.069600 0.071340 0.073080 0.074820 0.076560 0.078300 0.080040 0.081780 0.083520 0.085260 0.087000 0.088740 0.090480 0.092220 0.093960 0.095700 0.097440 0.099180 0.100920 0.102660 0.104400 0.106140 0.107880 0.109620 0.111360 0.113100 0.114840 0.116580 0.118320 0.120060 0.121800 0.123540 0.125280 0.127020 0.128760 0.130500 0.132240 0.133980 0.135720 0.137460 0.139200 0.140940 0.142680 0.144420 0.146160 0.147900 0.149640 0.151380 0.153120 0.154860 0.156600 0.158340 0.160080 0.161820 0.163560 0.165300 0.167040 0.168780 0.170520 0.172260 0.174000 0.175740 0.177480 0.179220 0.180960 0.182700 0.184440 0.186180 0.187920 0.189660 0.191400 0.193140 0.194880 0.196620 0.198360 0.200100 0.201840 0.203580 0.205320 0.207060 0.208800 0.210540 0.212280 0.214020 0.215760 0.217500 0.219240 0.220980 0.222720 0.224460 0.226200 0.227940 0.229680 0.231420 0.233160 0.234900 0.236640 0.238380 0.240120 0.241860 0.243600 0.245340 0.247080 0.248820 0.250560 0.252300 0.254040 0.255780 0.257520 0.259260 0.261000 0.262740 0.264480 0.266220 0.267960 0.269700 0.271440 0.273180 0.274920 0.276660 0.278400 0.280140 0.281880 0.283620 0.285360 0.287100 0.288840 0.290580 0.292320 0.294060 0.295800 0.297540 0.299280 0.301020 0.302760 0.304500 0.306240 0.307980 0.309720 0.311460 0.313200 0.314940 0.316680 0.318420 0.320160 0.321900 0.323640 0.325380 0.327120 0.328860 0.330600 0.332340 0.334080 0.335820 0.337560 0.339300 0.341040 0.342780 0.344520 0.346260 0.348000 0.349740 0.351480 0.353220 0.354960 0.356700 0.358440 0.360180 0.361920 0.363660 0.365400 0.367140 0.368880 0.370620 0.372360 0.374100 0.375840 0.377580 0.379320 0.381060 0.382800 0.384540 0.386280 0.388020 0.389760 0.391500 0.393240 0.394980 0.396720 0.398460 0.400200 0.401940 0.403680 0.405420 0.407160 0.408900 0.410640 0.412380 0.414120 0.415860 0.417600 0.419340 0.421080 0.422820 0.424560 0.426300 0.428040 0.429780 0.431520 0.433260 0.435000 0.436740 0.438480 0.440220 0.441960 <class 'str'>
  channel: id= illuminance <class 'core.iio.Channel'>
    attr: integration_time <class 'core.iio.ChannelAttr'> = 0.120060 <class 'str'>
    attr: raw <class 'core.iio.ChannelAttr'> = 3 <class 'str'>
    attr: scale <class 'core.iio.ChannelAttr'> = 0.833333 <class 'str'>
=== dev: bmp280 <class 'core.iio.Device'> ===
  channel: id= pressure <class 'core.iio.Channel'>
    attr: input <class 'core.iio.ChannelAttr'> = 99.969753906 <class 'str'>
    attr: oversampling_ratio <class 'core.iio.ChannelAttr'> = 16 <class 'str'>
  channel: id= temp <class 'core.iio.Channel'>
    attr: input <class 'core.iio.ChannelAttr'> = 34920 <class 'str'>
    attr: oversampling_ratio <class 'core.iio.ChannelAttr'> = 2 <class 'str'>
"""


def _iio_dev_dump():
    context = iio.Context('local:')
    for dev in context.devices:
        print("=== dev:", dev.name, type(dev), "===")

        for devattr_name, devattr_obj in dev.attrs.items():
            print("  attr: name=", devattr_name, type(devattr_obj), "=", devattr_obj.value.strip(), type(devattr_obj.value))

        for chan in dev.channels:
            print("  channel: id=", chan.id, type(chan))
            for attr, attr_obj in chan.attrs.items():
                print("    attr:", attr, type(attr_obj), "=", attr_obj.value.strip(), type(attr_obj.value))


class IioChannelAttribute(Property):
    __slots__ = '_attr', '_file'

    _eventids = ()  # No event manager

    def __init__(self, channel: iio.Channel, attr: iio.ChannelAttr):
        if type(self) is IioChannelAttribute:
            raise TypeError('Cant instantiate IioChannelAttribute directly.')

        self._attr = attr

        file = Path('/sys/bus/iio/devices', channel.device.id, attr.filename)
        self._file = file.resolve()  # Save resolved path.
        if not self._file.exists():
            raise FileNotFoundError('File does not exists: "{}" (resolved from "{}")'.format(self._file, file))

        output = isinstance(self, IioOutputChannelAttribute)
        Property.__init__(self,
                          datatype=DataType.iio_to_shpi(channel.type),
                          desc='Output channel attribute' if output else 'Input channel attribute',
                          persistent=False)

    def _get_value(self, attempt=1) -> Any:
        try:
            v = self._file.read_text().strip()
            return DataType.str_to_tight_datatype(v)
        except Exception as e:
            logger.error('Failed to read from iio channel %s: %s', repr(self), repr(e))

        if attempt > 5:
            raise IOError('Reading from iio channel failed 5 times: ' + repr(self))
        # Retry
        return self._get_value(attempt+1)

    def _get_cached_value(self) -> Any:
        # Just return previously written (cached) value
        return super().value

    def _set_value(self, newvalue: Any, attempt=1):
        try:
            self._file.write_text(str(newvalue))
            Property.value.fset(self, newvalue)
        except Exception as e:
            logger.error('Failed to write to iio channel %s: %s', repr(self), repr(e))

        if attempt > 5:
            raise IOError('Writing to iio channel failed 5 times: ' + repr(self))
        # Retry
        self._set_value(newvalue, attempt+1)


class IioInputChannelAttribute(IioChannelAttribute):
    value = property(fget=IioChannelAttribute._get_value)


class IioOutputChannelAttribute(IioChannelAttribute):
    value = property(fget=IioChannelAttribute._get_cached_value, fset=IioChannelAttribute._set_value)


class IioChannel(Property):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, channel: iio.Channel, description: str, chan_attr_class: Type[Any]):
        if type(self) is IioChannel:
            raise TypeError('Cant instantiate IioChannel directly.')

        attr_pd = PropertyDict()
        Property.__init__(self, datatype=DataType.PROPERTYDICT, initial_value=attr_pd, desc=description)

        for attr_name, attr in channel.attrs.items():  # type: str, iio.ChannelAttr
            attr_pd[attr_name] = chan_attr_class(channel, attr)


class IioInputChannel(IioChannel):
    __slots__ = ()

    def __init__(self, channel: iio.Channel):
        IioChannel.__init__(self, channel, 'Input channel', IioInputChannelAttribute)


class IioOutputChannel(IioChannel):
    __slots__ = ()

    def __init__(self, channel: iio.Channel):
        IioChannel.__init__(self, channel, 'Output channel', IioOutputChannelAttribute)


class IioDevAttribute(Property):
    __slots__ = '_attr', '_is_device_attr', '_is_available'

    _eventids = ()  # No event manager

    def __init__(self, attr: iio._Attr, is_device_attr: bool):
        self._attr = attr

        self._is_device_attr = is_device_attr
        self._is_available = isinstance(attr.name, str) and attr.name.endswith('_available')
        if self._is_available:
            Property.__init__(self, DataType.LIST_OF_STRINGS, None, desc=f'Available attribute "{attr.name}"',
                              persistent=False)
        else:
            Property.__init__(self, DataType.STRING if is_device_attr else DataType.FLOAT,
                              desc=f'Attribute "{attr.name}"', persistent=False)

    @property
    def value(self) -> Any:
        if self._is_available:
            # Expect list of strings
            return self._attr._read().strip().split()

        if self._is_device_attr:
            # Expect string
            return self._attr._read().strip()

        # Expect int/float -> float
        return float(self._attr._read())

    @value.setter
    def value(self, newvalue: Any):
        if self._is_available:
            raise TypeError('Cannot write to "available" attributes.')

        if self._is_device_attr:
            # Expect string
            value_str = str(newvalue).strip()

        # Expect int/float
        elif isinstance(newvalue, int):
            # value = float(newvalue)
            value_str = str(newvalue)
        elif isinstance(newvalue, float):
            # value = newvalue
            if newvalue.is_integer():
                # Write as integer without decimal dot
                value_str = str(int(newvalue))
            else:
                value_str = str(newvalue)
        else:
            # string or something else
            value_str = str(newvalue).strip()
            # value = value_str

        # Property.value.fset(self, value)
        self._attr._write(value_str + '\n')


class IioDevAttributes(Property):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, attrs: Dict[str, iio.DeviceAttr]):
        devattr_pd = PropertyDict()
        Property.__init__(self, datatype=DataType.PROPERTYDICT, initial_value=devattr_pd, desc='IIO device attributes')

        for device_attr_name, device_attr in attrs.items():
            devattr_pd[device_attr_name] = IioDevAttribute(device_attr, True)


class IioDevBufferAttributes(Property):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, attrs: Dict[str, iio.DeviceBufferAttr]):
        devattr_pd = PropertyDict()
        Property.__init__(self, datatype=DataType.PROPERTYDICT, initial_value=devattr_pd, desc='IIO device buffer attributes')

        for device_attr_name, device_attr in attrs.items():
            devattr_pd[device_attr_name] = IioDevAttribute(device_attr, True)


class IioDevChannels(Property):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, channels: List[iio.Channel]):
        chan_pd = PropertyDict()
        Property.__init__(self, datatype=DataType.PROPERTYDICT, initial_value=chan_pd, desc='IIO device channels')

        for channel in channels:
            if channel.output:
                chan_pd[channel.id] = IioOutputChannel(channel)
            else:
                chan_pd[channel.id] = IioInputChannel(channel)


class IioDev(Property):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, dev: iio.Device):
        dev_pd = PropertyDict()
        Property.__init__(self, DataType.PROPERTYDICT, initial_value=dev_pd, desc='Device access to ' + dev.name)

        dev_pd['name'] = ROProperty(DataType.STRING, dev.name.strip(), desc='Device name')
        dev_pd['id'] = ROProperty(DataType.STRING, dev.id.strip(), desc='Device id')

        if dev.attrs:
            dev_pd['attributes'] = IioDevAttributes(dev.attrs)

        if dev.buffer_attrs:
            dev_pd['buffer_attributes'] = IioDevBufferAttributes(dev.buffer_attrs)

        if dev.channels:
            dev_pd['channels'] = IioDevChannels(dev.channels)


class IIO(ModuleBase):
    """IIO interface module"""

    allow_maininstance = True
    allow_instances = False
    description = 'IIO interface'
    categories = 'Sensors', 'Hardware'

    _iio_devices_path = Path('/sys/bus/iio/devices')

    @classmethod
    def available(cls) -> bool:
        return cls._iio_devices_path.is_dir()

    @classmethod
    def iio_find_device_paths(cls, with_name_file=True, name_match: str = None) -> Generator[Path, None, None]:
        """Generator to iterate over iio devices by filesystem"""

        if not cls._iio_devices_path.is_dir():
            return

        for device in cls._iio_devices_path.iterdir():
            namefile = device / 'name'

            if name_match:
                if namefile.is_file():
                    if namefile.read_text().strip() == name_match:
                        yield device
            else:
                if namefile.is_file() or not with_name_file:
                    yield device

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)

        self.context = iio.Context('local:')

        self.properties['context'] = ROProperty(DataType.STRING, self.context.description.strip(), desc='Context description')

        for dev in self.context.devices:
            name = PropertyDict.create_keyname(dev.name)
            try:
                self.properties[name] = IioDev(dev)
            except Exception as e:
                logger.error('Could not add IIO device "%s": %s', name, repr(e), exc_info=True)

    def load(self):
        pass

    def unload(self):
        del self.context
