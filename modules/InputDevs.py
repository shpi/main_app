# -*- coding: utf-8 -*-

import subprocess
import select
from struct import calcsize, unpack
from enum import Enum
from pathlib import Path
from re import compile, Match
from typing import Set, Optional
from io import StringIO
from threading import Thread
from logging import getLogger
from time import time

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import Property, PropertyDict, ROProperty, Output, PropertyDictProperty, Input
from modules.Presence import Presence, PresenceHandlerSlot

from core.Toolbox import thread_kill, Pipe

logger = getLogger(__name__)


_re_id = compile(r'I: Bus=([0-9a-f]{4}) Vendor=([0-9a-f]{4}) Product=([0-9a-f]{4}) Version=([0-9a-f]{4})')
_re_name = compile(r'N: Name="(.*)"')
_re_ev = compile(r'B: EV=(.*)')
_re_handlers_input_nr = compile(r'H: Handlers=.*event(\d+)')


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


# ToDo: add name and ev! Duplicates!
def id_from_id_match(m: Match) -> str:
    return ''.join(m.groups())


class KeyProperty(Property):
    __slots__ = '_write_func',

    KEY_DOWN = object()
    KEY_UP = object()

    _eventids = {KEY_DOWN, KEY_UP, Property.UPDATED, Property.UPDATED_AND_CHANGED}

    UNPRESSED = 0
    PRESSED = 1
    REPEATING = 2

    def __init__(self, desc: str):
        Property.__init__(self, Output, DataType.INTEGER, self.UNPRESSED, desc='Keycode: "' + desc + '"', persistent=False)
        self._write_func = self.get_setvalue_func()

    def update_state(self, newstate: int):
        self._write_func(newstate)

    def load(self):
        # TODO: Load key assignments and scripts
        super().load()

    def key_down(self):
        self.events.emit(self.KEY_DOWN)

    def key_up(self):
        self.events.emit(self.KEY_UP)


class InputDeviceKeymapProperty(PropertyDictProperty):
    def __init__(self, keymap: str):
        pd_keys = PropertyDict()

        with StringIO(keymap) as key_stream:
            for keyline in key_stream:
                keypair = keyline.rstrip().split(':', maxsplit=1)
                if len(keypair) != 2:
                    continue

                keyid, keyname = keypair
                if keyid in pd_keys:
                    continue
                pd_keys[keyid] = KeyProperty(desc=keyname)

        PropertyDictProperty.__init__(self, pd_keys, desc='List of available keys')


class InputDeviceProperty(PropertyDictProperty):
    _systembits = calcsize('P') * 8  # 16 byte for 32bit,  24 for 64bit
    _read_size = 16 if _systembits == 32 else 24

    def __init__(self, desc: str, ev_int: int, handler: str, keymap: str):
        if ev_int is None:
            ev_int = 0
        self._ev: Set[EvTypes] = {ev for ev in EvTypes if ev_int & (2 ** ev.value)}
        self._devpath = Path('/dev/input', handler)
        self._thread: Optional[Thread] = None
        self._stoppipe: Optional[Pipe] = None
        self._is_mouse = bool({EvTypes.EV_ABS, EvTypes.EV_REL}.intersection(self._ev))

        self._pr_use = Property(Input, DataType.BOOLEAN, True, desc='Use this input device')
        self._pr_keymap = InputDeviceKeymapProperty(keymap)

        pr_last_key = Property(Output, DataType.STRING, desc='Key of last input', persistent=False)
        self._set_last_key = pr_last_key.get_setvalue_func()

        pr_last_input = Property(Output, DataType.TIMESTAMP, desc='Timestamp of last keypress', persistent=False)
        self._set_last_input = pr_last_input.get_setvalue_func()

        pr_last_touch = Property(Output, DataType.TIMESTAMP, desc='Timestamp of last touch', persistent=False)
        self._set_last_touch = pr_last_touch.get_setvalue_func()

        pd = PropertyDict(
            name=ROProperty(DataType.STRING, desc, desc='Name of input device'),
            use_device=self._pr_use,
            keymap=self._pr_keymap,
            last_key=pr_last_key,
            last_input=pr_last_input,
            last_touch=pr_last_touch,
            dev_path=ROProperty(DataType.STRING, str(self._devpath), desc='Device path'),
            is_mouse=ROProperty(DataType.BOOLEAN, self._is_mouse, desc='Has mouse capabilities'),
            EV=ROProperty(DataType.LIST_OF_STRINGS, [ev.name for ev in self._ev], desc='Input device capabilities'),
        )

        self._threadname = 'InputDevs_devloop_' + handler

        PropertyDictProperty.__init__(self, pd, desc=desc)

    def load(self):
        self._pr_use.events.subscribe(self._use_changed, Property.UPDATED)
        super().load()

    def unload(self):
        # Stop thread if running
        self._use_changed(None)  # Stop the thread

        del self._pr_use
        del self._pr_keymap

        super().unload()  # Unload sub properties from tree

    def _use_changed(self, prop):
        newstate = self._pr_use.value

        if (prop is not None and newstate) == ((self._thread and self._thread.is_alive()) or False):
            # State satisfied.
            return

        if newstate and prop is not None:
            # New pipe
            self._stoppipe = Pipe()
            # New thread
            self._thread = Thread(target=self.devloop, name=self._threadname, daemon=True)
            # Run
            self._thread.start()
        else:
            if self._stoppipe:
                self._stoppipe.write(b'X')
            if self._thread and self._thread.is_alive():
                self._thread.join(5.)
                if self._thread.is_alive():
                    # Graceful exit did not work.
                    if not thread_kill(self._thread, 5):  # Fallback and timeout
                        logger.error('Could not kill thread of: %r', self)

    @property
    def use_device(self) -> bool:
        return self._pr_use.value

    @use_device.setter
    def use_device(self, use: bool):
        self._pr_use.value = use

    def devloop(self):
        try:
            logger.debug('Starting devloop on %s', str(self._devpath))
            self._devloop()
            logger.debug('Stopped devloop on %s', str(self._devpath))
        except Exception as e:
            logger.error('Exception occured during devloop of device %s: %s', self._devpath, repr(e), exc_info=True)

    def _devloop(self):
        # Minimize unnecesary dict lookups
        read_size = self._read_size
        ismouse = self._is_mouse
        stop_fd = self._stoppipe.read_fd
        incomplete_cnt = 0
        set_last_touch = self._set_last_touch
        set_last_input = self._set_last_input
        set_last_key = self._set_last_key
        pd_keymap = self._pr_keymap.value

        logger.debug(f'start reading: %s', self._devpath)
        with self._devpath.open('rb') as fd:
            input_fd = fd.fileno()
            read_fds = stop_fd, input_fd
            while True:
                r, _, _ = select.select(read_fds, (), ())

                if stop_fd in r:
                    self._stoppipe.read(8)  # To read and clear the buffer

                    # if input_fd in r:
                    #     fd.read(2048)  # To read and clear the buffer
                    break

                if input_fd not in r:
                    logger.error('Bad file descriptor was returned by select.')
                    break

                event = fd.read(read_size)
                if len(event) < read_size:
                    if incomplete_cnt > 5:
                        logger.error('Incomplete data received from input device multiple times. Stopping.')
                        break

                    incomplete_cnt += 1
                    logger.error('Incomplete data received from input device. Ignoring fragment.')
                    continue

                # Unpack struct
                timestamp, _id, evtype, keycode, value = unpack('llHHI', event)
                # print(keycode, value, evtype)

                # if ismouse:
                #     set_last_touch(time())
                # else:
                #     set_last_input(time())

                if evtype != 1:
                    # type 1 = key, we watch only keys!
                    continue

                # keycode = str(keycode)
                # set_last_key(keycode)
                #
                # prop: KeyProperty = pd_keymap.get(keycode)
                # if prop is None:
                #     logger.warning('Unknown keycode received: %s', keycode)
                #     continue

                # Remember key state
                # prop.update_state(value)


class InputDevs(ModuleBase):
    description = "Manages input devices"
    allow_maininstance = True
    allow_instances = False
    categories = 'Hardware', 'Input'
    depends_on = Presence,

    _INFOFILE = Path('/proc/bus/input/devices')
    _KEYMAP_EXECUTABLE = Path('keymap/keymap')

    @classmethod
    def available(cls) -> bool:
        ok = True  # Think positive

        if not cls._KEYMAP_EXECUTABLE.is_file():
            logger.info('InputDevs: /keymap/keymap executable not found.')
            ok = False

        if not cls._INFOFILE.is_file():
            logger.info('InputDevs: Missing input devices.')
            ok = False

        # Check having read access to input dev files
        devlist = sorted(list(Path('/dev/input').glob("event*")))
        first_dev = devlist and devlist[0] or None
        if first_dev:
            try:
                with first_dev.open('rb'):
                    pass
            except PermissionError:
                logger.info('InputDevs: No permission to open input dev files. '
                            'Try to add the user to the "input" group or run as root.')
                ok = False

        return ok

    def __init__(self, parent, instancename: str = None):
        ModuleBase.__init__(self, parent=parent, instancename=instancename)

        pr_last_input = Property(Output, DataType.TIMESTAMP, desc='Timestamp of last keypress', persistent=False)
        self._set_last_input = pr_last_input.get_setvalue_func()

        pr_last_touch = Property(Output, DataType.TIMESTAMP, desc='Timestamp of last touch', persistent=False)
        self._set_last_touch = pr_last_touch.get_setvalue_func()

        self._announce_human_handler: Optional[PresenceHandlerSlot] = None
        self._presence_maininstance: Optional[Presence] = None

        self._pd_available_devices = PropertyDict()

        self.properties.update(
            last_input=pr_last_input,
            last_touch=pr_last_touch,
            available_devices=PropertyDictProperty(self._pd_available_devices, 'Contains all available input devices'),
        )

    def load(self):
        self._check_inputdev_file()
        self._presence_maininstance: Presence = Presence.instances().get(None)
        if self._presence_maininstance:
            self._announce_human_handler \
                = self._presence_maininstance.register_handler(self.__class__, 'touched_display', 10.)

    def unload(self):
        # Early unload of properties to clear subscriptions.

        # Early unload to release subscriptions
        logger.info("Unloading InputDevs. May take a while...")
        self.properties.unload()

        if self._presence_maininstance and self._announce_human_handler:
            self._presence_maininstance.unregister_handler(self._announce_human_handler)
        self._announce_human_handler = None

        logger.info("Done unloading InputDevs.")

        del self._pd_available_devices

    def _last_input_changed(self):
        self._set_last_input(time())

    def _last_touch_changed(self):
        self._set_last_touch(time())
        self._announce_human_handler.trigger()

    def _check_inputdev_file(self):
        found: Set[str] = set()

        with self._INFOFILE.open(encoding="utf8") as file:
            input_id = None
            name = None
            ev = None
            handler = None
            keymap = None

            def finish_last():
                found.add(input_id)
                if input_id not in self._pd_available_devices:
                    prop = self._pd_available_devices[input_id] = InputDeviceProperty(
                        desc=name, ev_int=ev, handler=handler, keymap=keymap
                    )
                    # Add/update
                    prop['last_input'].events.subscribe(self._last_input_changed, Property.UPDATED_AND_CHANGED)
                    prop['last_touch'].events.subscribe(self._last_touch_changed, Property.UPDATED_AND_CHANGED)

            for line in file:
                line = line.strip()
                match_idline = _re_id.fullmatch(line)
                # Next device?
                if match_idline:
                    # It's a new idline
                    if input_id:
                        # Complete. Finish last inputdev
                        finish_last()

                    # Next device
                    input_id = id_from_id_match(match_idline)

                    # Reset vars
                    name = None
                    ev = None
                    handler = None
                    keymap = None
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
                    handler_num = int(match_handler_num.group(1))
                    # ToDo: gcc keymap.c -o keymap
                    p = subprocess.Popen(
                        ["keymap/keymap", str(handler_num)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        encoding="utf8"
                    )
                    keymap = p.communicate()[0].strip()
                    handler = f'event{handler_num}'

            finish_last()

        # Remove disconnected input devices
        for input_id in tuple(self._pd_available_devices):
            if input_id not in found:
                del self._pd_available_devices[input_id]
