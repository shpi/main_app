# -*- coding: utf-8 -*-

from typing import Type, List, Optional
from time import time

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import Property, PropertyDict, IntervalProperty, Output, PropertyDictProperty


class PresenceHandlerSlot:
    __slots__ = '_timeout', '_set_trigger', '_triggertime', '_destprop'

    def __init__(self, destprop: Property, timeout: float):
        self._timeout = timeout
        self._destprop = destprop
        self._set_trigger = destprop.get_setvalue_func()
        self._triggertime: Optional[float] = None

    def trigger(self):
        self._triggertime = time()
        if self._destprop:
            self._set_trigger(True)

    def untrigger(self):
        self._triggertime = None
        if self._destprop:
            self._set_trigger(False)

    @property
    def is_triggered(self) -> bool:
        return self._triggertime is not None

    def check_timeout(self, now: float):
        if not self._triggertime:
            return

        if now > self._triggertime + self._timeout:
            self.untrigger()

    def unload(self):
        self.untrigger()
        self._destprop = None

    def __del__(self):
        self.unload()


class Presence(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = 'Central human presence detection logic'
    categories = 'Sensors', 'Hardware'

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)

        pr_triggered = self.properties["detecting_human"] \
            = Property(Output, DataType.PRESENCE, False,
                       desc='Sensors or other hardware detected human presence',
                       persistent=False)

        self._set_triggered = pr_triggered.get_setvalue_func()

        self._pd_handler = PropertyDict()
        self.properties["handlers"] = PropertyDictProperty(self._pd_handler,
                                                           desc='Registered handlers which can trigger presence events')

        self._handlers: List[PresenceHandlerSlot] = []
        self._pr_interval: Optional[IntervalProperty] = None  # Unannounced Property as interval caller

    def load(self):
        self._pr_interval = IntervalProperty(self._check_timeouts, 5., persistent_interval=False)

    def unload(self):
        self._pr_interval.value = None

    def _check_timeouts(self):
        now = time()
        for handler in self._handlers:
            handler.check_timeout(now)

    def _trigger_changed(self):
        for handler in self._handlers:
            if handler.is_triggered:
                # Set global trigger
                self._set_triggered(True)
                return

        # Release global trigger
        self._set_triggered(False)

    def register_handler(self, mclass: Type[ModuleBase], channel: str, timeout: float):
        key = f'{mclass.__name__}.{channel}'

        prop = self._pd_handler[key] = Property(Output, DataType.PRESENCE, False,
                                                desc='Trigger status of handler',
                                                persistent=False)

        # Call check function on each trigger changes
        prop.events.subscribe(self._trigger_changed, Property.UPDATED_AND_CHANGED)

        newhandler = PresenceHandlerSlot(prop, timeout)
        self._handlers.append(newhandler)
        return newhandler

    def unregister_handler(self, handler: PresenceHandlerSlot):
        self._handlers.remove(handler)
        handler.unload()
