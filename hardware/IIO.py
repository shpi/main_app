#!/usr/bin/env python3

import os
import hardware.iio as iio
from functools import partial
from core.DataTypes import Convert, DataType


class IIO:
    """Class for retrieving the requested information."""

    def __init__(self):
        self.inputs = dict()
        self.context = iio.Context('local:')
        self.path = 'iio'
        # print("IIO context has %u devices:" % len(self.context.devices))

        for dev in self.context.devices:
            self._device_info(dev)

    def get_inputs(self) -> dict:
        return self.inputs

    @staticmethod
    def read_iio(id, channel, retries=0):
        try:
            if os.path.isfile(f'/sys/bus/iio/devices/{id}/{channel}'):
                with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                    return int(rf.read().rstrip())
                    rf.close()
        except:
            if (retries < 3):
                return IIO.read_iio(id, channel, retries+1)
            else:
                return None

    def read_processed(id, channel, scale=1, offset=0, retries=0):
        if os.path.isfile(f'/sys/bus/iio/devices/{id}/{channel}'):
            try:
                with open(f'/sys/bus/iio/devices/{id}/{channel}', 'r') as rf:
                    value = scale * (int(rf.read().rstrip()) + offset)
                    return float(value)
                    rf.close()
            except:
                if (retries < 3):
                    return IIO.read_processed(id, channel, scale, offset, retries+1)
                else:
                    return None

    @staticmethod
    def write_iio(id, channel, value):
        # in_temp_object_calibemissivity
        if os.path.isfile(f'/sys/bus/iio/devices/{id}/{channel}'):
            with open(f'/sys/bus/iio/devices/{id}/{channel}', 'w') as rf:
                return (rf.write(str(value)))
                rf.close()

    def _device_info(self, dev):
        # print("\t" + dev.id + ": " + dev.name)
        # print("\t\t%u channels found: " % len(dev.channels))
        for channel in dev.channels:

            # print("\t\t\t%s: %s (%s)" % (channel.id, channel.name or "", "output" if channel.output else "input"))
            if len(channel.attrs) > 0:
                self.inputs[f'{self.path}/{dev.name}/{channel.id}'] = dict()
                self.inputs[f'{self.path}/{dev.name}/{channel.id}']['description'] = dev.name + ' ' + channel.id
                self.inputs[f'{self.path}/{dev.name}/{channel.id}']['lastupdate'] = 0
                self.inputs[f'{self.path}/{dev.name}/{channel.id}']['interval'] = -1
                self.inputs[f'{self.path}/{dev.name}/{channel.id}']['type'] = Convert.iio_to_shpi(
                    channel.type)

                #print("\t\t\t%u channel-specific attributes found: " % len(channel.attrs))
                for channel_attr in channel.attrs:
                    path = channel.attrs[channel_attr].filename

                    # print(path)
                    #print("\t\t\t\t" + channel_attr + ", value: " + channel.attrs[channel_attr].value)

                    if channel_attr == 'scale':
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}']['scale'] = channel.attrs[channel_attr].value

                    elif channel_attr == 'offset':
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}']['offset'] = channel.attrs[channel_attr].value

                    elif channel_attr == 'input':
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}']['value'] = channel.attrs[channel_attr].value
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}']['call'] = partial(
                            IIO.read_iio, dev.id, path)
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}']['interval'] = 60

                    elif channel_attr == 'raw':
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}']['raw'] = channel.attrs[channel_attr].value

                    elif channel_attr.endswith('_available'):

                        if f'{self.path}/{dev.name}/{channel.id}/{channel_attr[:-10]}' not in self.inputs:
                            self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr[:-10]}'] = {}
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr[:-10]}']['available'] = channel.attrs[channel_attr].value.split()

                    else:
                        if f'{self.path}/{dev.name}/{channel.id}/{channel_attr}' not in self.inputs:
                            self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}'] = {}
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}']['value'] = channel.attrs[channel_attr].value.rstrip()
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}']['call'] = partial(
                            IIO.read_iio, dev.id, path)
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}']['interval'] = 60
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}']['type'] = DataType.FLOAT
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}']['description'] = channel.id + ' ' + channel_attr
                        # print(f'/sys/bus/iio/devices/{dev.id}/{path}')

                        try:
                            IIO.write_iio(
                                dev.id, path, channel.attrs[channel_attr].value)
                            self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}']['set'] = partial(
                                IIO.write_iio, dev.id, path)
                            self.inputs[f'{self.path}/{dev.name}/{channel.id}/{channel_attr}']['interval'] = -1
                        except:
                            pass
                if 'raw' in self.inputs[f'{self.path}/{dev.name}/{channel.id}']:
                    scale = 1
                    offset = 0
                    if 'offset' in self.inputs[f'{self.path}/{dev.name}/{channel.id}']:
                        offset = float(
                            self.inputs[f'{self.path}/{dev.name}/{channel.id}']['offset'])

                    if 'scale' in self.inputs[f'{self.path}/{dev.name}/{channel.id}']:
                        scale = float(
                            self.inputs[f'{self.path}/{dev.name}/{channel.id}']['scale'])

                    # channel.attrs['raw'].filename
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}']['value'] = float(
                        (float(channel.attrs['raw'].value) + offset) * scale)
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}']['call'] = partial(
                        IIO.read_processed, str(dev.id), str(channel.attrs['raw'].filename), scale, offset)
                    # print(self.inputs[f'{self.path}/{dev.name}/{channel.id}']['call'])
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}']['interval'] = 60

        if len(dev.attrs) > 0:
            #print("\t\t%u device-specific attributes found: " % len(dev.attrs))
            for device_attr in dev.attrs:
                #print("\t\t\t" + device_attr + ", value: " + dev.attrs[device_attr].value)

                if device_attr == 'scale':
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}']['scale'] = dev.attrs[device_attr].value

                elif device_attr == 'offset':
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}']['offset'] = dev.attrs[device_attr].value

                elif device_attr.endswith('_available'):

                    if f'{self.path}/{dev.name}/{channel.id}/{device_attr[:-10]}' not in self.inputs:
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr[:-10]}'] = {}
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr[:-10]}']['available'] = dev.attrs[device_attr].value.split()
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr[:-10]}']['interval'] = 0

                else:
                    if f'{self.path}/{dev.name}/{channel.id}/{device_attr}' not in self.inputs:
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}'] = {}

                    self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}']['type'] = DataType.UNDEFINED
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}']['description'] = channel.id + ' ' + device_attr
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}']['value'] = dev.attrs[device_attr].value.rstrip()

                    path = dev.attrs[device_attr].filename

                    self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}']['call'] = partial(
                        IIO.read_iio, dev.id, path)
                    self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}']['interval'] = 300
                    # print(f'/sys/bus/iio/devices/{dev.id}/{path}')

                    try:
                        IIO.write_iio(
                            dev.id, path, dev.attrs[device_attr].value)
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}']['set'] = partial(
                            IIO.write_iio, dev.id, path)
                        self.inputs[f'{self.path}/{dev.name}/{channel.id}/{device_attr}']['interval'] = -1
                    except:
                        pass


def main():
    """Module's main method."""

    information = IIO()
    print(information.inputs)


if __name__ == "__main__":
    main()
