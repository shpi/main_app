# -*- coding: utf-8 -*-

from abc import abstractmethod
from enum import Enum, auto
from typing import Optional, Iterable, Type, Iterator, Mapping, Union, Dict, Any

from PySide2.QtCore import QObject

from core.FakeABC import FakeABC
from interfaces.PropertySystem import PropertyDict, ModuleInstancePropertyDict
from interfaces.MainApp import MainAppBase


class IgnoreModuleException(BaseException):
    """
    Raise during load() or __init__ of your module to stop creation
    """


# class ModuleCategories(Enum):
#    _INTERNAL = auto()  # Hide this module in module manager
#    _AUTOLOAD = auto()  # Automatically loads this internal module
#    LOGIC = auto()
#    HARDWARE = auto()
#    INFO = auto()
#    UI = auto()
#    USER_MODULE = auto()


class ModuleBase(QObject, FakeABC):
    def __init__(self, parent: QObject = None, instancename: str = None):
        """
        A module instance identified by instancename is being created.
        instancename may be None, if allow_maininstance is defined as True.

        If instancename is a string this instance represents a specific, named
        instance of this module, if allow_instances is defined as True.

        The instancename must not be saved and may be aqcuired by calling self.instancename() later.

        Each module instance should create a new ModuleInstancePropertyDict containing its Properties.
        Do not read or write from Properties during __init__ because it's path and dependencies are not ready.

        Save the populated ModuleInstancePropertyDict instance into self.properties.
        You may access properties by self.properties["propname"] later or additionally save specific properties into
        'self' directly for speedups.
        """

        FakeABC.__init__(self)  # Manual check for matching all abstract base classes.
        QObject.__init__(self, parent)

        self.properties = ModuleInstancePropertyDict()

        # TODO: app reference

    @classmethod
    def available(cls) -> bool:
        """
        Class may tell here if it is avaliable for instantiation.
        Missing hardware etc. should return False.
        Default: True
        """
        return True

    def instancename(self) -> Optional[str]:
        """
        A module may read its assigned instance name by this function.
        This function is only available after completing __init__.
        During __init__, use given argument "instancename".
        """
        raise NotImplementedError("Function called too early. Don't use it in __init__.")

    def modulename(self) -> str:
        """
        modulename refers to class name of module.
        This function is only available after completing __init__.
        """
        raise NotImplementedError("Function called too early. Don't use it in __init__.")

    @classmethod
    def instances(cls) -> "ModuleInstancesView":
        """
        Module class's instance view which contains all loaded instances.
        """
        raise NotImplementedError("Function called too early. Don't use it in __init__.")

    @abstractmethod
    def load(self):
        """
        Method to tell a module it's now allowed to load completely.
        self.properties are ready then.
        imports in required_packages satisfied.
        Do not use imports defined in required_packages until this call.
        No special imports in __init__ or on module level.
        Basic builtin python modules are allowed.
        Module may throw IgnoreModuleException here if feature not implemented.
        A module must specify this function.
        """

    @abstractmethod
    def unload(self):
        """
        Telling the module to stop and clean up before unload.
        Close connections, destroy created instances, free memory, release other references.
        A module must specify this function.
        """

    @classmethod
    @abstractmethod
    def categories(cls) -> Iterable[str]:
        """
        Iterable of categories this module matches
        A module must specify this attibute.
        """

    @classmethod
    def depends_on(cls) -> Optional[Iterable[Type["ModuleBase"]]]:
        """
        An iterable of module classes, on which this module depends on.
        A module may specify this attibute.
        """
        return None

    @classmethod
    @abstractmethod
    def allow_maininstance(cls) -> bool:
        """
        Allow creation of an unnamed main instance.
        A module must specify this attibute.
        """

    @classmethod
    @abstractmethod
    def allow_instances(cls) -> bool:
        """
        Allow creation of named instances.
        A module must specify this attibute.
        """

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """
        Describe your Module in a sentence.
        A module must specify this attibute.
        """

    def get_instance_names(self) -> Optional[Iterable[str]]:
        """
        This function may be called on the maininstance of the module.
        It may return an iterable of strings which will be used as instancenames and offered in the UI.

        Requires allow_instances=True

        If None, the user must specify instancenames.
        If list of strings, provided instancenames may be offered in the UI.
        """
        return None

    def qml_context_properties(self) -> Optional[Dict[str, Any]]:
        return None


class ModuleInstancesView(Mapping):
    def __getitem__(self, instancename: Optional[str]) -> ModuleBase:
        pass

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator[ModuleBase]:
        pass


class ThreadModuleBase(ModuleBase):
    MAX_SLEEP_INTERVAL = 2  # Deep sleep at most this amount of seconds
    STOP_TIMEOUT = 10  # Wait at least this seconds on thread stop.

    def __init__(self, parent: QObject, instancename: str = None):
        ModuleBase.__init__(self, parent=parent, instancename=instancename)

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

    def sleep(self, seconds: Union[int, float]) -> bool:
        """
        The ThreadModule should use this interruptable sleep function instead of Python's sleep().
        Sleeps "seconds" but may return earier, if module gets stopped.
        Do not rely on resulting sleep time for calculations based on timediff!

        Returns True on normal sleep exit.
        Returns False if module is stopping and sleep may have been interrupted earlier.
        """
        raise NotImplementedError("Function called too early. Don't use it in __init__.")

    def module_is_running(self) -> bool:
        """
        Returns True if the module should run.
        Use this function to exit loops.
        """
