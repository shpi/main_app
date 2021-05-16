# -*- coding: utf-8 -*-

import logging
from abc import abstractmethod
from enum import Enum, auto
from typing import Optional, Dict
from threading import Thread, enumerate
from time import sleep

from PySide2.QtCore import QObject

from core.FakeABC import FakeABC


class ModuleCategories(Enum):
    LOGIC = auto()
    INFO = auto()
    UI = auto()
    CONNECTIONS = auto()


class ModuleBase(FakeABC):
    def __init__(self, instancename: str = None):
        super().__init__()
        self.instancename = instancename

    @abstractmethod
    def load(self):
        """
        This method may be called multiple times when this Module is being
            put into running state again by modulemanager.
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
        This method may be called multiple times when this Module is being
            put into running state again by modulemanager.
        Stop and clean up.
        Close connections, destroy instances, free memory, release references.
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


class ThreadModuleBase(ModuleBase, Thread):
    MAX_SLEEP_INTERVAL = 2  # Deep sleep at most this amount of seconds
    STOP_TIMEOUT = 10  # Wait at least this seconds on thread stop.

    def __init__(self, instancename: str = None, threadname: str = None):
        ModuleBase.__init__(self, instancename)


    @abstractmethod
    def stop(self):
        """
        Stop the thread and the module
        """

    def sleep(self, seconds):
        """
        Sleeps "seconds" but may return earier, if module gets stopped.
        Do not rely on resulting sleep time for timediff calculations!
        """
