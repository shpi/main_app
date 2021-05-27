# -*- coding: utf-8 -*-

from abc import abstractmethod
from enum import Enum, auto
from typing import Optional, Iterable

from PySide2.QtCore import QObject

from core.FakeABC import FakeABC


class IgnoreModuleException(BaseException):
    """
    Raise during load() or __init__ of your module to stop creation
    """


class ModuleCategories(Enum):
    _INTERNAL = auto()

    LOGIC = auto()
    HARDWARE = auto()
    INFO = auto()
    UI = auto()
    USER_MODULE = auto()


class ModuleBase(QObject, FakeABC):
    def __init__(self):
        FakeABC.__init__(self)
        QObject.__init__(self)

        # TODO: app reference

    def instancename(self) -> Optional[str]:
        """
        A module may read its instance name by this function
        """

    @abstractmethod
    def load(self):
        """
        Method to tell a module it's now allowed to load completely.
        self.properties ready.
        imports in required_packages satisfied.
        Do not use imports defined in required_packages until this call.
        No special imports in __init__ or on module level.
        Basic builtin python modules are allowed.
        Module may throw IgnoreModuleException here if feature not implemented.
        """

    @abstractmethod
    def unload(self):
        """
        Telling the module to stop and clean up before unload.
        Close connections, destroy instances, free memory, release references.
        """

    @classmethod
    @abstractmethod
    def categories(cls) -> Iterable[ModuleCategories]:
        """
        Iterable of categories this module matches
        """

    @classmethod
    @abstractmethod
    def allow_maininstance(cls) -> bool:
        """
        Allow creation of unnamed main instance.
        Yourclass()
        """

    @classmethod
    @abstractmethod
    def allow_instances(cls) -> bool:
        """
        Allow creation of named instances.
        Yourclass(instancename="instance_xyz")
        """

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """
        Describe your Module in a sentence.
        """

    @abstractmethod
    def get_inputs(self) -> list:
        """
        Module must provide its inputs by this function
        """


class ThreadModuleBase(ModuleBase):
    MAX_SLEEP_INTERVAL = 2  # Deep sleep at most this amount of seconds
    STOP_TIMEOUT = 10  # Wait at least this seconds on thread stop.

    def __init__(self):
        ModuleBase.__init__(self)

    @abstractmethod
    def run(self):
        """
        Mainthread function of the module.
        """

    @abstractmethod
    def stop(self):
        """
        Called when a ThreadModule should stop its thread for unloading the module.
        """

    def sleep(self, seconds):
        """
        The ThreadModule should use this interruptable sleep function instead of Python's sleep().
        Sleeps "seconds" but may return earier, if module gets stopped.
        Do not rely on resulting sleep time for calculations based on timediff!
        """
