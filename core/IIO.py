import os
import stat
import logging
import sys
from functools import partial

import core.iio as iio
from core.DataTypes import Convert, DataType
from core.Property import EntityProperty


class IIO:
    name = 'iio'
    _properties = dict()

    @staticmethod
    def get_inputs() -> list:
        if IIO._properties:
            return IIO._properties.values()

        try:
            context = iio.Context('local:')
            logging.debug(f'Initialized IIO context with {len(context.devices)} devices')
            for dev in context.devices:
                logging.debug(f'Processing device: {dev.id}, Name: {dev.name}')
                if dev.id.startswith('hwmon'):
                    logging.debug(f"Skipping device {dev.name} (hwmon device)")
                    continue
                try:
                    IIO._device_info(dev)
                except Exception as e:
                    _, _, tb = sys.exc_info()
                    logging.error(f'Error processing device {dev.id}: {e} in line {tb.tb_lineno}')
        except Exception as e:
            _, _, tb = sys.exc_info()
            logging.error(f'No IIO sensors found, error: {e} in line {tb.tb_lineno}')

        return IIO._properties.values()

    @staticmethod
    def read_iio(id, channel, retries=0):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                value = rf.read().rstrip()
                logging.debug(f'Reading {channel} from {id}: Value = {value}')
                return Convert.str_to_tight_datatype(value)
        except Exception as e:
            logging.error(f'Error reading {channel} from {id}: {e}')
            if retries < 3:
                return IIO.read_iio(id, channel, retries + 1)
            return None

    @staticmethod
    def read_processed(id, channel, scale=1, offset=0, retries=0):
        try:
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                value = scale * (float(rf.read().rstrip()) + offset)
                logging.debug(f'Reading processed value from {channel} on {id}: Value = {value}')
                return value
        except Exception as e:
            logging.error(f'Error reading processed value from {channel} on {id}: {e}')
            if retries < 3:
                return IIO.read_processed(id, channel, scale, offset, retries + 1)
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
                    logging.warning(f'Write test altered {path}; attempting to restore')
                    f.seek(0)
                    f.write(original)
                    f.flush()
                    f.seek(0)
                    if f.read() != original:
                        logging.error(f'Failed to restore original value for {path}')
                    return False
            return True
        except Exception as e:
            logging.debug(f'Write access test failed for {path}: {e}')
            return False

    @staticmethod
    def _device_info(dev):
        for channel in dev.channels:
            logging.debug(f'Processing channel: {channel.id}, Name: {channel.name or ""}, Output: {channel.output}')
            if not channel.attrs:
                continue

            scale = 1
            offset = 0
            raw = None

            IIO._properties[f'{dev.name}/{channel.id}'] = EntityProperty(
                category='sensor/' + dev.name,
                name=channel.id,
                description=dev.name + ' ' + channel.id,
                type=Convert.iio_to_shpi(channel.type),
                interval=20
            )

            for channel_attr in channel.attrs:
                path = channel.attrs[channel_attr].filename

                if channel_attr == 'scale':
                    scale = channel.attrs[channel_attr].value
                elif channel_attr == 'offset':
                    offset = channel.attrs[channel_attr].value
                elif channel_attr == 'timestamp':
                    continue
                elif channel_attr == 'input':
                    IIO._properties[f'{dev.name}/{channel.id}'].value = channel.attrs[channel_attr].value
                    IIO._properties[f'{dev.name}/{channel.id}'].call = partial(IIO.read_iio, dev.id, path)
                elif channel_attr == 'raw':
                    raw = channel.attrs[channel_attr].value
                elif channel_attr.endswith('_available'):
                    key = f'{dev.name}/{channel.id}/{channel_attr[:-10]}'
                    if key not in IIO._properties:
                        IIO._properties[key] = EntityProperty(
                            category='sensor/' + dev.name,
                            name=channel_attr[:-10],
                            description=dev.name + ' ' + channel.id,
                            type=DataType.FLOAT,
                            available=channel.attrs[channel_attr].value.split(),
                            interval=-1)
                    else:
                        IIO._properties[key].available = channel.attrs[channel_attr].value.split()
                else:
                    key = f'{dev.name}/{channel.id}/{channel_attr}'
                    if key not in IIO._properties:
                        IIO._properties[key] = EntityProperty(
                            category='sensor/' + dev.name,
                            name=channel_attr,
                            type=DataType.FLOAT,
                            interval=-1)
                    IIO._properties[key].description = f'{dev.name} {channel.id} {channel_attr}'
                    IIO._properties[key].value = channel.attrs[channel_attr].value.rstrip()
                    IIO._properties[key].call = partial(IIO.read_iio, dev.id, path)

                    file_path = f'/sys/bus/iio/devices/{dev.id}/{path}'
                    if IIO.is_writable(file_path):
                        IIO._properties[key].set = partial(IIO.write_iio, dev.id, path)

            if raw is not None:
                IIO._properties[f'{dev.name}/{channel.id}'].value = (float(raw) + float(offset)) * float(scale)
                IIO._properties[f'{dev.name}/{channel.id}'].call = partial(IIO.read_processed, dev.id, channel.attrs['raw'].filename, float(scale), float(offset))

        if dev.attrs:
            for device_attr in dev.attrs:
                if device_attr in ('scale', 'offset', 'timestamp'):
                    continue

                key = f'{dev.name}/{channel.id}/{device_attr}'
                if device_attr.endswith('_available'):
                    short = device_attr[:-10]
                    key = f'{dev.name}/{channel.id}/{short}'
                    if key not in IIO._properties:
                        IIO._properties[key] = EntityProperty(
                            category='sensor/' + dev.name,
                            name=short,
                            description=dev.name + ' ' + channel.id + ' ' + short,
                            type=DataType.UNDEFINED,
                            interval=-1)
                    IIO._properties[key].available = dev.attrs[device_attr].value.split()
                else:
                    if key not in IIO._properties:
                        IIO._properties[key] = EntityProperty(
                            category='sensor/' + dev.name,
                            name=device_attr,
                            description=dev.name + ' ' + channel.id + ' ' + device_attr,
                            type=DataType.UNDEFINED,
                            interval=-1)
                    IIO._properties[key].value = dev.attrs[device_attr].value.rstrip()
                    IIO._properties[key].call = partial(IIO.read_iio, dev.id, dev.attrs[device_attr].filename)

                    file_path = f'/sys/bus/iio/devices/{dev.id}/{dev.attrs[device_attr].filename}'
                    if IIO.is_writable(file_path):
                        IIO._properties[key].set = partial(IIO.write_iio, dev.id, dev.attrs[device_attr].filename)
