# -*- coding: utf-8 -*-

import logging
from typing import Optional, Dict, Type, List
from threading import Thread, enumerate
from time import sleep

from interfaces.Module import ModuleBase, ThreadModuleBase
from core.Inputs import InputsDict


class Module:
    """
    Internal Module class holding the actual module instances.
    """

    instances_by_cls: Dict[str, Dict[Optional[str], "Module"]] = {}

    _inputs = InputsDict()

    def __init__(self, module_class: Type[ModuleBase], instancename: str = None):
        logging.info(f"Creating Module instance {instancename!s} of {module_class.__name__}")
        self.module_class = module_class

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

        clsstr = module_class.__name__

        # Lookup instance dict for specific subclass type
        clsinstances = Module.instances_by_cls.get(clsstr)

        if clsinstances is None:
            # It's the first instance of that subclass.
            # Create a new dictionary for this subclass based on instancename.
            clsinstances = Module.instances_by_cls[clsstr] = {}

        if instancename in clsinstances:
            raise ValueError(f"There is already an instancename of {instancename} for class {clsstr}")

        # Store new instance by instancename
        clsinstances[instancename] = self

        self.running = False
        try:
            # Instantiate the module class
            self.module_instance = module_class(instancename)
        except Exception as e:
            logging.error("Error on __init__ of module: " + str(e), exc_info=True)

    def load(self):
        self.running = True
        try:
            self.module_instance.load()
        except Exception as e:
            logging.error("Error on load() of module: " + str(e), exc_info=True)

    def unload(self):
        self.running = False

        try:
            self.module_instance.unload()
        except Exception as e:
            logging.error("Error on unload() of module: " + str(e), exc_info=True)

        # Remove from dicts
        clsstr = self.module_class.__name__
        clsinstances = Module.instances_by_cls[clsstr]
        clsinstances.pop(self.module_instancename)
        if not clsinstances:
            # Remove empty cls instances dict
            Module.instances_by_cls.pop(clsstr)

        # Remove instance
        del self.module_instance

        logging.info(f"Destroyed module instance '{self.module_instancename}' of {clsstr}")

    def __repr__(self):
        return f"<Module {self.module_class.__name__}[{self.module_instancename}]>"


class ThreadModule(Module):
    thread_instances: List["ThreadModule"] = []

    @classmethod
    def kill_threadmodules(cls):
        print("Kill threads")
        for tm in cls.thread_instances:
            Module._inputs.entries[tm.].set(0)

        # Temporary handling until modulemanager works
        ThreadModule.destroy_module(httpserver)

    def __init__(self, module_class: Type[ThreadModuleBase], instancename: str = None, threadname: str = None):
        Module.__init__(self, module_class, instancename=instancename)

        if not threadname:
            threadname = module_class.__name__ + ("-" + instancename if instancename else "")

        if threadname in (t.name for t in enumerate()):
            raise RuntimeError(f"threadname '{threadname}' collides with an existing thread name.")

        self.module_threadname = threadname
        self.thread = Thread(target=self.module_instance.run)

    def load(self):
        Module.load(self)

        try:
            # Start the modules' run function in a thread
            self.thread.start()
        except Exception as e:
            logging.error("Error on load() of module: " + str(e), exc_info=True)

    def unload(self):
        # Stop a thread first
        self.running = False

        try:
            self.module_instance.stop()
            if self.thread.is_alive():
                self.thread.join(self.module_instance.STOP_TIMEOUT)
            if self.thread.is_alive():
                print(f"Thread of {repr(self.module_class)} did not end after {self.module_instance.STOP_TIMEOUT} seconds.")

        except Exception as e:
            logging.error("Error on stopping threadmodule: " + str(e), exc_info=True)

        # Handover to Modules unload
        Module.unload(self)

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
        return f"<ThreadModule {self.module_class.__name__}[{self.module_instancename}]>"
