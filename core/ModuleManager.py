# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import logging
import importlib
from core.Toolbox import Pre_5_15_2_fix


class ModuleManager(QObject):
    def __init__(self, inputs, settings: QSettings):
        super().__init__()

        self.settings = settings
        self.inputs = inputs
        self.available_modules = {'Logic': ['Shutter', 'Thermostat'],
                                  'Info': ['Weather'],
                                  'UI': ['Shutter', 'ShowValue', 'MultiShutter'],
                                  'Connections': ['HTTP']}

        self._modules = dict()  # saves names of loaded instances
        self._instances = dict()  # instances itself

        self._available_rooms = self.settings.value(f"available_rooms", ['Screensaver'])

        if isinstance(self._available_rooms, str):
            self._available_rooms = [self._available_rooms]

        self._rooms = dict()  # saves instance names per room / category

        for room in self._available_rooms:
            rom = self.settings.value(f"room/{room}", [])

            if isinstance(rom, str):
                rom = [rom]

            if not isinstance(rom, list):
                rom = list()

            self._rooms[room] = rom

        for category, modules in self.available_modules.items():
            cat = self._modules[category] = dict()
            for key in modules:
                data = self.settings.value(f"{category}/{key}", [])

                if isinstance(data, str):
                    data = [data]

                if data is None:
                    data = []

                cat[key] = data

        for category, value in self._modules.items():
            self._instances[category] = dict()

            for classname, instancenames in value.items():
                self._instances[category][classname] = dict()
                tempclass = getattr(importlib.import_module(category.lower() + '.' + classname), classname)
                if isinstance(instancenames, list):
                    for instancename in instancenames:
                        logging.debug(f'Initiating {category}:{classname}:{instancename}')
                        self._instances[category][classname][instancename] = tempclass(instancename, inputs, settings)

                        # try:
                        if hasattr(self._instances[category][classname][instancename], 'get_inputs'):
                            inputs.add(self._instances[category][classname][instancename].get_inputs())
                        # except Exception as e:
                        #    logging.debug('here:' + str(e))

    """

    We use time scheduler of inputs class and register module as input vars,
    this approach uses fewer ressources and modules should be event driven, if possible

    def update(self):
        for category in self._instances:
            for classname in self._instances[category]:
                for instance in self._instances[category][classname]:
                    try:
                        logging.debug(f'calling update function of {category}:{classname}:{instance}')
                        self._instances[category][classname][instance].update()
                    except AttributeError:
                        pass
    """

    @Signal
    def modulesChanged(self):
        pass

    @Signal
    def roomsChanged(self):
        pass

    @Property('QVariantMap', notify=roomsChanged)
    def rooms(self) -> dict:
        return self._rooms

    """ @Slot(str, list)
    def set_rooms(self, roomname, rooms):

        if isinstance(rooms, str):
            rooms = [rooms]

        self._rooms[roomname] = rooms
        self.settings.setValue(f"room/{roomname}", rooms)
        self.roomsChanged.emit()
    """

    @Slot(str, str)
    def add_to_room(self, roomname, room):

        if room not in self._rooms[roomname]:
            self._rooms[roomname].append(room)
            self.settings.setValue(f"room/{roomname}", self._rooms[roomname])
            self.roomsChanged.emit()

    @Slot(str, str)
    def del_from_room(self, roomname, room):

        if room in self._rooms[roomname]:
            self._rooms[roomname].remove(room)
            self.settings.setValue(f"room/{roomname}", self._rooms[roomname])
            self.roomsChanged.emit()

    # @Property('QVariantList', notify=modulesChanged)
    def available_rooms(self) -> list:
        return self._available_rooms

    # @available_rooms.setter
    @Pre_5_15_2_fix('QVariantList', available_rooms, notify=roomsChanged)
    def available_rooms(self, value):

        if isinstance(value, list):
            if 'Screensaver' not in value:
                value.append('Screensaver')
        else:
            value = ['Screensaver']

        for room in value:
            if room not in self._rooms:
                self._rooms[room] = list()
            elif room == '':
                value.remove(room)

        self._available_rooms = list(set(value))
        self.settings.setValue(f"available_rooms", self._available_rooms)
        self.roomsChanged.emit()

    @Slot(str)
    def delete_room(self, roomname):

        if roomname in self._available_rooms:
            self._available_rooms.remove(roomname)
            self.settings.setValue("available_rooms", self._available_rooms)
            self.roomsChanged.emit()

    @Property('QVariantMap', notify=modulesChanged)
    def loaded_instances(self) -> dict:
        return self._instances

    @Property('QVariantMap', notify=modulesChanged)
    def modules(self):
        return self._modules

    @Slot(str, str, str)
    def add_instance(self, category, classname, instancename):
        if instancename not in self._modules[category][classname]:
            self._modules[category][classname].append(instancename)
            self.settings.setValue(category + "/" + classname, self._modules[category][classname])
            tempclass = getattr(importlib.import_module(category.lower() + '.' + classname), classname)

            self._instances[category][classname][instancename] = tempclass(instancename, self.inputs, self.settings)

            try:
                self.inputs.add(self._instances[category][classname][instancename].get_inputs())
            except Exception as e:
                logging.debug(e)
        self.modulesChanged.emit()

    @Slot(str, str, str)
    def remove_instance(self, category, classname, instancename):
        self._modules[category][classname].remove(instancename)
        self.settings.setValue(category + "/" + classname, self._modules[category][classname])
        self._instances[category][classname][instancename].delete_inputs()
        del self._instances[category][classname][instancename]
        self.modulesChanged.emit()

    @Slot(str, str, result='QVariantList')
    def instances(self, category, classname):
        if category != '' and classname != '':
            return self._modules[category][classname]
        elif category != '':
            return list(self._modules[category].keys())
        else:
            return list(self._modules.keys())

    @Slot(result='QVariantList')
    def all_instances(self) -> list:

        listed = list()

        for category in self._instances:
            for classname in self._instances[category]:
                for instance in self._instances[category][classname]:
                    listed.append(f'{category}/{classname}/{instance}')

        return listed
