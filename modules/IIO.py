# -*- coding: utf-8 -*-

# https://elinux.org/images/b/ba/ELC_2017_-_Industrial_IO_and_You-_Nonsense_Hacks%21.pdf

from logging import getLogger
from pathlib import Path
from typing import Generator, Dict, Any, List, Optional

import core.iio as iio
from interfaces.DataTypes import DataType, datatype_from_iio, datatype_to_basic_type
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import PropertyDict, Property, ROProperty, Input, Function, PropertyDictProperty


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


def _datatype_from_name(name: str) -> DataType:
    if name in {'raw'}:
        return DataType.INTEGER

    if name in {'offset', 'scale', 'calibemissivity', 'input'}:
        return DataType.FLOAT

    if name.endswith('_frequency'):
        return DataType.FREQUENCY

    if name.endswith('_time'):
        return DataType.TIMEDELTA

    if name.endswith('_ratio'):
        return DataType.INTEGER

    if name.endswith('_available'):
        return DataType.LIST_OF_STRINGS

    return DataType.UNDEFINED


def _floatprec_from_name(name: str) -> Optional[int]:
    if name in {'calibemissivity', 'input'}:
        return 9

    if name in {'offset', 'scale'} or name.endswith('_time') or name.endswith('_frequency'):
        return 6

    return None


def _poll_interval_from_name(name: str):
    if name.endswith('offset'):
        return None
    if name.endswith('scale'):
        return None
    if name.endswith('_available'):
        return None
    return 10


class IioChannelAttribute(Property):
    __slots__ = '_attr', '_file'

    _eventids = ()  # No event manager

    def __init__(self, channel: iio.Channel, attr: iio.ChannelAttr, iio_output: bool):
        self._attr = attr

        file = Path('/sys/bus/iio/devices', channel.device.id, attr.filename)
        self._file = file.resolve()  # Save resolved path.
        if not self._file.exists():
            raise FileNotFoundError('File does not exists: "{}" (resolved from "{}")'.format(self._file, file))

        datatype = _datatype_from_name(attr.name)

        if iio_output:
            Property.__init__(self, Input, datatype, desc='Output channel attribute', persistent=False)
            # Standard: self._getfunc = self._from_cache
            self._getfunc = self._read_sync_cache

        else:
            def_time = _poll_interval_from_name(attr.name)
            # print(attr.name, def_time)
            Property.__init__(self, Function, datatype, self._read_channel,
                              desc='Input channel attribute', function_poll_min_def=(1, def_time))

        if datatype_to_basic_type(datatype) is float:
            prec = _floatprec_from_name(attr.name)
            if prec is not None:
                self._floatprec_default = prec

    def _read_sync_cache(self):
        res = self._read_channel()

        if res != self._from_cache():
            # Sync cache
            Property._set_value(self, res)

        return res

    def _set_value(self, newvalue):
        with self._lock:
            self._write_channel(newvalue)
            Property._set_value(self, newvalue)

    def _read_channel(self, attempt=1) -> Any:
        try:
            v = self._file.read_text().strip()
            # print("_read_channel", self._file, v)
            return DataType.str_to_tight_datatype(v)
        except Exception as e:
            logger.error('Failed to read from iio channel %s: %s', repr(self), repr(e))

        if attempt > 5:
            raise IOError('Reading from iio channel failed 5 times: ' + repr(self))
        # Retry
        return self._read_channel(attempt+1)

    def _write_channel(self, newvalue: Any, attempt=1):
        try:
            self._file.write_text(str(newvalue))
        except Exception as e:
            logger.error('Failed to write to iio channel %s: %s', repr(self), repr(e))

        if attempt > 5:
            raise IOError('Writing to iio channel failed 5 times: ' + repr(self))
        # Retry
        self._write_channel(newvalue, attempt+1)


class IioChannel(PropertyDictProperty):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, channel: iio.Channel, description: str, iio_output: bool):
        attr_pd = PropertyDict()
        PropertyDictProperty.__init__(self, attr_pd, desc=description)

        for attr_name, attr in channel.attrs.items():  # type: str, iio.ChannelAttr
            attr_pd[attr_name] = IioChannelAttribute(channel, attr, iio_output)


class PathProperty(Property):
    __slots__ = '_iopath',

    def __init__(self, readonly: bool, path: Path, datatype: DataType = DataType.STRING, desc: str = None):
        self._iopath = path
        if not desc:
            desc = str(path)

        if readonly:
            Property.__init__(self, Function, datatype, self._read_file, desc=desc, function_poll_min_def=(1, None))
        else:
            Property.__init__(self, Input, datatype, desc=desc, persistent=False)

            # Standard: self._getfunc = self._from_cache
            self._getfunc = self._read_sync_cache

    def _read_sync_cache(self):
        res = self._read_file()

        if res != self._from_cache():
            # Sync cache
            Property._set_value(self, res)

        return res

    def _set_value(self, newvalue):
        with self._lock:
            if self._write_file(newvalue):
                Property._set_value(self, newvalue)

    def _read_file(self) -> str:
        try:
            return self._iopath.read_text()
        except Exception as e:
            logger.error('Could not write from %s: %s', self._iopath, repr(e))
            return '0'

    def _write_file(self, newvalue: str) -> bool:
        try:
            self._iopath.write_text(newvalue)
            return True
        except Exception as e:
            logger.error('Could not write into %s: %s', self._iopath, repr(e))
            return False

class PathPropertyEnable(PathProperty):
    __slots__ = '_value_on_unload'

    def __init__(self, path: Path, desc: str = None, readonly=False, value_on_unload: bool = False):
        PathProperty.__init__(self, readonly, path, datatype=DataType.BOOLEAN, desc=desc)
        self._value_on_unload = value_on_unload

    def _read_file(self) -> bool:
        return super()._read_file() != '0\n'

    def _write_file(self, newvalue: bool):
        super()._write_file('1' if newvalue else '0')

    def unload(self):
        if isinstance(self._value_on_unload, bool):
            try:
                self._write_file(self._value_on_unload)
            except Exception as e:
                logger.error('Could not set unload state:', repr(e))

        super().unload()


class PathPropertyInteger(PathProperty):
    __slots__ = ()

    def __init__(self, path: Path, desc: str, readonly=False):
        PathProperty.__init__(self, readonly, path, datatype=DataType.INTEGER, desc=desc)

    def _read_file(self) -> int:
        return int(super()._read_file())

    def _write_file(self, newvalue: int):
        super()._write_file(str(newvalue))


class IioInputChannel(IioChannel):
    __slots__ = '_pr_base', '_pr_offset', '_pr_scale', '_ch_datatype'

    def __init__(self, channel: iio.Channel):
        self._ch_datatype = datatype_from_iio(channel.type)

        IioChannel.__init__(self, channel, 'Input channel', iio_output=False)

        # Append some processing properties
        if 'raw' in self._value:
            self._value['processed'] = Property(Function, self._ch_datatype, self._from_raw,
                                                desc='Processed value from raw', function_poll_min_def=(1, None))
            self._pr_base: Property = self['raw']
            self._pr_offset: Optional[Property] = self.value.get('offset')
            self._pr_scale: Optional[Property] = self.value.get('scale')

        elif 'input' in self._value:
            self._pr_base: Property = self['input']

            self._value['processed'] = Property(Function, self._ch_datatype, self._from_input,
                                                desc='Processed value from input', function_poll_min_def=(1, 5))

        # self._value['read'] = FunctionProperty(datatype=self._ch_datatype,
        #                                       getterfunc=self._read,
        #                                       desc='Direct reading of channel')

        # self._value['read_raw'] = FunctionProperty(datatype=self._ch_datatype,
        #                                           getterfunc=self._read_raw,
        #                                           desc='Direct reading of channel')

        if channel.scan_element:
            self._value['scan_elements_enable'] = PathPropertyEnable(
                Path('/sys/bus/iio/devices', channel.device.id, 'scan_elements', f'in_{channel.id}_en'),
                'scan_element enable/disable'
            )

    def _scaled(self, unscaled):
        if self._ch_datatype is DataType.TEMPERATURE:
            return unscaled / 1000

        return unscaled

    def _from_input(self):
        v = self._pr_base.value
        return self._scaled(v)

    def _from_raw(self):
        # Scaled value = (raw + offset) * scale
        v = self._pr_base.value

        if self._pr_offset:
            v += self._pr_offset.value

        if self._pr_scale:
            v *= self._pr_scale.value

        return self._scaled(v)

    def _read(self):
        return "Not yet supported"

    def _read_raw(self):
        return "Not yet supported"


class IioOutputChannel(IioChannel):
    __slots__ = ()

    def __init__(self, channel: iio.Channel):
        IioChannel.__init__(self, channel, 'Output channel', iio_output=True)


class IioDevAttribute(Property):
    __slots__ = '_attr', '_is_device_attr', '_is_available'

    _eventids = ()  # No event manager

    def __init__(self, attr: iio._Attr, is_device_attr: bool):
        self._attr = attr

        self._is_device_attr = is_device_attr
        self._is_available = isinstance(attr.name, str) and attr.name != 'data_available' and attr.name.endswith('_available')
        if self._is_available:
            Property.__init__(self, Function, DataType.LIST_OF_STRINGS, self._read_attr,
                              desc=f'Available attribute "{attr.name}"', persistent=False,
                              function_poll_min_def=(60, None))

        else:
            Property.__init__(self, Input, DataType.STRING if is_device_attr else DataType.FLOAT,
                              desc=f'Attribute "{attr.name}"', persistent=False)

            # Standard: self._getfunc = self._from_cache
            self._getfunc = self._read_sync_cache

    def _read_sync_cache(self):
        res = self._read_attr()

        if res != self._from_cache():
            # Sync cache
            Property._set_value(self, res)

        return res

    def _set_value(self, newvalue):
        with self._lock:
            self._write_attr(newvalue)
            Property._set_value(self, newvalue)

    def _read_attr(self) -> Any:
        if self._is_available:
            # Expect list of strings
            return self._attr._read().strip().split()

        if self._is_device_attr:
            # Expect string
            return self._attr._read().strip()

        # Expect int/float -> float
        return float(self._attr._read())

    def _write_attr(self, newvalue: Any):
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


class IioDevAttributes(PropertyDictProperty):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, attrs: Dict[str, iio.DeviceAttr]):
        devattr_pd = PropertyDict()
        PropertyDictProperty.__init__(self, devattr_pd, desc='IIO device attributes')

        for device_attr_name, device_attr in attrs.items():
            devattr_pd[device_attr_name] = IioDevAttribute(device_attr, True)


class IioDevBufferAttributes(PropertyDictProperty):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, attrs: Dict[str, iio.DeviceBufferAttr]):
        devattr_pd = PropertyDict()
        PropertyDictProperty.__init__(self, devattr_pd, desc='IIO device buffer attributes')

        for device_attr_name, device_attr in attrs.items():
            devattr_pd[device_attr_name] = IioDevAttribute(device_attr, True)


class IioDevChannels(PropertyDictProperty):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, channels: List[iio.Channel]):
        chan_pd = PropertyDict()
        PropertyDictProperty.__init__(self, chan_pd, desc='IIO device channels')

        for channel in channels:
            if channel.output:
                chan_pd[channel.id] = IioOutputChannel(channel)
            else:
                chan_pd[channel.id] = IioInputChannel(channel)


class IioDevBufferLength(Property):
    __slots__ = '_enable_path', '_length_path'

    _eventids = ()  # No event manager

    def __init__(self, enable_path: Path, length_path: Path):
        self._enable_path = enable_path
        self._length_path = length_path

        Property.__init__(self, Input, DataType.INTEGER,
                          desc='Enable buffer / buffer length. 0=Disabled', persistent=False)

        # Standard: self._getfunc = self._from_cache
        self._getfunc = self._read_sync_cache

    def _read_sync_cache(self):
        enabled = self._enable_path.read_text() != '0\n'
        if enabled:
            res = int(self._length_path.read_text())
        else:
            res = 0

        if res != self._from_cache():
            # Sync cache
            Property._set_value(self, res)

        return res

    def _set_value(self, newvalue):
        with self._lock:
            Property._set_value(self, newvalue)

            if newvalue < 1:
                self._enable_path.write_text('0')
                return

            self._length_path.write_text(str(int(newvalue)))
            self._enable_path.write_text('1')


class IioDevBuffer(PropertyDictProperty):
    __slots__ = '_buffer_path',

    _eventids = ()  # No event manager

    def __init__(self, buffer_path: Path):
        self._buffer_path = buffer_path.resolve()
        pd = PropertyDict()
        PropertyDictProperty.__init__(self, pd, desc='Buffer control')

        data_available_path = buffer_path / 'data_available'
        if data_available_path.is_file():
            pd['data_available'] = PathPropertyInteger(data_available_path.resolve(),
                                                       desc='Amount of data in buffer', readonly=True)

        enable_path = self._buffer_path / 'enable'
        length_path = self._buffer_path / 'length'
        if enable_path.is_file() and length_path.is_file():
            pd['length'] = IioDevBufferLength(enable_path, length_path)


class IioDev(PropertyDictProperty):
    __slots__ = ()

    _eventids = ()  # No event manager

    def __init__(self, dev: iio.Device):
        dev_pd = PropertyDict()
        PropertyDictProperty.__init__(self, dev_pd, desc='Device access to ' + dev.name)

        dev_pd['name'] = ROProperty(DataType.STRING, dev.name.strip(), desc='Device name')
        dev_pd['id'] = ROProperty(DataType.STRING, dev.id.strip(), desc='Device id')

        if dev.attrs:
            dev_pd['attributes'] = IioDevAttributes(dev.attrs)

        if dev.buffer_attrs:
            dev_pd['buffer_attributes'] = IioDevBufferAttributes(dev.buffer_attrs)

        if dev.channels:
            dev_pd['channels'] = IioDevChannels(dev.channels)

        buffer_path = Path('/sys/bus/iio/devices', dev.id, 'buffer')
        if buffer_path.is_dir():
            dev_pd['buffer'] = IioDevBuffer(buffer_path)

        raw_path = Path('/dev', dev.id)
        if raw_path.exists():
            dev_pd['rawdevice'] = ROProperty(DataType.STRING, str(raw_path), desc='Raw data access path')


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
