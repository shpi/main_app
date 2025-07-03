#!/usr/bin/env python3

import os
import stat
import logging
import sys
from functools import partial

import core.iio as iio
from core.DataTypes import Convert, DataType
from core.Property import EntityProperty

# Map common attribute names to their DataType and a short description.
ATTRIBUTE_INFO = {
    'raw': (DataType.INT, 'Unscaled raw value'),
    'input': (DataType.INT, 'Processed input value'),
    'scale': (DataType.FLOAT, 'Scale factor applied to raw value'),
    'offset': (DataType.FLOAT, 'Offset applied to raw value'),
    'calibbias': (DataType.FLOAT, 'Calibration bias value'),
    'calibscale': (DataType.FLOAT, 'Calibration scale value'),
    'sampling_frequency': (DataType.FLOAT, 'Sampling frequency in Hz'),
    'integration_time': (DataType.FLOAT, 'Integration time'),
    'oversampling_ratio': (DataType.INT, 'Oversampling ratio'),
    'hysteresis': (DataType.FLOAT, 'Hysteresis value'),
    'filter_low_pass_0_frequency': (DataType.FLOAT, 'Low pass filter frequency'),
    'filter_high_pass_0_frequency': (DataType.FLOAT, 'High pass filter frequency'),
    'enable': (DataType.BOOL, 'Enable or disable the channel'),
}

# Descriptive text for known IIO channel types.
CHANNEL_DESCRIPTIONS = {
    iio.ChannelType.IIO_VOLTAGE: 'Voltage measurement',
    iio.ChannelType.IIO_CURRENT: 'Current measurement',
    iio.ChannelType.IIO_POWER: 'Power measurement',
    iio.ChannelType.IIO_ACCEL: 'Acceleration measurement',
    iio.ChannelType.IIO_MAGN: 'Magnetic field measurement',
    iio.ChannelType.IIO_LIGHT: 'Light intensity measurement',
    iio.ChannelType.IIO_INTENSITY: 'Light intensity measurement',
    iio.ChannelType.IIO_PROXIMITY: 'Proximity measurement',
    iio.ChannelType.IIO_TEMP: 'Temperature measurement',
    iio.ChannelType.IIO_ROT: 'Angular velocity measurement',
    iio.ChannelType.IIO_ANGL: 'Angular measurement',
    iio.ChannelType.IIO_TIMESTAMP: 'Timestamp',
    iio.ChannelType.IIO_CAPACITANCE: 'Capacitance measurement',
    iio.ChannelType.IIO_PRESSURE: 'Pressure measurement',
    iio.ChannelType.IIO_HUMIDITYRELATIVE: 'Relative humidity measurement',
    iio.ChannelType.IIO_STEPS: 'Step count',
    iio.ChannelType.IIO_ENERGY: 'Energy measurement',
    iio.ChannelType.IIO_DISTANCE: 'Distance measurement',
    iio.ChannelType.IIO_VELOCITY: 'Velocity measurement',
    iio.ChannelType.IIO_CONCENTRATION: 'Concentration measurement',
    iio.ChannelType.IIO_RESISTANCE: 'Electrical resistance measurement',
    iio.ChannelType.IIO_PH: 'pH level',
    iio.ChannelType.IIO_UVINDEX: 'UV index',
    iio.ChannelType.IIO_ELECTRICALCONDUCTIVITY: 'Electrical conductivity',
    iio.ChannelType.IIO_COUNT: 'Count value',
    iio.ChannelType.IIO_GRAVITY: 'Gravity measurement',
}

class IIO:
    """Class for retrieving the requested information."""

    def __init__(self):
        self.properties = dict()
        self.name = 'iio'

        try:
            self.context = iio.Context('local:')
            logging.debug(f'Initialized IIO context with {len(self.context.devices)} devices')
            for dev in self.context.devices:
                logging.debug(f'Processing device: {dev.id}, Name: {dev.name}')
                try:
                    self._device_info(dev)
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    line_number = exception_traceback.tb_lineno
                    logging.error(f'Error processing device {dev.id}: {e} in line {line_number}')

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'No IIO sensors found, error: {e} in line {line_number}')

    def get_inputs(self) -> list:
        return self.properties.values()

    @staticmethod
    def read_iio(id, channel, retries=0):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                value = rf.read().rstrip()
                logging.debug(f'Reading {channel} from {id}: Value = {value}')
                return Convert.str_to_tight_datatype(value)

        except Exception as e:
            logging.error(f'Error reading {channel} from {id}: {e}')
            if (retries < 3):
                logging.debug(f'Retry {retries + 1} for reading {channel} from {id}')
                return IIO.read_iio(id, channel, retries + 1)
            else:
                return None

    def read_processed(id, channel, scale=1, offset=0, retries=0):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                value = scale * (float(rf.read().rstrip()) + offset)
                logging.debug(f'Reading processed value from {channel} on {id}: Value = {value}')
                return value

        except Exception as e:
            logging.error(f'Error reading processed value from {channel} on {id}: {e}')
            if (retries < 3):
                logging.debug(f'Retry {retries + 1} for reading processed value from {channel} on {id}')
                return IIO.read_processed(id, channel, scale, offset, retries + 1)
            else:
                return None

    @staticmethod
    def write_iio(id, channel, value):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'w') as wf:
                wf.write(str(value))
                logging.debug(f'Writing {value} to {channel} on {id}')
        except Exception as e:
            logging.error(f'Error writing to {channel} on {id}: {e}')
            return None

    @staticmethod
    def is_writable(path):
        """Check if a sysfs attribute is writable without altering its value.

        The method rewrites the current value and verifies it remains
        unchanged. If the value unexpectedly differs after the write, it tries
        to restore the original contents and reports the attribute as not
        writable.
        """
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'r+') as f:
                original = f.read()
                f.seek(0)
                f.write(original)
                f.flush()
                f.seek(0)
                after = f.read()

                if after != original:
                    logging.warning(
                        f'Write test altered {path}; attempting to restore')
                    f.seek(0)
                    f.write(original)
                    f.flush()
                    f.seek(0)
                    restored = f.read()
                    if restored != original:
                        logging.error(
                            f'Failed to restore original value for {path}')
                    return False

            return True
        except Exception as e:
            logging.debug(f'Write access test failed for {path}: {e}')
            return False


    def _device_info(self, dev):
        for channel in dev.channels:
            logging.debug(f'Processing channel: {channel.id}, Name: {channel.name or ""}, Output: {channel.output}')
            if len(channel.attrs) > 0:
                scale = 1
                offset = 0
                raw = None

                channel_desc = CHANNEL_DESCRIPTIONS.get(channel.type, channel.id)
                self.properties[f'{dev.name}/{channel.id}'] = EntityProperty(
                    category='sensor/' + dev.name,
                    name=channel.id,
                    description=f"{dev.name} {channel_desc}",
                    type=Convert.iio_to_shpi(channel.type),
                    interval=20)

                for channel_attr in channel.attrs:
                    path = channel.attrs[channel_attr].filename
                    logging.debug(f'Accessing attribute {channel_attr} at path {path} for channel {channel.id} on device {dev.id}')

                    if channel_attr == 'scale':
                        scale = channel.attrs[channel_attr].value

                    elif channel_attr == 'offset':
                        offset = channel.attrs[channel_attr].value

                    elif channel_attr == 'timestamp':
                        pass  # not useful for us

                    elif channel_attr == 'input':
                        self.properties[f'{dev.name}/{channel.id}'].value = channel.attrs[channel_attr].value
                        self.properties[f'{dev.name}/{channel.id}'].call = partial(IIO.read_iio, dev.id, channel.attrs[channel_attr].filename)

                    elif channel_attr == 'raw':
                        raw = channel.attrs[channel_attr].value

                    elif channel_attr.endswith('_available'):
                        base = channel_attr[:-10]
                        dtype, adesc = ATTRIBUTE_INFO.get(base, (DataType.FLOAT, base))
                        if f'{dev.name}/{channel.id}/{base}' not in self.properties:
                            self.properties[f'{dev.name}/{channel.id}/{base}'] = EntityProperty(
                                category='sensor/' + dev.name,
                                name=base,
                                description=f"{dev.name} {channel.id} {adesc}",
                                type=dtype,
                                available=channel.attrs[channel_attr].value.split(),
                                interval=-1)
                        else:
                            self.properties[f'{dev.name}/{channel.id}/{base}'].available = channel.attrs[channel_attr].value.split()

                    else:
                        if f'{dev.name}/{channel.id}/{channel_attr}' not in self.properties:
                            dtype, adesc = ATTRIBUTE_INFO.get(channel_attr, (DataType.FLOAT, channel_attr))
                            self.properties[f'{dev.name}/{channel.id}/{channel_attr}'] = EntityProperty(
                                category='sensor/' + dev.name,
                                name=channel_attr,
                                description=f"{dev.name} {channel.id} {adesc}",
                                type=dtype,
                                interval=-1)

                        dtype, adesc = ATTRIBUTE_INFO.get(channel_attr, (DataType.FLOAT, channel_attr))
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].description = f"{dev.name} {channel.id} {adesc}"
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].name = channel_attr
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].value = channel.attrs[channel_attr].value.rstrip()
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].type = dtype
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].call = partial(IIO.read_iio, dev.id, path)

                        #attr_file_path = f'/sys/bus/iio/devices/{dev.id}/{channel.attrs[channel_attr].filename}'

                        file_path = f'/sys/bus/iio/devices/{dev.id}/{channel.attrs[channel_attr].filename}'
                        if IIO.is_writable(file_path):
                                logging.debug(f'{dev.name}/{channel.id}/{channel_attr} is writeable, registering setter')
                                self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].set = partial(IIO.write_iio, dev.id, channel.attrs[channel_attr].filename)


                if raw is not None:
                    self.properties[f'{dev.name}/{channel.id}'].value = (float(raw) + float(offset)) * float(scale)
                    self.properties[f'{dev.name}/{channel.id}'].call = partial(IIO.read_processed, dev.id, channel.attrs['raw'].filename, float(scale), float(offset))

        if len(dev.attrs) > 0:
            for device_attr in dev.attrs:
                if device_attr == 'scale':
                    general_scale = dev.attrs[device_attr].value

                elif device_attr == 'offset':
                    general_offset = dev.attrs[device_attr].value

                elif device_attr == 'timestamp':
                    pass  # not useful for us

                elif device_attr.endswith('_available'):
                    base = device_attr[:-10]
                    dtype, adesc = ATTRIBUTE_INFO.get(base, (DataType.FLOAT, base))
                    if f'{dev.name}/{channel.id}/{base}' not in self.properties:
                        self.properties[f'{dev.name}/{channel.id}/{base}'] = EntityProperty(
                            category='sensor/' + dev.name,
                            name=base,
                            description=f"{dev.name} {channel.id} {adesc}",
                            type=dtype,
                            interval=-1)

                    self.properties[f'{dev.name}/{channel.id}/{base}'].available = dev.attrs[device_attr].value.split()

                else:
                    if f'{dev.name}/{channel.id}/{device_attr}' not in self.properties:
                        dtype, adesc = ATTRIBUTE_INFO.get(device_attr, (DataType.FLOAT, device_attr))
                        self.properties[f'{dev.name}/{channel.id}/{device_attr}'] = EntityProperty(
                            category='sensor/' + dev.name,
                            name=device_attr,
                            description=f"{dev.name} {channel.id} {adesc}",
                            type=dtype,
                            interval=-1)

                    dtype, adesc = ATTRIBUTE_INFO.get(device_attr, (DataType.FLOAT, device_attr))
                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].value = dev.attrs[device_attr].value.rstrip()
                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].description = f"{dev.name} {channel.id} {adesc}"
                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].type = dtype
                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].call = partial(IIO.read_iio, dev.id, dev.attrs[device_attr].filename)



                    file_path = f'/sys/bus/iio/devices/{dev.id}/{dev.attrs[device_attr].filename}'
                    if IIO.is_writable(file_path):
                            logging.debug(f'{dev.name}/{channel.id}/{device_attr} is writeable, registering setter')
                            self.properties[f'{dev.name}/{channel.id}/{device_attr}'].set = partial(IIO.write_iio, dev.id, dev.attrs[device_attr].filename)
