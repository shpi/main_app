# -*- coding: utf-8 -*-

import importlib
import logging

from PySide2.QtCore import Property, Signal, Slot

from core.Settings import settings
from core.Constants import internal_modules, external_modules
from interfaces.Module import ModuleBase, ThreadModuleBase, ModuleCategories
from interfaces.PropertySystem import PersistentPropertyDict, Property
from core.Module import Module, ThreadModule


class Modules(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = "Module manager"
    categories = ModuleCategories._INTERNAL,

    def __init__(self, mainapp):
        ModuleBase.__init__(self, parent=mainapp, instancename=None)

        self.mainapp = mainapp
        self.all_modules_classes = internal_modules() | external_modules()

        self.pages = settings.list('pages', ['Home'])

        self._pages = dict()  # saves instance names per page / category

        for room in self._available_rooms:
            self._rooms[room] = settings.list(f"room/{room}", [])

        for category, modules in self.available_modules.items():
            cat = self._modules[category] = dict()
            for key in modules:
                cat[key] = settings.list(f"{category}/{key}")

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

    def load(self):
        pass

    def unload(self):
        pass

    @Signal
    def modulesChanged(self):
        pass

    @Signal
    def roomsChanged(self):
        pass

    @Property('QVariantMap', notify=roomsChanged)
    def rooms(self) -> dict:
        return self._rooms

    @Slot(str, str)
    def add_to_room(self, roomname, room):
        if room not in self._rooms[roomname]:
            self._rooms[roomname].append(room)
            settings.setstr(f"room/{roomname}", self._rooms[roomname])
            self.roomsChanged.emit()

    @Slot(str, str)
    def del_from_room(self, roomname, room):
        if room in self._rooms[roomname]:
            self._rooms[roomname].remove(room)
            settings.setstr(f"room/{roomname}", self._rooms[roomname])
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
        settings.set('available_rooms', self._available_rooms)
        self.roomsChanged.emit()

    @Slot(str)
    def delete_room(self, roomname):
        if roomname != 'Screensaver' and roomname in self._available_rooms:
            self._available_rooms.remove(roomname)
            settings.set("available_rooms", self._available_rooms)
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
            settings.setstr(category + "/" + classname, self._modules[category][classname])
            tempclass = getattr(importlib.import_module(category.lower() + '.' + classname), classname)

            self._instances[category][classname][instancename] = tempclass(instancename, self.inputs, settings)

            try:
                self.inputs.add(self._instances[category][classname][instancename].get_inputs())
            except Exception as e:
                logging.debug(e)
        self.modulesChanged.emit()

    @Slot(str, str, str)
    def remove_instance(self, category, classname, instancename):
        self._modules[category][classname].remove(instancename)
        settings.setstr(category + "/" + classname, self._modules[category][classname])
        # logging.warning(settings.getstr(category + "/" + classname))
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
