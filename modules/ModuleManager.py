# -*- coding: utf-8 -*-

from logging import getLogger
from typing import Optional, Dict, Any, Union, Type, Iterable, List

from PySide2.QtCore import Property as QtProperty, Signal, Slot
from PySide2.QtQml import QQmlApplicationEngine

from core.Settings import settings, new_settings_instance
from core.Constants import internal_modules, external_modules, always_preload_modules
from interfaces.Module import ModuleBase, ThreadModuleBase
from interfaces.PropertySystem import Property, PropertyDict, IntervalProperty, ModuleInstancePropertyDict, \
    properties_start, properties_stop
from interfaces.DataTypes import DataType
from core.Module import Module, ThreadModule
from core.Logger import LogCall


logger = getLogger(__name__)
logcall = LogCall(logger)


def map_classes(classes: Iterable) -> Dict[str, Type[ModuleBase]]:
    return {cls.__name__: cls for cls in classes}


def map_class_categories(classes: Iterable[Type[ModuleBase]]) -> Dict[str, List[Type[ModuleBase]]]:
    out = {}

    for mclass in classes:
        for mcat in mclass.categories:  # type: str
            if mcat in out:
                catlist = out[mcat]
            else:
                catlist = out[mcat] = []

            catlist.append(mclass)
    return out


class Modules(ModuleBase):
    """
    "Modules" module which interfaces with Module class for qml
    """

    allow_maininstance = True
    allow_instances = False
    description = "Module manager"
    categories = ()

    _main_instance: Optional["Module"] = None

    modules_changed = Signal()
    categories_changed = Signal()

    all_modules_classes = internal_modules() | external_modules()
    all_modules_classes_by_str = map_classes(all_modules_classes)
    module_categories = map_class_categories(all_modules_classes)

    _root_properties = PropertyDict.root(allowcreate=True)

    @classmethod
    def selfload(cls, mainapp):
        if cls._main_instance is not None:
            raise ValueError('"Modules" module is already selfloaded.')

        # Instantiate my main instance
        m = cls._main_instance = Module(cls, parent=mainapp)

        # Load this module
        m.loaded = True
        m.load(force_reload=True)  # Module.load() is called which calls our load()

    def __init__(self, parent, instancename: str = None):
        if self._main_instance is not None:
            raise ValueError('"Modules" module has already been instantiated.')

        ModuleBase.__init__(self, parent=parent, instancename=instancename)

        self.mainapp = parent

        self.qmlengine: QQmlApplicationEngine = parent.engine

        # Add contextproperties from mainapp
        self.add_module_contextproperties(parent)

        # self.properties = ModuleInstancePropertyDict()
        ModuleInstancePropertyDict.changed_callback = lambda: self.categories_changed.emit()

    def qml_context_properties(self) -> Optional[Dict[str, Any]]:
        return {'modules': self}

    def load(self):
        logcall(properties_start)

        if self._root_properties is not PropertyDict.root():
            raise ReferenceError('Root property has already been created before.')

        # Initialize root propertydict
        self._root_properties.load()

        # Add this instance manually
        self.add_module_properties(self)
        self.add_module_contextproperties(self)

        # Load other modules which are always loaded or are saved in settings

        to_load = set(settings.childGroups()) | set(m.__name__ for m in always_preload_modules())
        logger.info("Adding modules now: %s", str(to_load))

        for classname in to_load:
            # Iterate over top level settings which contain the settings for modules and their instances
            cls = self.all_modules_classes_by_str.get(classname)
            if cls is None:
                # Unknown class or not available anymore.
                continue

            if cls.allow_maininstance and not cls.allow_instances:
                # Only a main instance expected
                if settings.value(f'{classname}/__load', True):
                    self.add_module_instance(cls)

            elif cls.allow_instances() and not cls.allow_maininstance():
                # Iterate over instances
                instance_settings = new_settings_instance(classname)
                for instancename in instance_settings.childGroups():
                    if instance_settings.value(f'{instancename}/__load', True):
                        self.add_module_instance(cls, instancename)
            else:
                # ToDo
                pass

        # Call load() in correct ordner on still unloaded modules
        Module.load_modules()

    def add_module_instance(self, class_or_class_str: Union[Type[ModuleBase], str], instancename: str = None):
        if type(class_or_class_str) is str:
            mcls = self.all_modules_classes_by_str.get(class_or_class_str)
        elif issubclass(class_or_class_str, ModuleBase):
            mcls = class_or_class_str
        else:
            logger.error('Could not find module class or invalid class type: %s', class_or_class_str)
            return

        try:
            if issubclass(mcls, ThreadModuleBase):
                m = ThreadModule(mcls, instancename)  # ToDo: Parenting
            elif issubclass(mcls, ModuleBase):
                m = Module(mcls, instancename)
            else:
                return
        except Exception as e:
            logger.error('Initialization of Module %s failed: %s', mcls, e)
            return

        if m.module_instance is None:
            # Module did not want to be loaded or threw an exception.
            # Module instance will remain without a bound ModuleBase instance.
            return

        self.add_module_properties(m.module_instance)
        self.add_module_contextproperties(m.module_instance)

    def remove_module_instance(self, m: Module):
        # Remove Module and its settings
        if m.module_instance and m.module_instance.properties:
            path = m.module_instance.properties.path
            settings.remove(path)

        inst = m.module_instance  # keep instance over unload()
        m.unload()
        self.remove_module_properties(inst)

    def add_module_contextproperties(self, obj):
        cprops = obj.qml_context_properties()
        if not cprops:
            return

        root_context = self.qmlengine.rootContext()

        for key, obj in cprops.items():  # type: str, Any
            root_context.setContextProperty(key, obj)

    def add_module_properties(self, m: ModuleBase):
        if m.properties is None:
            return

        rp = self._root_properties
        classname = m.modulename()
        instancename = m.instancename()

        if m.allow_maininstance and not m.allow_instances:
            # Only maininstance expected
            rp[classname] = Property(DataType.PROPERTYDICT, initial_value=m.properties, desc=str(m.description))

        elif m.allow_instances and not m.allow_maininstance:
            # Only instances expected
            instances_property = rp.get(classname)

            if instances_property is None:
                # Prepare new PropertyDict for first instance
                instances_property = rp[classname] = Property(DataType.PROPERTYDICT, desc='Instances of ' + classname)

            instances_property[instancename] = Property(DataType.PROPERTYDICT,
                                                        initial_value=m.properties, desc=str(m.description))

        else:
            # maininstance and instances expected. Conflicting. ToDo.
            pass

    def remove_module_properties(self, m: ModuleBase):
        if m.properties is None:
            return

        rp = self._root_properties
        classname = m.modulename()
        instancename = m.instancename()

        if m.allow_maininstance and not m.allow_instances:
            # Only maininstance expected
            del rp[classname]

        elif m.allow_instances and not m.allow_maininstance:
            # Only instances expected
            instances_property = rp[classname]
            del instances_property[instancename]
            if len(instances_property) == 0:
                # Remove root of class
                del rp[classname]

        else:
            # maininstance and instances expected. Conflicting. ToDo.
            pass

    @classmethod
    def shutdown(cls):
        print("shutdown")
        logcall(Module.unload_modules)
        logcall(properties_stop)

    def unload(self):
        del self.mainapp
        del self.qmlengine
        del self._root_properties
        del self.all_modules_classes
        del self.all_modules_classes_by_str

    @QtProperty('QVariantMap', notify=categories_changed)
    def categories_dict(self) -> Dict[str, List[str]]:
        """
        Active categories which resolve into list of module instance paths
        """
        return ModuleInstancePropertyDict.catlist_by_cat

    @QtProperty('QVariantMap', notify=categories_changed)
    def categories_list(self) -> List[str]:
        """
        Plain list of all active categories
        """
        return [cat[0] for cat in ModuleInstancePropertyDict.active_categories]

    @QtProperty('QVariantMap', notify=modules_changed)
    def loaded_instances(self) -> dict:
        """
        modules.loaded_instances['Info']['Weather'][swipeView.instancename]
        reference to "inputdict"

        self._instances[category][classname][instancename] = tempclass(instancename, self.inputs, self.settings)
        """
        return self._instances

    @QtProperty('QVariantMap', notify=modules_changed)
    def modules(self):
        """
        modules.modules['Logic']['Thermostat'][0]
        dict[category]/dict[classname]/list[instancenames]
        """
        return self._modules

    @Slot(str, str, str)
    def add_instance(self, classname, instancename):
        self.add_module_instance(classname, instancename or None)
        self.modules_changed.emit()

    @Slot(str, str, str)
    def remove_instance(self, classname, instancename):
        instancesdict = Module.instancesdict_by_cls[classname]
        instance = instancesdict[instancename or None]
        self.remove_module_instance(instance)
        self.modulesChanged.emit()

    @Slot(str, result='QVariantList')
    def instances(self, classname) -> List[str]:
        instancesdict = Module.instancesdict_by_cls[classname]
        return [instancename or '' for instancename in instancesdict]

    @Slot(result='QVariantList')
    def all_instances(self) -> list:
        listed = list()

        for category in self._instances:
            for classname in self._instances[category]:
                for instance in self._instances[category][classname]:
                    listed.append(f'{category}/{classname}/{instance}')

        return listed
