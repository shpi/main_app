#!/usr/bin/env python3

import os
import stat
import logging
import sys
from functools import partial

import core.iio as iio
from core.DataTypes import Convert, DataType
from core.Property import EntityProperty


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

    def _device_info(self, dev):
        for channel in dev.channels:
            logging.debug(f'Processing channel: {channel.id}, Name: {channel.name or ""}, Output: {channel.output}')
            if len(channel.attrs) > 0:
                scale = 1
                offset = 0
                raw = None

                self.properties[f'{dev.name}/{channel.id}'] = EntityProperty(parent=self,
                                                                             category='sensor',
                                                                             entity=dev.name,
                                                                             name=channel.id,
                                                                             description=dev.name + ' ' + channel.id,
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
                        if f'{dev.name}/{channel.id}/{channel_attr[:-10]}' not in self.properties:
                            self.properties[f'{dev.name}/{channel.id}/{channel_attr[:-10]}'] = EntityProperty(
                                parent=self,
                                category='sensor',
                                entity=dev.name,
                                name=channel_attr[:-10],
                                description=dev.name + ' ' + channel.id,
                                type=DataType.FLOAT,
                                available=channel.attrs[channel_attr].value.split(),
                                interval=-1)
                        else:
                            self.properties[f'{dev.name}/{channel.id}/{channel_attr[:-10]}'].available = channel.attrs[channel_attr].value.split()

                    else:
                        if f'{dev.name}/{channel.id}/{channel_attr}' not in self.properties:
                            self.properties[f'{dev.name}/{channel.id}/{channel_attr}'] = EntityProperty(
                                parent=self,
                                category='sensor',
                                entity=dev.name,
                                name=channel_attr,
                                type=DataType.FLOAT,
                                interval=-1)

                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].description = dev.name + ' ' + channel.id + ' ' + channel_attr
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].name = channel_attr
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].value = channel.attrs[channel_attr].value.rstrip()
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].call = partial(IIO.read_iio, dev.id, path)

                        #attr_file_path = f'/sys/bus/iio/devices/{dev.id}/{channel.attrs[channel_attr].filename}'

                        if os.path.exists(f'/sys/bus/iio/devices/{dev.id}/{channel.attrs[channel_attr].filename}') and os.access(f'/sys/bus/iio/devices/{dev.id}/{channel.attrs[channel_attr].filename}', os.W_OK):
                                logging.debug(f'{dev.name}/{channel.id}/{channel_attr} is writeable? Lets check')
                                logging.debug(f'/sys/bus/iio/devices/{dev.id}/{channel.attrs[channel_attr].filename}')
                                try:
                                      IIO.write_iio(dev.id, channel.attrs[channel_attr].filename, channel.attrs[channel_attr].value.rstrip())

                                except Exception as e:
                                      logging.error(f'Error writing {dev.name}/{channel.id}/{channel_attr}: {e}')

                                finally:
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
                    if f'{dev.name}/{channel.id}/{device_attr[:-10]}' not in self.properties:
                        self.properties[f'{dev.name}/{channel.id}/{device_attr[:-10]}'] = EntityProperty(
                            parent=self,
                            category='sensor',
                            entity=dev.name,
                            name=device_attr[:-10],
                            description=dev.name + ' ' + channel.id + ' ' + device_attr[:-10],
                            type=DataType.UNDEFINED,
                            interval=-1)

                    self.properties[f'{dev.name}/{channel.id}/{device_attr[:-10]}'].available = dev.attrs[device_attr].value.split()

                else:
                    if f'{dev.name}/{channel.id}/{device_attr}' not in self.properties:
                        self.properties[f'{dev.name}/{channel.id}/{device_attr}'] = EntityProperty(
                            parent=self,
                            category='sensor',
                            entity=dev.name,
                            name=device_attr,
                            description=dev.name + ' ' + channel.id + ' ' + device_attr,
                            type=DataType.UNDEFINED,
                            interval=-1)

                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].value = dev.attrs[device_attr].value.rstrip()
                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].call = partial(IIO.read_iio, dev.id, dev.attrs[device_attr].filename)


                    if os.path.exists(f'/sys/bus/iio/devices/{dev.id}/{dev.attrs[device_attr].filename}') and os.access(f'/sys/bus/iio/devices/{dev.id}/{dev.attrs[device_attr].filename}', os.W_OK):
                            file_stat = os.stat(f'/sys/bus/iio/devices/{dev.id}/{dev.attrs[device_attr].filename}')
                            if (file_stat.st_mode & stat.S_IWUSR):

                                logging.debug(f'{dev.name}/{channel.id}/{device_attr} is writeable? Lets check')
                                logging.debug(f'/sys/bus/iio/devices/{dev.id}/{dev.attrs[device_attr].filename}')
                                try:
                                    IIO.write_iio(dev.id, dev.attrs[device_attr].filename, dev.attrs[device_attr].value)
                                except Exception as e:
                                    logging.error(f'Error writing {dev.name}/{channel.id}/{device_attr}: {e}')

                                finally:
                                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].set = partial(IIO.write_iio, dev.id, dev.attrs[device_attr].filename)

# Add any additional functionality or script entry point below if needed


