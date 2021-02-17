import logging
import subprocess
import threading
import struct
import ctypes
import time
import sys
from core.DataTypes import DataType
from functools import partial
from core.Property import EntityProperty, ThreadProperty

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
    if test_bit(events, EV_SYN):       s.append("EV_SYN")
    if test_bit(events, EV_KEY):       s.append("EV_KEY")
    if test_bit(events, EV_REL):       s.append("EV_REL")
    if test_bit(events, EV_ABS):       s.append("EV_ABS")
    if test_bit(events, EV_MSC):       s.append("EV_MSC")
    if test_bit(events, EV_LED):       s.append("EV_LED")
    if test_bit(events, EV_SND):       s.append("EV_SND")
    if test_bit(events, EV_REP):       s.append("EV_REP")
    if test_bit(events, EV_FF):        s.append("EV_FF")
    if test_bit(events, EV_PWR):       s.append("EV_PWR")
    if test_bit(events, EV_FF_STATUS): s.append("EV_FF_STATUS")

    return s


def createId(x):
    if x in ('1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'):
        return True
    return False


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
                                                      description='Last active input device',
                                                      type=DataType.STRING,
                                                      interval=-1)

        self.properties['lasttouch'] = EntityProperty(parent=self,
                                                      category='core',
                                                      entity='input_dev',
                                                      name='lasttouch',
                                                      description='Last touch input device',
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

    def devloop(self, devpath, id, ismouse=0):

        systembits = (struct.calcsize("P") * 8)
        try:
            logging.debug(f'start reading: {devpath}')
            with open(devpath, 'rb') as devfile:
                while self.properties[f'{id}/thread'].value:
                    # 16 byte for 32bit,  24 for 64bit
                    event = devfile.read(16 if systembits == 32 else 24)
                    (timestamp, _id, type, keycode, value) = struct.unpack('llHHI', event)

                    if (type == 1):  # type 1 = key, we watch only keys!

                        try:

                            if ismouse:
                                self.properties['lasttouch'].value = value

                            self.properties['lastinput'].value = value
                            self.properties[f'{id}/thread'].value = 1  # helping action to track activity on input device
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
