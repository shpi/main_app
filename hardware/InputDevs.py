import logging
import subprocess
import threading
import struct
import ctypes
import time
import sys
from core.DataTypes import DataType
from functools import partial

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


class eThread(threading.Thread):

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for did, thread in threading._active.items():
            if thread is self:
                return did

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class InputDevs:
    FILENAME = '/proc/bus/input/devices'

    def __init__(self):

        super(InputDevs, self).__init__()

        self.devs = dict()
        self.inputs = dict()

        self.inputs['lastinput'] = dict()
        self.inputs['lastinput']['description'] = 'Last User Input'
        self.inputs['lastinput']['value'] = 'start'
        self.inputs['lastinput']['lastupdate'] = time.time()
        self.inputs['lastinput']['type'] = DataType.TIME
        self.inputs['lastinput']['interval'] = -1


        self.inputs['lasttouch'] = dict()
        self.inputs['lasttouch']['description'] = 'Last Mouse Input'
        self.inputs['lasttouch']['value'] = 'start'
        self.inputs['lasttouch']['lastupdate'] = time.time()
        self.inputs['lasttouch']['type'] = DataType.TIME
        self.inputs['lasttouch']['interval'] = -1

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
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    keys, stderr = p.communicate()
                    keys = set(keys.decode().strip().split('\n'))

                    device['keys'] = dict()

                    for key in keys:

                        try:
                            keydict = dict()
                            key = key.split(':')
                            keydict['lastupdate'] = 0
                            keydict['type'] = DataType.INT
                            keydict['value'] = None
                            keydict['description'] = key[1]
                            keydict['interval'] = -1
                            keydict['interrupts'] = []
                            # device['keys'][int(key[0])] = keydict
                            self.inputs[f'dev/{str(id)}/keys/{str(key[0])}'] = keydict

                        except IndexError:
                            pass

                self.devs[id] = device

        f.close()

        for id, subdevice in self.devs.items():
            self.inputs[f'dev/{str(id)}/thread'] = dict()
            self.inputs[f'dev/{str(id)}/thread']['description'] = 'Thread for ' + subdevice['name']
            self.inputs[f'dev/{str(id)}/thread']['value'] = 1
            self.inputs[f'dev/{str(id)}/thread']['interval'] = 30
            self.inputs[f'dev/{str(id)}/thread']['lastupdate'] = 0
            self.inputs[f'dev/{str(id)}/thread']['ismouse'] = 1 if ('EV_ABS' in subdevice['EV'] or 'EV_REL' in subdevice['EV']) else 0
            self.inputs[f'dev/{str(id)}/thread']['interrupts'] = []

            self.inputs[f'dev/{str(id)}/thread']['thread'] = eThread(target=self.devloop, args=(f"/dev/input/{subdevice['event'][0]}", id))
            self.inputs[f'dev/{str(id)}/thread']['type'] = DataType.BOOL
            self.inputs[f'dev/{str(id)}/thread']['call'] = partial(self.update, id)
            self.inputs[f'dev/{str(id)}/thread']['set'] = partial(self.control_thread, id)
            #self.inputs[f'dev/{str(id)}/thread']['thread'].start()

    def get_inputs(self) -> dict:


        return self.inputs

    def update(self, id):

        if self.inputs[f'dev/{str(id)}/thread']['value'] and (not self.inputs[f'dev/{str(id)}/thread']['thread'] or not self.inputs[f'dev/{str(id)}/thread']['thread'].is_alive()):
            self.inputs[f'dev/{str(id)}/thread']['thread'] = eThread(target=self.devloop, args=("/dev/input/" + self.devs[id]['event'][0], id))
            self.inputs[f'dev/{str(id)}/thread']['thread'].start()
            logging.error('Restarted Thread for Input Device: ' + id)

        elif not self.inputs[f'dev/{str(id)}/thread']['value'] and self.inputs[f'dev/{str(id)}/thread']['thread'].is_alive():
            self.inputs[f'dev/{str(id)}/thread']['thread'].raise_exception()
            logging.error('Stopped Thread for Input Device: ' + id)

        return self.inputs[f'dev/{str(id)}/thread']['value']


    def control_thread(self, id, value):

        if value != self.inputs[f'dev/{str(id)}/thread']['value']:
            if value and (
                    not self.inputs[f'dev/{str(id)}/thread']['thread']
                    or not self.inputs[f'dev/{str(id)}/thread']['thread'].is_alive()):
                self.inputs[f'dev/{str(id)}/thread']['thread'] = eThread(
                    target=self.devloop, args=("/dev/input/" + self.devs[id]['event'][0], id))
                self.inputs[f'dev/{str(id)}/thread']['thread'].start()
            elif not value and self.inputs[f'dev/{str(id)}/thread']['thread'].is_alive():
                self.inputs[f'dev/{str(id)}/thread']['thread'].raise_exception()

            self.inputs[f'dev/{str(id)}/thread']['value'] = value

    def devloop(self, devpath, id):

        systembits = (struct.calcsize("P") * 8)
        try:
            logging.debug(f'start reading: {devpath}')
            with open(devpath, 'rb') as devfile:
                while self.inputs[f'dev/{str(id)}/thread']['value']:
                    # 16 byte for 32bit,  24 for 64bit
                    event = devfile.read(16 if systembits == 32 else 24)
                    (timestamp, _id, type, keycode, value) = struct.unpack('llHHI', event)

                    if (type == 1):  # type 1 = key
                        try:
                            self.inputs['lastinput']['value'] = devpath
                            self.inputs['lastinput']['lastupdate'] = timestamp

                            if self.inputs[f'dev/{str(id)}/thread']['ismouse']:
                                self.inputs['lasttouch']['value'] = devpath
                                self.inputs['lasttouch']['lastupdate'] = timestamp

                            self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['value'] = value
                            self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['lastupdate'] = time.time()
                            self.inputs[f'dev/{str(id)}/thread']['lastupdate'] = timestamp

                            if 'interrupts' in self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']:
                                for function in self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['interrupts']:
                                    function(f'dev/{str(id)}/keys/{str(keycode)}', value,
                                             self.inputs[f'dev/{str(id)}/thread']['ismouse'])

                            if 'interrupts' in self.inputs[f'dev/{str(id)}/thread']:
                                for function in self.inputs[f'dev/{str(id)}/thread']['interrupts']:
                                    function(f'dev/{str(id)}', value, self.inputs[f'dev/{str(id)}/thread']['ismouse'])

                        except KeyError:
                            self.inputs[f'dev/{str(id)}/keys/{str(keycode)}'] = dict()
                            self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['value'] = value
                            self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['lastupdate'] = timestamp

        except Exception as e:
            #self.inputs[f'dev/{str(id)}/thread']['value'] = 0
            self.inputs[f'dev/{str(id)}/thread']['lastupdate'] = time.time()

            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'dev/{str(id)}/thread failed: {e} in line {line_number}')

