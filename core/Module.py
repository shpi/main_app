# -*- coding: utf-8 -*-

from logging import getLogger
from typing import Optional, Dict, Type, List, Iterator
from threading import Thread, enumerate
from time import sleep

from PySide2.QtCore import QObject

from core.Toolbox import thread_kill
from interfaces.Module import ModuleBase, ThreadModuleBase, IgnoreModuleException, ModuleInstancesView
from interfaces.PropertySystem import PropertyDict
from core.Logger import LogCall


logger = getLogger(__name__)
logcall = LogCall(logger)


class ModuleInstancesViewer(ModuleInstancesView):
    def __init__(self, module_class: Type[ModuleBase], content_dict: Dict[Optional[str], ModuleBase]):
        self._class = module_class
        self._instances = content_dict

    def __getitem__(self, instancename: Optional[str]) -> ModuleBase:
        return self._instances[instancename]

    def __len__(self) -> int:
        return len(self._instances)

    def __iter__(self) -> Iterator[Optional[str]]:
        return iter(self._instances)

    def values(self) -> Iterator[ModuleBase]:
        return iter(self._instances.values())

    def keys(self) -> Iterator[Optional[str]]:
        return iter(self._instances)


class Module:
    """
    Internal Module class holding the actual module instances.
    """
    modules_classes: Dict[str, Type[ModuleBase]] = {}
    instancesviewer_by_cls: Dict[str, ModuleInstancesViewer] = {}
    instancesdict_by_cls: Dict[str, Dict[Optional[str], ModuleBase]] = {}
    instances_in_loadorder: List["Module"] = []

    __slots__ = 'module_class', 'running', 'module_instancename', 'module_instance', 'loaded'

    @classmethod
    def unload_modules(cls):
        # Unload in reverse order
        for minst in reversed(Module.instances_in_loadorder):
            logcall(minst.unload)
        Module.instances_in_loadorder.clear()

    @classmethod
    def load_modules(cls):
        """
        Call load() in correct order on unloaded modules.
        """

        for m in cls.instances_in_loadorder:
            if not m.loaded and m.module_instance is not None:
                m.load()

    def __init__(self, module_class: Type[ModuleBase], instancename: str = None, parent: QObject = None):
        if not issubclass(module_class, ModuleBase):
            raise TypeError('Given module_class is not a subclass of ModuleBase:' + str(module_class))

        logger.info('Creating Module instance %s', module_class.__name__ + ('.' + instancename if instancename else ''))
        self.module_class = module_class

        # Check instancing policy with instancename

        if module_class.allow_maininstance == module_class.allow_instances:
            logger.error('For now, exactly one attribute must be set to True: allow_maininstance OR allow_instances. '
                         'Module: %s', str(module_class))

        if instancename is None:
            if not module_class.allow_maininstance:
                raise NotImplementedError(
                    'The module defined not to allow an unnamed main instance. Choose an instancename. '
                    '(allow_maininstance=False)')

        elif type(instancename) is str:
            if not module_class.allow_instances:
                raise NotImplementedError('The module defined not to allow named instances. (allow_instances=False)')

            if PropertyDict.path_sep in instancename:
                raise ValueError('Path seperator char is not allowed in the instancename:' + PropertyDict.path_sep)

        else:
            raise ValueError("Type of instancename must be str for individuals or None for main instance.")

        self.running = False

        # Remember instance name
        self.module_instancename = instancename

        self.module_instance: Optional[ModuleBase] = None  # Default on failures for checking in subclasses

        self.loaded = False

        # --- self complete ---

        if not module_class.available():
            logger.info('This module decided to not be avaliable on this system: %s', module_class)
            return

        clsstr = module_class.__name__

        try:
            # Instantiate the module class
            self.module_instance = module_class(parent, instancename)

        except IgnoreModuleException as e:
            logger.error('Module instance of %s denies instantiation: %s', clsstr, e)
            return

        except Exception as e:
            logger.error('Exception during init of %s with instancename %s: %s', clsstr, str(instancename), repr(e), exc_info=True)
            return

        # Lookup instance dict for specific subclass type
        instances = Module.instancesdict_by_cls.get(clsstr)
        viewer = Module.instancesviewer_by_cls.get(clsstr)

        if viewer is None:
            # It's the first instance of that module subclass.
            instances = Module.instancesdict_by_cls[clsstr] = {}
            viewer = Module.instancesviewer_by_cls[clsstr] = ModuleInstancesViewer(module_class, instances)
            module_class.instances = lambda cls: viewer

        elif instancename in viewer:
            raise ValueError(f"There is already an instancename of {instancename!s} for class {clsstr}")

        # Link functions and accessors to the module instance
        self.module_instance.instancename = lambda: self.module_instancename
        self.module_instance.modulename = lambda: clsstr

        # Store new instance by instancename
        instances[instancename] = self.module_instance

        Module.instances_in_loadorder.append(self)

    def load(self, force_reload=False):
        if self.loaded and not force_reload:
            logger.warning('Module has already been loaded: %s[%s]', self.module_class, self.module_instancename)
            return

        if self.module_instance is None:
            logger.warning('Unable to load moduleinstance because class init failed before or already loaded: %s[%s]',
                           self.module_class, self.module_instancename)
            return

        self.running = True
        logcall(self.module_instance.load, errmsg='Error during load() of module: %s', stack_trace=True)
        self.loaded = True

    def unload(self):
        self.running = False

        if self in self.instances_in_loadorder:
            self.instances_in_loadorder.remove(self)

        if self.module_instance is None or not self.loaded:
            # Module was not loaded
            return

        self.loaded = False

        logcall(self.module_instance.unload, errmsg='Error during unload() of module: %s', stack_trace=True)

        # Remove from dicts
        clsstr = self.module_class.__name__

        instances = Module.instancesdict_by_cls[clsstr]
        del instances[self.module_instancename]

        # Remove instance
        self.module_instance = None

        logger.info('Destroyed module instance %s ', clsstr + ('.' + self.module_instancename if self.module_instancename else ''))

    def __repr__(self):
        return f'<Module {self.module_class.__name__}[{self.module_instancename}]>'


class ThreadModule(Module):
    __slots__ = 'module_threadname', 'thread'

    thread_instances: List["ThreadModule"] = []

    def __init__(self, module_class: Type[ThreadModuleBase], instancename: str = None,
                 parent: QObject = None, threadname: str = None):

        Module.__init__(self, module_class, instancename=instancename, parent=parent)

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
            logger.error('Error on starting thread of module: %s', e, exc_info=True)

    def unload(self):
        # Stop a thread first
        self.running = False

        try:
            self.module_instance.stop()
            if self.thread.is_alive():
                self.thread.join(self.module_class.STOP_TIMEOUT)
            if self.thread.is_alive():
                logger.error('Thread of %s did not end after %s seconds. Killing it now.',
                             self.module_class, self.module_class.STOP_TIMEOUT)
                self.kill()

        except Exception as e:
            logger.error("Error on stopping threadmodule: %s", e, exc_info=True)

        # Handover to Modules unload
        Module.unload(self)

    @property
    def is_alive(self) -> bool:
        return self.thread.is_alive()

    def kill(self):
        if not self.thread.is_alive():
            return

        thread_kill(self.thread)

    def sleep(self, seconds) -> bool:
        """
        Sleeps "seconds" but may return earier, if module gets stopped.
        Do not rely on resulting sleep time for timediff calculations!
        """

        # ToDo: Real sleep with timeout

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
