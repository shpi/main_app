import logging
import struct
import subprocess
import sys
from enum import Enum
from functools import partial

from core.DataTypes import DataType
from core.Property import EntityProperty, ThreadProperty


class EvTypes(Enum):
    EV_SYN = 0x00
    EV_KEY = 0x01
    EV_REL = 0x02
    EV_ABS = 0x03
    EV_MSC = 0x04
    EV_SW = 0x05
    EV_LED = 0x11
    EV_SND = 0x12
    EV_REP = 0x14
    EV_FF = 0x15
    EV_PWR = 0x16
    EV_FF_STATUS = 0x17


def test_bit(eventlist, b):
    index = b // 32
    bit = b % 32
    if len(eventlist) <= index:
        return False
    if eventlist[index] & (1 << bit):
        return True
    else:
        return False


def EvHexToStr(events):
    s = []

    for key in EvTypes:
        #print(key.value)
        if test_bit(events, key.value):
            s.append(key.name)

    return s


def createId(x):
    return x in ('1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')


class InputDevs:
    FILENAME = '/proc/bus/input/devices'

    def __init__(self):

        super(InputDevs, self).__init__()

        self.devs = dict()
        self.properties = dict()

        self.properties['lastinput'] = EntityProperty(parent=self,
                                                      category='core',
                                                      entity='input_dev',
                                                      name='lastinput',
                                                      description='Last active input',
                                                      type=DataType.STRING,
                                                      interval=-1)


        with open(self.FILENAME, 'r') as f:

            while True:
                line = f.readline()

                if not line:
                    break

                if line.startswith('I: Bus='):
                    device = dict()

                    id = (''.join(filter(createId, line)))

                if line.startswith('N: Name='):
                    device['name'] = line[len('N: Name='):].strip('"\n')

                if line.startswith('B: EV'):
                    eventsHex = [int(x, base=16) for x in line[6:].split()]
                    eventsHex.reverse()
                    device['EV'] = EvHexToStr(eventsHex)

                if line.startswith('H: Handlers='):
                    events = list(
                        line[len('H: Handlers='):].rstrip().split(' '))
                    device['event'] = list(
                        filter(lambda x: x.startswith('event'), events))

                    p = subprocess.Popen(["keymap/keymap", ''.join(filter(str.isdigit, str(device['event'])))],
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

                    keys = p.communicate()[0]

                    keys = set(keys.decode().strip().split('\n'))

                    device['keys'] = dict()

                    for key in keys:

                        try:
                            key = key.split(':')
                            # device['keys'][int(key[0])] = keydict
                            self.properties[f'{id}/key_{str(key[0])}'] = EntityProperty(
                                parent=self,
                                category='input_dev',
                                entity=id,
                                name=str(key[0]),
                                description=key[1],
                                type=DataType.INT,
                                interval=-1)

                        except IndexError:
                            pass

                self.devs[id] = device

        f.close()

        for id, subdevice in self.devs.items():
            self.properties[f'{id}/thread'] = ThreadProperty(
                name=id,
                category='module',
                entity='input_dev',
                parent=self,
                value=1,
                description='Thread for ' + subdevice['name'],
                interval=60,
                function=partial(self.devloop, f"/dev/input/{subdevice['event'][0]}", id, 'EV_ABS' in subdevice['EV'])
            )

    def get_inputs(self) -> list:

        return self.properties.values()

    def devloop(self, devpath, id, ismouse=False):

        systembits = (struct.calcsize("P") * 8)
        try:
            logging.debug(f'start reading: {devpath}')
            with open(devpath, 'rb') as devfile:
                while self.properties[f'{id}/thread'].value:
                    # 16 byte for 32bit,  24 for 64bit
                    event = devfile.read(16 if systembits == 32 else 24)
                    (timestamp, _id, evtype, keycode, value) = struct.unpack('llHHI', event)

                    if evtype == 1:  # type 1 = key, we watch only keys!

                        try:
                            if ismouse: self.properties['lastinput'].value = 2 if value else 0

                            else:
                                if value: self.properties[f'{id}/thread'].value = 1  # helps to track activity on input device
                                self.properties[f'{id}/key_{str(keycode)}'].value = value

                        except KeyError:
                            self.properties[f'{id}/key_{str(keycode)}'] = EntityProperty(parent=self,
                                                                                         category='input_dev',
                                                                                         entity=id,
                                                                                         name=str(keycode),
                                                                                         description=str(keycode),
                                                                                         type=DataType.INT,
                                                                                         interval=-1)
                            self.properties[f'{id}/key_{str(keycode)}'].value = value

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'input_dev/{id}/thread failed: {e} in line {line_number}')
