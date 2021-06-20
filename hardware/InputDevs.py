import logging
import struct
import subprocess
import sys
from enum import Enum
from functools import partial
from pathlib import Path
from re import compile, Match
from typing import Set

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase, ModuleCategories, IgnoreModuleException
from interfaces.PropertySystem import Property, PropertyDict


_re_id = compile(r'I: Bus=([0-9a-f]{4}) Vendor=([0-9a-f]{4}) Product=([0-9a-f]{4}) Version=([0-9a-f]{4})')
_re_name = compile(r'N: Name="(.*)"')
_re_ev = compile(r'B: EV=(.*)')
_re_handlers_input_nr = compile(r'H: Handlers=.*event(\d+)')


def id_from_id_match(m: Match) -> str:
    return ''.join(m.group(x) for x in range(4))


class InputDeviceProperty(PropertyDict):
    # _eventids = Property._eventids |

    def __init__(self, desc: str, ev: Set, handler: int, keymap: str):
        Property.__init__(self, datatype=DataType.BOOLEAN, initial_value=True, desc=desc)
        self._devpath = Path('/dev/input' + str(handler))

    @property
    def use_device(self) -> bool:
        return self.value

    @use_device.setter
    def use_device(self, use: bool):
        self.value = use


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


class InputDevs(ModuleBase):
    description = "Manages input devices"
    allow_maininstance = True
    allow_instances = False
    categories = ModuleCategories._INTERNAL,

    _INFOFILE = Path('/proc/bus/input/devices')

    def __init__(self, parent, instancename: str = None):
        if not self._INFOFILE.is_file():
            raise IgnoreModuleException('File not found: %s', (self._INFOFILE,))

        ModuleBase.__init__(self, parent=parent, instancename=instancename)

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

        self._pr_last_input = Property()
        self._pr_last_touch = Property()

        self._pd_available_devices = PropertyDict()
        self.properties = PropertyDict(
            last_input=self._pr_last_input,
            last_touch=self._pr_last_touch,
            available_devices=Property(
                DataType.PROPERTYDICT,
                self._pd_available_devices,
                desc='Contains all available input devices',
            ),
        )


                    p = subprocess.Popen(["keymap/keymap", ''.join(filter(str.isdigit, str(device['event'])))],
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding="utf8")

                    keys_output = p.communicate()[0].strip()
                    keys = set(keys_output.split('\n'))

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
                                type=DataType.INTEGER,
                                interval=-1)

                        except IndexError:
                            pass

                self.devs[id] = device

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

    def load(self):
        self._check_inputdev_file()

    def unload(self):
        pass

    def check_inputdev_file(self):
        found: Set[str] = set()

        with self._INFOFILE.open(encoding="utf8") as file:
            input_id = None
            name = None
            ev = None
            handler = None
            keymap = None
            for line in file:
                match_idline = _re_id.fullmatch(line)
                # Next device?
                if match_idline:
                    if input_id:
                        # Device complete
                        self._pd_available_devices[input_id] = InputDeviceProperty(desc=name, ev=ev, handler=handler, keymap=keymap)

                    # Next device
                    input_id = id_from_id_match(match_idline)

                    # Reset vars
                    name = None
                    ev = None
                    handler = None
                    keymap = None
                    found.add(input_id)
                    if input_id in self._pd_available_devices:
                        # Skip it. Already in PropertyDict
                        input_id = None

                elif input_id is None:
                    # Line is obsolete
                    continue

                # Line could be relevant

                match_name = _re_name.fullmatch(line)
                if match_name:
                    name = match_name.group(1)

                match_ev = _re_ev.fullmatch(line)
                if match_ev:
                    ev = int(match_ev.group(1), 16)

                match_handler_num = _re_handlers_input_nr.match(line)
                if match_handler_num:
                    handler = int(match_handler_num.group(1))
                    p = subprocess.Popen(
                        ["keymap/keymap", str(handler)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        encoding="utf8"
                    )
                    keymap = p.communicate()[0].strip()

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
                            if ismouse:
                                self.properties['lasttouch'].value = value

                            if value != self.properties['lastinput'].value:
                                logging.debug(devpath + ' key: ' + str(keycode) + ', ' + str(value))

                            self.properties['lastinput'].value = value
                            self.properties[f'{id}/thread'].value = 1  # helping to track activity on input device
                            self.properties[f'{id}/key_{str(keycode)}'].value = value

                        except KeyError:
                            self.properties[f'{id}/key_{str(keycode)}'] = EntityProperty(parent=self,
                                                                                         category='input_dev',
                                                                                         entity=id,
                                                                                         name=str(keycode),
                                                                                         description=str(keycode),
                                                                                         type=DataType.INTEGER,
                                                                                         interval=-1)
                            self.properties[f'{id}/key_{str(keycode)}'].value = value

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'input_dev/{id}/thread failed: {e} in line {line_number}')
