import ctypes
import logging
import threading
import time

from core.DataTypes import DataType


class ModuleThread(threading.Thread):

    #def _init_(self):
    #    super()._init_()


    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for did, thread in threading._active.items():
            if thread is self:
                return did

    def stop(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            logging.error('Thread Exception raise failure.')


class EntityProperty:
    # version = "1.0"
    # description = "Basic Property Class for all Sensors, Outputs, Modules"

    __slots__ = ['category', 'name', 'description', '_value', '_old_value', 'type',
                 'last_update', 'last_change', 'step', 'available', '_logging', 'exposed', '__call', '__set', 'min',
                 'max', 'events',
                 'is_exclusive_output', 'registered_output_path', 'update_needs_thread', 'interval']

    def __init__(self, name: str = None, category: str = None, value=None, set=None, call=None,
                 description=None,
                 type=None, available=None, min=None, max=None, step=None, exposed=False, logging=False, update=None,
                 interval=None):

        # self.parent_module = parent  # parent_module that provides this property, parents needs .name property
        self.category = category  # path
        self.name = name  # name for this property
        self.description = description  # description
        self._old_value = None
        self.type = type  # DataType
        self.last_update = 0
        self.last_change = None
        self.exposed = exposed  # make it available for network
        self._logging = logging  #
        self.events = []
        self.__call = call
        self.available = available
        self.step = step
        self.min = min
        self.max = max
        self.__set = set  # is Output? private function! control access to it
        self.is_exclusive_output = False  # for unique access
        self.registered_output_path = None  # if exclusive
        self.interval = interval
        self.update_needs_thread = False  # for stuff with timeout like http etc

        if value is not None:
            self._value = value
        elif self.__call is not None:
            self._value = None
            self.update()
        else:
            self._value = None

    @property
    def value(self):
        return self._value

    @property
    def logging(self):
        return self._logging

    @logging.setter
    def logging(self, value):
        self._logging = bool(value)

    @property
    def path(self):
        return self.category + '/' + self.name

    @property
    def is_output(self):
        return callable(self.__set)

    @property
    def call(self):
        raise ValueError('Access to call function is restricted.')

    @call.setter
    def call(self, callable_function):
        if callable(callable_function):
            self.__call = callable_function

    @property
    def set(self):
        if self.is_exclusive_output:
            raise ValueError('Access to set function is restricted.')
        else:
            return self.__set

    @set.setter
    def set(self, callable_function):
        if callable(callable_function):
            self.__set = callable_function

    @value.setter
    def value(self, value):
        self.last_update = time.time()
        if value != self._value:
            # Todo: Check Dataype here!
            self._old_value = self._value
            self._value = value
            self.last_change = self.last_update

            for event in self.events:
                if callable(event):
                    logging.debug(f"{self.path} value: {value}, event fired: {event.__name__}")
                    event(self.path, self._value)
                else:
                    logging.error(self.name + ' event[' + str(event) + '] not a function!')

    def update(self):
        if self.__call is not None:
            value = self.__call()
            self.value = value
        else:
            logging.error('No Update Function for ' + self.name + ' given.')


class ThreadProperty(ModuleThread):
    # version = "1.0"
    # description = "Thread Property Class for Modules"

    __slots__ = ['category', 'name', 'description', '_value', 'type',
                 'last_update', 'last_change', '_logging', 'exposed', 'events', 'is_exclusive_output',
                 'interval', 'function', 'thread']

    def __init__(self, name: str = None,
                 category: str = None,
                 parent=None,
                 value=None,
                 description=None,
                 exposed=False,
                 logging=False,
                 interval=60,
                 function=None):

        # self.parent_module = parent  # parent_module that provides this property, parents needs .name property
        self.category = category  # category for tree in GUI, like sensor, output, sound, network
        self.name = name  # name for this property
        self.description = description  # description
        self._value = value  # value
        self.type = DataType.THREAD
        self.last_update = None
        self.last_change = None
        self._logging = logging
        self.exposed = exposed
        self.events = []
        self.is_exclusive_output = False  # for unique access
        self.interval = interval
        self.function = function

        ModuleThread.__init__(self, target=self.function, name='ThreadProperty_' + str(self.category) + str(self.name))
        # self.thread = ModuleThread(target=self.function)

    @property
    def logging(self):
        return self._logging

    @logging.setter
    def logging(self, value):
        self._logging = bool(value)

    def set(self, value):
        self.value = value

    @property
    def is_output(self):
        return True

    @property
    def path(self):
        return self.category + '/' + self.name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.last_update = time.time()
        if value != self._value:
            self._value = value
            self.last_change = self.last_update
            self.update()
        elif value:  # if thread is active and still value setted, we fire events
            for event in self.events:
                if callable(event):
                    event(self.path, self._value)
                else:
                    logging.error(self.name + ' event[' + str(event) + '] not a function!')

    def update(self):

        if self._value and not self.is_alive():
            #self.thread = ModuleThread(target=self.function)
            ModuleThread.__init__(self, target=self.function, name='ThreadProperty_' + str(self.category) + str(self.name))
            self.start()
            logging.info('(Re)Started Thread ' + (self.category or self.parent_module.name) + ' ' + self.name)

        elif not self._value and self.is_alive():
            self.stop()
            logging.info('Stopped Thread ' + (self.category or self.parent_module.name) + ' ' + self.name)


class FakeEvents:
    def append(fakeself, value):
        logging.debug('This is a static property, so no events will happen :-) ' + str(value))


class StaticProperty(object):
    # version = "1.0"
    # description = "Basic Property Class for all Statics"

    __slots__ = ['category', 'name', 'description', 'value', 'type', 'exposed']

    def __init__(self, name: str = None,
                 category: str = None,
                 parent=None,
                 value=None,
                 description=None,
                 type=None,
                 exposed=False):
        # self.parent_module = parent  # parent_module that provides this property, parents needs .name property
        self.category = category  # category for tree in GUI, like sensor, output, sound, network
        self.name = name  # name for this property
        self.description = description  # description
        self.value = value  # value
        self.type = type  # DataType
        self.exposed = exposed  # make it available for network

    @staticmethod
    def update():
        pass

    @property
    def path(self):
        return self.category + '/' + self.name

    @property
    def events(self):
        return FakeEvents()

    @property
    def is_output(self):
        return False

    @property
    def logging(self):
        return False

    @logging.setter
    def logging(self, value):
        if value:
            logging.error('Property: ' + self.path + ', static properties do not support logging.')

    @property
    def interval(self):
        return 0
