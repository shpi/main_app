# -*- coding: utf-8 -*-

import logging
import sys
from functools import partial
from pathlib import Path
from typing import Generator

import hardware.iio as iio
from interfaces.DataTypes import DataType
from core.Property import EntityProperty


class IIO:
    """Class for retrieving the requested information."""

    _iio_devices_path = Path('/sys/bus/iio/devices')

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

    def __init__(self):
        self.properties = {}
        self.name = 'iio'

        try:
            self.context = iio.Context('local:')
            for dev in self.context.devices:
                try:
                    self._device_info(dev)
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    line_number = exception_traceback.tb_lineno
                    logging.error(f'error: {e} in line {line_number}')

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'No IIO sensors found, error: {e} in line {line_number}')

        # print("IIO context has %u devices:" % len(self.context.devices))

    def get_inputs(self) -> list:
        return self.properties.values()

    @staticmethod
    def read_iio(id, channel, retries=0):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                value = rf.read().rstrip()
                logging.debug('reading ' + channel + ': ' + str(value))
                return DataType.str_to_tight_datatype(value)

        except Exception as e:
            if retries < 3:
                return IIO.read_iio(id, channel, retries + 1)
            else:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                line_number = exception_traceback.tb_lineno
                logging.error(f'channel: {channel} error: {e} in line {line_number}')
                return None

    def read_processed(id, channel, scale=1, offset=0, retries=0):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                value = scale * (float(rf.read().rstrip()) + offset)
                logging.debug('reading ' + channel + ': ' + str(value))
                return value

        except Exception as e:
            if retries < 3:
                return IIO.read_processed(id, channel, scale, offset, retries + 1)
            else:
                exception_traceback = sys.exc_info()[2]
                line_number = exception_traceback.tb_lineno
                logging.error(f'channel: {channel} error: {e} in line {line_number}')
                return None

    @staticmethod
    def write_iio(id, channel, value):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'w') as rf:
                return rf.write(str(value))

        except Exception as e:
            exception_traceback = sys.exc_info()[2]
            line_number = exception_traceback.tb_lineno
            logging.error(f'channel: {channel} error: {e} in line {line_number}')
            return None

    def _device_info(self, dev):
        # print("\t" + dev.id + ": " + dev.name)
        # print("\t\t%u channels found: " % len(dev.channels))
        for channel in dev.channels:
            # print("\t\t\t%s: %s (%s)" % (channel.id, channel.name or "", "output" if channel.output else "input"))

            if len(channel.attrs) > 0:
                scale = 1
                offset = 0
                raw = None

                self.properties[f'{dev.name}/{channel.id}'] = EntityProperty(parent=self,
                                                                             category='sensor',
                                                                             entity=dev.name,
                                                                             name=channel.id,
                                                                             description=dev.name + ' ' + channel.id,
                                                                             type=DataType.iio_to_shpi(
                                                                                 channel.type),
                                                                             interval=20)

                # print("\t\t\t%u channel-specific attributes found: " % len(channel.attrs))
                for channel_attr in channel.attrs:
                    path = channel.attrs[channel_attr].filename

                    # print("\t\t\t\t" + channel_attr + ", value: " + channel.attrs[channel_attr].value)

                    if channel_attr == 'scale':
                        scale = channel.attrs[channel_attr].value

                    elif channel_attr == 'offset':
                        offset = channel.attrs[channel_attr].value

                    elif channel_attr == 'timestamp':
                        pass  # not useful for us

                    elif channel_attr == 'input':
                        self.properties[f'{dev.name}/{channel.id}'].value = channel.attrs[
                            channel_attr].value
                        self.properties[f'{dev.name}/{channel.id}'].call = partial(IIO.read_iio, dev.id, path)

                    elif channel_attr == 'raw':
                        raw = channel.attrs[channel_attr].value

                    elif channel_attr.endswith('_available'):

                        if f'{dev.name}/{channel.id}/{channel_attr[:-10]}' not in self.properties:
                            self.properties[
                                f'{dev.name}/{channel.id}/{channel_attr[:-10]}'] = EntityProperty(
                                parent=self,
                                category='sensor',
                                entity=dev.name,
                                name=channel_attr[:-10],
                                description=dev.name + ' ' + channel.id,
                                type=DataType.FLOAT,
                                available=channel.attrs[channel_attr].value.split(),
                                interval=-1)

                        else:
                            self.properties[f'{dev.name}/{channel.id}/{channel_attr[:-10]}'].available = \
                                channel.attrs[channel_attr].value.split()

                    else:
                        if f'{dev.name}/{channel.id}/{channel_attr}' not in self.properties:
                            self.properties[f'{dev.name}/{channel.id}/{channel_attr}'] = EntityProperty(
                                parent=self,
                                category='sensor',
                                entity=dev.name,
                                name=channel_attr,
                                type=DataType.FLOAT,
                                interval=-1)

                        self.properties[
                            f'{dev.name}/{channel.id}/{channel_attr}'].description = dev.name + ' ' + channel.id + ' ' + channel_attr
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].name = channel_attr
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].value = \
                            channel.attrs[channel_attr].value.rstrip()
                        self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].call = partial(
                            IIO.read_iio, dev.id, path)

                        try:
                            IIO.write_iio(dev.id, path, channel.attrs[channel_attr].value)
                            self.properties[f'{dev.name}/{channel.id}/{channel_attr}'].set = partial(
                                IIO.write_iio, dev.id, path)

                        except Exception as e:
                            logging.error('error iio: ' + str(e))
                            pass

                if raw is not None:
                    self.properties[f'{dev.name}/{channel.id}'].value = (float(raw) + float(offset)) * float(scale)
                    self.properties[f'{dev.name}/{channel.id}'].call = partial(IIO.read_processed,
                                                                               dev.id, channel.attrs[
                                                                                   'raw'].filename,
                                                                               float(scale), float(offset))

        if len(dev.attrs) > 0:
            for device_attr in dev.attrs:
                if device_attr == 'scale':
                    general_scale = dev.attrs[device_attr].value

                elif device_attr == 'offset':
                    general_offset = dev.attrs[device_attr].value

                elif device_attr == 'timestamp':
                    pass  # not useful for us

                elif device_attr.endswith('_available'):
                    # "[min step max]"
                    if f'{dev.name}/{channel.id}/{device_attr[:-10]}' not in self.properties:
                        self.properties[
                            f'{dev.name}/{channel.id}/{device_attr[:-10]}'] = EntityProperty(
                            parent=self,
                            category='sensor',
                            entity=dev.name,
                            name=device_attr[:-10],
                            description=dev.name + ' ' + channel.id + ' ' + device_attr[:-10],
                            type=DataType.UNDEFINED,
                            interval=-1)

                    self.properties[f'{dev.name}/{channel.id}/{device_attr[:-10]}'].available = \
                        dev.attrs[device_attr].value.split()

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

                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].value = dev.attrs[
                        device_attr].value.rstrip()
                    self.properties[f'{dev.name}/{channel.id}/{device_attr}'].call = partial(
                        IIO.read_iio, dev.id, dev.attrs[device_attr].filename)

                    try:
                        IIO.write_iio(dev.id, path, dev.attrs[device_attr].value)
                        self.properties[f'{dev.name}/{channel.id}/{device_attr}'].set = partial(
                            IIO.write_iio, dev.id, path)

                    except Exception as e:
                        logging.error(str(e))
