import subprocess
import threading
from PySide2.QtCore import QObject
import struct


class InputDevs(QObject):

    FILENAME = '/proc/bus/input/devices'

    def __init__(self, parent: QObject = None):
        super(InputDevs, self).__init__(parent)

        self.devs = dict()
        self.inputs = dict()

        with open(self.FILENAME, 'r') as f:

            while True:
                line = f.readline()

                if not line:
                    break

                if line.startswith('I: Bus='):
                    device = dict()
                    id = int(''.join(filter(str.isdigit, line)))

                if line.startswith('N: Name='):
                    device['name'] = line[len('N: Name='):].strip('"\n')

                if line.startswith('H: Handlers='):
                    events = list(line[len('H: Handlers='):].rstrip().split(' '))
                    device['event'] = list(filter(lambda x: x.startswith('event'), events))

                    p = subprocess.Popen(["keymap/keymap", ''.join(filter(str.isdigit,str(device['event'])))],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    keys, stderr = p.communicate()
                    keys = set(keys.decode().strip().split('\n'))

                    device['keys'] = dict()

                    for key in keys:

                        try:
                            keydict = dict()
                            key = key.split(':')
                            keydict['lastupdate'] = 0
                            keydict['type'] = 'bool'
                            keydict['value'] = None
                            keydict['description'] = key[1]
                            keydict['interval'] = -1
                            # device['keys'][int(key[0])] = keydict
                            self.inputs[f'dev/{str(id)}/keys/{str(key[0])}'] = keydict

                        except IndexError:
                            pass

                if line.startswith('B: EV='):
                    device['EV'] = line[len('B: EV='):].strip('"\n')

                self.devs[id] = device

        f.close()

        for id, subdevice in self.devs.items():
            self.devs[id]['thread'] = threading.Thread(target=self.devloop,args = (f"/dev/input/{subdevice['event'][0]}",id) )
            self.devs[id]['running'] = True
            self.devs[id]['thread'].start()

    def get_inputs(self) -> dict:
        return self.inputs

    def devloop(self, devpath, id):
        systembits = (struct.calcsize("P") * 8)

        with open(devpath, 'rb') as devfile:

            while self.devs[id]['running']:
                event = devfile.read(16 if systembits == 32 else 24)  #16 byte for 32bit,  24 for 64bit
                (timestamp, _id, type, keycode, value) = struct.unpack('llHHI', event)

                if (type == 1):

                    try:
                        self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['value'] = value
                        self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['lastupdate'] = timestamp

                    except KeyError:
                        self.inputs[f'dev/{str(id)}/keys/{str(keycode)}'] = dict()
                        self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['value'] = value
                        self.inputs[f'dev/{str(id)}/keys/{str(keycode)}']['lastupdate'] = timestamp

