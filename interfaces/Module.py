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


class ModuleBase(QObject, FakeABC):
    instances_by_cls: Dict[str, Dict[Optional[str], "ModuleBase"]] = {}

    @classmethod
    def destroy_module(cls, modinst: "ModuleBase", with_unload=True):
        modinst.running = False
        if with_unload:
            try:
                modinst.unload()
            except Exception as e:
                logging.error("Error on unloading module: " + str(e), exc_info=True)

        # Remove from dicts
        clsstr = modinst.__class__.__name__
        clsinstances = ModuleBase.instances_by_cls[clsstr]
        clsinstances.pop(modinst.instancename)
        if not clsinstances:
            # Remove empty cls instances dict
            ModuleBase.instances_by_cls.pop(clsstr)

        logging.info(f"Destroyed module instance '{modinst.instancename}' of {clsstr}")

    def __init__(self, instancename: str = None):
        QObject.__init__(self)
        logging.info(f"Created module instance {instancename!s} of {self.__class__.__name__}")

        if instancename is None:
            if not self.allow_maininstance:
                raise NotImplementedError(
                    "The module defined not to allow an unnamed main instance. Choose an instancename. "
                    "(allow_maininstance=False)")
        else:
            if not self.allow_instances:
                raise NotImplementedError("The module defined not to allow named instances. (allow_instances=False)")

            if type(instancename) is str:
                if "." in instancename:
                    raise ValueError("No dot '.' allowed in instancename.")

            elif type(instancename) is int:  # int allowed
                instancename = str(instancename)

            else:
                raise ValueError("Type of instancename must be str for individuals or None for main instance.")

        # Remember instance name
        self.instancename = instancename

        clsstr = self.__class__.__name__

        # Lookup instance dict for specific subclass type
        clsinstances = ModuleBase.instances_by_cls.get(clsstr)

        if clsinstances is None:
            # It's the first instance of that subclass.
            # Create a new dictionary for this subclass based on instancename.
            clsinstances = ModuleBase.instances_by_cls[clsstr] = {}

        if instancename in clsinstances:
            raise ValueError(f"There is already an instancename of {instancename} for class {clsstr}")

        # Store new instance by instancename
        clsinstances[instancename] = self

        self.running = False

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

    def __repr__(self):
        return f"<Module {self.__class__.__name__}[{self.instancename}]>"


class ThreadModuleBase(ModuleBase, Thread):
    MAX_SLEEP_INTERVAL = 2  # Deep sleep at most this amount of seconds
    STOP_TIMEOUT = 10  # Wait at least this seconds on thread stop.

    def __init__(self, instancename: str = None, threadname: str = None):
        ModuleBase.__init__(self, instancename=instancename)

        if not threadname:
            threadname = self.__class__.__name__ + ("-" + instancename if instancename else "")

        if threadname in (t.name for t in enumerate()):
            raise RuntimeError(f"threadname '{threadname}' collides with an existing thread name.")

        Thread.__init__(self, name=threadname)

    @classmethod
    def destroy_module(cls, modinst: "ThreadModuleBase", with_unload=True):
        # Stop a thread first
        modinst.running = False
        try:
            modinst.stop()
            if modinst.is_alive():
                modinst.join(ThreadModuleBase.STOP_TIMEOUT)
            if modinst.is_alive():
                print(f"Thread of {repr(modinst)} did not end after {ThreadModuleBase.STOP_TIMEOUT} seconds.")
        except Exception as e:
            logging.error("Error on stopping threadmodule: " + str(e), exc_info=True)

        # Handover to Modules destroy procedure
        ModuleBase.destroy_module(modinst=modinst, with_unload=with_unload)

    @abstractmethod
    def stop(self):
        pass

    def sleep(self, seconds):
        """
        Sleeps "seconds" but may return earier, if module gets stopped.
        Do not rely on resulting sleep time for timediff calculations!
        """

        remain = seconds
        # Loop in MAX_SLEEP_INTERVAL chunks
        while remain > ThreadModuleBase.MAX_SLEEP_INTERVAL and self.running:
            sleep(ThreadModuleBase.MAX_SLEEP_INTERVAL)
            remain -= ThreadModuleBase.MAX_SLEEP_INTERVAL

        # Sleep remaining fraction of MAX_SLEEP_INTERVAL
        if remain > 0 and self.running:
            sleep(remain)

    def __repr__(self):
        return f"<ThreadModule {self.__class__.__name__}[{self.instancename}]>"
