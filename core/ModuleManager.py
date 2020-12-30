from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import os
import importlib
# from enum import Enum for self.state later
import threading
from datetime import datetime
from core.DataTypes import DataType


class ModuleManager(QObject):

    def __init__(self,inputs, settings: QSettings = None):

        super(ModuleManager, self).__init__()


        self.settings = settings
        self.inputs = inputs
        self.available_modules = {'Logic': ['Shutter'],
                                  'Info': ['Weather'],
                                  'UI' : ['UIShutter']}

        self._modules = dict()
        self._instances = dict()

        for category, modules in self.available_modules.items():
            self._modules[category] = {
            key : [(settings.value(category + "/" + key))]
            if isinstance(settings.value(category + "/" + key, []), str)
            else settings.value(category + "/" + key,[])
            if isinstance(settings.value(category + "/" + key, []), list)
            else []
            for key in modules}

        for category, value in self._modules.items():
            self._instances[category] = dict()

            for classname, instancenames in value.items():
                self._instances[category][classname] = dict()
                tempclass = getattr(importlib.import_module(category.lower() + '.' + classname), classname)

                for instancename in instancenames:
                    self._instances[category][classname][instancename] = tempclass(instancename,inputs,settings)
                    print(self._instances[category][classname][instancename])
                    try:
                        inputs.add(self._instances[category][classname][instancename].get_inputs())
                    except:
                        pass

    # for key,value in weather.items():
    #    inputs.add(value.get_inputs())

    def update(self):
        for category in self._instances:
            for classname in self._instances[category]:
                for instance in self._instances[category][classname]:
                    try:

                        self._instances[category][classname][instance].update()
                    except AttributeError:
                        pass

    @Signal
    def modulesChanged(self):
        pass

    @Property('QVariantMap', constant=True)
    def loaded_instances(self) -> dict:
        return self._instances


    @Property('QVariantMap', notify=modulesChanged)
    def modules(self):
        return self._modules


    @Slot(str, str, str)
    def add_instance(self, category, classname, instancename):
        self._modules[category][classname].append(instancename)
        self.settings.setValue(category + "/" + classname, self._modules[category][classname])
        tempclass = getattr(importlib.import_module(category.lower() + '.' + classname), classname)

        self._instances[category][classname][instancename] = tempclass(instancename,self.inputs,self.settings)
        print(self._instances[category][classname][instancename])
        try:
            self.inputs.add(self._instances[category][classname][instancename].get_inputs())
        except:
            pass
        self.modulesChanged.emit()



    @Slot(str,str,str)
    def remove_instance(self, category, classname, instancename):
        self._modules[category][classname].remove(instancename)
        self.settings.setValue(category + "/" + classname, self._modules[category][classname])
        self._instances[category][classname][instancename].delete_inputs()
        del self._instances[category][classname][instancename]
        self.modulesChanged.emit()




    @Slot(str,str, result='QVariantList')
    def instances(self, category, classname):

        if category != '' and classname != '':
            return (self._modules[category][classname])
        elif category != '':
            return list(self._modules[category].keys())
        else:
            return list(self._modules.keys())

    @Property(int, constant=True)
    def dim_timer(self):
        return int(self._dim_timer)

    @dim_timer.setter
    def set_dim_timer(self, seconds):
        self._dim_timer = int(seconds)
        self.settings.setValue("appearance/dim_timer", seconds)

