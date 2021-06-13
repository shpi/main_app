# -*- coding: utf-8 -*-

import logging
import ctypes
from typing import Optional, Dict, Type, List, Iterator
import threading
from threading import Thread, enumerate
from time import sleep, time

from PySide2.QtCore import QObject

from interfaces.Module import ModuleBase, ThreadModuleBase, IgnoreModuleException, ModuleInstancesView
from core.Inputs import InputsDict


class ModuleInstancesViewer(ModuleInstancesView):
    def __init__(self, module_class: Type[ModuleBase], content_dict: dict):
        self._class = module_class
        self._instances: Dict[Optional[str], ModuleBase] = content_dict

    def __getitem__(self, instancename: Optional[str]) -> ModuleBase:
        return self._instances[instancename]

    def __len__(self) -> int:
        return len(self._instances)

    def __iter__(self) -> Iterator[Optional[str]]:
        return iter(self._instances)


class Module:
    """
    Internal Module class holding the actual module instances.
    """
    modules_classes: Dict[str, Type[ModuleBase]] = {}
    instancesviewer_by_cls: Dict[str, ModuleInstancesViewer] = {}
    instancesdict_by_cls: Dict[str, Dict[Optional[str], ModuleBase]] = {}
    instances_in_loadorder: List["Module"] = []

    inputs = InputsDict()

    # Loop for checking logic regularly
    _last_update = 0  # to initialize everything
    _update_running = False

    @classmethod
    def get_classes(cls) -> List[Type[ModuleBase]]:
        return []

    @classmethod
    def check_loop(cls):
        if cls._update_running:
            return

        try:
            cls._update_running = True
            cls.inputs.update(cls._last_update)
        except Exception as e:
            logging.error(f"Error in check_loop: {e!s}", exc_info=True)

        finally:
            cls._last_update = int(time())
            cls._update_running = False

    @classmethod
    def unload_modules(cls):
        # Unload in reverse order
        for minst in reversed(list(Module.instances_in_loadorder)):
            minst.unload()

        # Legacy compatibility
        for key in Module.inputs.entries:
            if key.endswith('thread'):
                Module.inputs.entries[key].set(0)

    def __init__(self, module_class: Type[ModuleBase], instancename: str = None, parent: QObject = None):
        logging.info(f"Creating Module instance {instancename!s} of {module_class.__name__}")
        self.module_class = module_class

        # Check instancing policy with instancename
        if instancename is None:
            if not module_class.allow_maininstance:
                raise NotImplementedError(
                    "The module defined not to allow an unnamed main instance. Choose an instancename. "
                    "(allow_maininstance=False)")
        else:
            if not module_class.allow_instances:
                raise NotImplementedError("The module defined not to allow named instances. (allow_instances=False)")

            if type(instancename) is str:
                if "." in instancename:
                    raise ValueError("No dot '.' allowed in instancename.")

            else:
                raise ValueError("Type of instancename must be str for individuals or None for main instance.")

        # Remember instance name
        self.module_instancename = instancename

        self.running = False
        clsstr = module_class.__name__

        self.module_instance: Optional[ModuleBase] = None  # Default on failures for checking in subclasses
        try:
            # Instantiate the module class
            self.module_instance = module_class(parent)

        except IgnoreModuleException as e:
            logging.error(f"Module instance of {clsstr} denies instantiation: " + str(e))
            return

        # Link functions and accessors to the module instance
        self.module_instance.instancename = lambda: self.module_instancename

        # Lookup instance dict for specific subclass type
        viewer = Module.instancesviewer_by_cls.get(clsstr)
        instances = Module.instancesdict_by_cls.get(clsstr)

        if viewer is None:
            # It's the first instance of that module subclass.
            instances = Module.instancesdict_by_cls[clsstr] = {}
            viewer = Module.instancesviewer_by_cls[clsstr] = ModuleInstancesViewer(module_class, instances)
            module_class.instances = viewer

        if instancename in viewer:
            raise ValueError(f"There is already an instancename of {instancename!s} for class {clsstr}")

        # Store new instance by instancename
        instances[instancename] = self.module_instance

        Module.instances_in_loadorder.append(self)

    def load(self):
        if self.module_instance is None:
            return

        self.running = True
        try:
            self.module_instance.load()
        except Exception as e:
            logging.error("Error on load() of module: " + str(e), exc_info=True)

    def unload(self):
        self.running = False

        try:
            self.module_instance.unload()
            self.instances_in_loadorder.remove(self)
        except Exception as e:
            logging.error("Error on unload() of module: " + str(e), exc_info=True)

        # Remove from dicts
        clsstr = self.module_class.__name__

        instances = Module.instancesdict_by_cls[clsstr]
        instances.pop(self.module_instancename)

        # Remove instance
        del self.module_instance

        logging.info(f"Destroyed module instance '{self.module_instancename}' of {clsstr}")

    def __repr__(self):
        return f"<Module {self.module_class.__name__}[{self.module_instancename}]>"


class ThreadModule(Module):
    thread_instances: List["ThreadModule"] = []

    def __init__(self, module_class: Type[ThreadModuleBase], instancename: str = None, threadname: str = None):
        Module.__init__(self, module_class, instancename=instancename)

        if self.module_instance is None:
            # Module could not be instantiated. Should be handled in Module.__init__.
            return

        if not threadname:
            threadname = module_class.__name__ + ("-" + instancename if instancename else "")

        if threadname in (t.name for t in enumerate()):
            raise RuntimeError(f"threadname '{threadname}' collides with an existing thread name.")

        self.module_threadname = threadname
        self.module_instance.sleep = self.sleep  # Get access to sleep function
        self.module_instance.module_is_running = lambda: self.running
        self.thread = Thread(target=self.module_instance.run)

    def load(self):
        Module.load(self)

        if self.module_instance is None:
            return

        try:
            # Start the modules' run function in a thread
            self.thread.start()
        except Exception as e:
            logging.error("Error on starting thread of module: " + str(e), exc_info=True)

    def unload(self):
        # Stop a thread first
        self.running = False

        try:
            self.module_instance.stop()
            if self.thread.is_alive():
                self.thread.join(self.module_instance.STOP_TIMEOUT)
            if self.thread.is_alive():
                logging.error(f"Thread of {repr(self.module_class)} did not end after "
                              f"{self.module_instance.STOP_TIMEOUT} seconds. Killing it now.")
                self.kill()

        except Exception as e:
            logging.error("Error on stopping threadmodule: " + str(e), exc_info=True)

        # Handover to Modules unload
        Module.unload(self)

    @property
    def is_alive(self) -> bool:
        return self.thread.is_alive()

    @property
    def thread_id(self) -> Optional[int]:
        return self.thread.native_id

    @property
    def thread_killid(self) -> int:
        # return self.thread.ident
        if hasattr(self.thread, '_thread_id'):
            return self.thread._thread_id
        for did, thread in threading._active.items():
            if thread is self.thread:
                return did

    def kill(self):
        if not self.thread.is_alive():
            return

        thread_id = self.thread_killid
        print("kill ids should match:", thread_id, self.thread.ident)

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        print("Kill result:", res)
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            logging.error('Thread Exception raise failure.')

    def sleep(self, seconds) -> bool:
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

        return self.running

    def __repr__(self):
        return f"<ThreadModule {self.module_class.__name__}[{self.module_instancename}]>"
