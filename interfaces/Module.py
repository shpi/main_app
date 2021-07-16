# -*- coding: utf-8 -*-

from abc import abstractmethod
from typing import Optional, Iterable, Type, Iterator, Mapping, Union, Dict, Any

from PySide2.QtCore import QObject

from core.FakeABC import FakeABC
from interfaces.PropertySystem import ModuleInstancePropertyDict


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
    """
    Minimal base class for each Module that can be used in the main app.
    """

    # Optionally provide a sequence of depending ModuleBase classes.
    # Import the modules and define a sequence of all dependencies in a sequence.
    # load() on your module will be called after each dependency has been loaded.
    depends_on: Iterable[Type["ModuleBase"]] = ()

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

        # Create at least an empty one.
        # Modify this attribute in __init__: Extend it or replace it with a prefilled one.
        self.properties = ModuleInstancePropertyDict()

        # TODO: app reference?

    @classmethod
    def available(cls) -> bool:
        """
        A class may tell here if it's avaliable for instantiation.
        Missing hardware etc. should return False.
        Default: True
        """
        return True

    def instancename(self) -> Optional[str]:
        """
        A module instance may read its assigned instance name by this function.
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
        Module class's instance view which contains all loaded instances of the specific class.
        """
        raise NotImplementedError("Function called too early. Don't use it in __init__.")

    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a function.
    def load(self):
        """
        Method to tell a module it's now allowed to load its majority of functions completely.
        Own and dependent properties are ready and loaded now.
        You're finally allowed to access dependend modules defined in "depends_on".
        """

    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a function.
    def unload(self):
        """
        Telling the module to stop and clean up before an unload.
        Close connections, destroy created instances, free memory, and most important release other references.
        """

    @classmethod
    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a direct class attribute to override this function.
    def categories(cls) -> Iterable[str]:
        """
        Iterable of categories this module matches
        A module must specify this attibute.
        """

    @classmethod
    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a direct class attribute to override this function.
    def allow_maininstance(cls) -> bool:
        """
        Allow creation of an unnamed main instance.
        A module must specify this attibute.
        """

    @classmethod
    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a direct class attribute to override this function.
    def allow_instances(cls) -> bool:
        """
        Allow creation of named instances.
        A module must specify this attibute.
        """

    @classmethod
    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a direct class attribute to override this function.
    def description(cls) -> str:
        """
        Describe your Module in a sentence.
        A module must specify this attibute.
        """

    def get_instance_names(self) -> Optional[Iterable[str]]:
        """
        Requires allow_instances=True

        This function will be called on the maininstance of the module.
        It may return an iterable of strings which will be used as instancenames and offered in the UI.

        If None, the user must specify instancenames.
        If sequence of strings, provided instancenames may be offered in the UI.
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
    """
    Minimal base class for each Module that can will be running in its own thread.
    Extends ModuleBase with some extra functions and requirements.
    """

    MAX_SLEEP_INTERVAL = 2  # Deep sleep at most this amount of seconds
    STOP_TIMEOUT = 10  # Wait at least this seconds on thread stop.

    def __init__(self, parent: QObject, instancename: str = None):
        ModuleBase.__init__(self, parent=parent, instancename=instancename)

    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a function.
    def run(self):
        """
        Mainthread function of the module.
        """

    @abstractmethod  # Means REQUIRED. A module must specify this attribute as a function.
    def stop(self):
        """
        Called when a ThreadModule should stop its thread for unloading the module.
        """

    def sleep(self, seconds: Union[int, float]) -> bool:
        """
        The ThreadModule should use this interruptable sleep function instead of Python's sleep().

        Sleeps "seconds" but may return earier, if module gets stopped.
        Do not rely on resulting sleep time for calculations based on the expected sleep time!

        Returns True on normal sleep exit.
        Returns False if module is stopping and sleep may have been interrupted earlier.
        """
        raise NotImplementedError("Function called too early. Don't use it in __init__.")

    def module_is_running(self) -> bool:
        """
        Returns True if the module should run.
        Use this function to exit loops etc.
        """
