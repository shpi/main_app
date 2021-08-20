# -*- coding: utf-8 -*-

import sys
from logging import getLogger
from typing import Optional, Dict, Any, Union, Type, Iterable, List, Set

from PySide2.QtCore import Property as QtProperty, Signal, Slot

from core.Settings import settings, new_settings_instance
from core.Constants import internal_modules, external_modules, always_instantiate_modules
from core.Module import Module, ThreadModule
from core.Logger import LogCall

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase, ThreadModuleBase
from interfaces.PropertySystem import Property, PropertyDict, PropertyAccess, ModuleInstancePropertyDict, \
    ModuleMainProperty, properties_start, properties_stop


from helper.PropertyExport import propertydict_to_html


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


def trace_module_dependencies(module: Type[ModuleBase], all_available_modules: Set[Type[ModuleBase]], _level=0) -> Optional[Set[Type[ModuleBase]]]:
    if _level > 10:
        logger.error('Too many recursive dependency checks for Module %s', str(module))
        return None

    result: Set[Type[ModuleBase]] = set()

    for dep in module.depends_on:
        if dep not in all_available_modules:
            logger.error('Unknown dependency %s for Module %s', str(dep), str(module))
            return None

        # This dependency is well known. Check its dependencies
        deplist = trace_module_dependencies(dep, all_available_modules, _level+1)
        if deplist is None:
            # At least one dependency failed. Break recursion.
            return None

        # Add this modules dependency and their dependencies.
        result.update(set(module.depends_on))
        result.update(deplist)

    # Finished and success
    return result


def extend_dependencies(minimal_modules_set: Set[Type[ModuleBase]], all_available_modules: Set[Type[ModuleBase]]):
    for dep_module in minimal_modules_set.copy():
        extra_deps = trace_module_dependencies(dep_module, all_available_modules)
        if extra_deps is None:
            # Fail
            logger.error('This Module has missing dependencies and will be skipped: %s', str(dep_module))
            minimal_modules_set.remove(dep_module)
        else:
            # Success. Add extra dependencies if they are detected and not yet in to-load list.
            minimal_modules_set.update(extra_deps)


def get_loadorder(to_load: Set[Type[ModuleBase]]) -> List[Type[ModuleBase]]:
    remaining = to_load.copy()
    ordered: List[Type[ModuleBase]] = []

    while remaining:  # At least one element to process
        # Fetch satisfied module classes based on current load order state which are ready to load
        next_candidates = set(remainder for remainder in remaining if set(remainder.depends_on).issubset(ordered))

        if not next_candidates:
            # No more modules to process
            break

        # Append next_candidated to load order
        ordered.extend(next_candidates)

        # Remove processed modules from queue
        remaining -= next_candidates

    if remaining:
        # At least one module cannot be loaded because of missing, conflicting or circular dependencies.
        logger.error('These Moduls can\'t be loaded because of missing, conflicting or circular dependencies: %s', str(remaining))

    return ordered


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
    slides_changed = Signal()

    _root_properties = PropertyDict.root(allowcreate=True)

    @classmethod
    def selfload(cls, mainapp):
        if cls._main_instance is not None:
            raise ValueError('"Modules" module is already selfloaded.')

        if cls._root_properties is not PropertyDict.root():
            raise RuntimeError('Root property has already been created before.')

        logcall(properties_start, parent=mainapp)

        # Initialize root propertydict
        cls._root_properties.load()

        # Instantiate my main instance
        m = cls._main_instance = Module(cls, parent=mainapp)

        # Load this module
        m.loaded = True
        m.load(force_reload=True)  # Module.load() is called which calls our load()

    def __init__(self, parent, instancename: str = None):
        if self._main_instance is not None:
            raise ValueError('"Modules" module has already been instantiated.')

        ModuleBase.__init__(self, parent=parent, instancename=instancename)

        self.all_modules_classes = internal_modules() | external_modules()
        self.all_modules_classes.add(self.__class__)  # Append us lately to avoid circular imports
        self.all_modules_classes_by_str = map_classes(self.all_modules_classes)
        self.module_categories = map_class_categories(self.all_modules_classes)

        self.mainapp = parent

        self.property_access = PropertyAccess(parent, self._root_properties)

        # Add contextproperties from mainapp
        self.add_module_contextproperties(parent)

        # Fast and simple callback
        ModuleInstancePropertyDict.changed_callback = self.categories_changed_emit

    def categories_changed_emit(self):
        self.categories_changed.emit()

    def qml_context_properties(self) -> Optional[Dict[str, Any]]:
        return {
            'modules': self,
            'properties': self.property_access,
        }

    def load(self):
        # Add this instance manually
        self.add_module_properties(self)
        self.add_module_contextproperties(self)

        # Find modules to be loaded.

        # Modules referenced in settings
        config_modules_set: Set[Type[ModuleBase]] = set()
        for config_module_str in settings.childGroups():  # type: str
            mcls = self.all_modules_classes_by_str.get(config_module_str)
            if mcls is None:
                logger.warning('Unknown Module class referenced in settings: "%s". Skipping.', config_module_str)
            else:
                config_modules_set.add(mcls)

        # Combine referenced and static modules
        to_load: Set[Type[ModuleBase]] = config_modules_set | set(always_instantiate_modules)

        logger.info("Modules to load: %s", str([m.__name__ for m in to_load]))

        # Add dependencies recursively which are not in the to_load set yet.
        extend_dependencies(to_load, self.all_modules_classes)

        logger.info("Modules to load with dependencies: %s", str([m.__name__ for m in to_load]))

        # Oder Module classes by their dependencies.
        to_load_ordered = get_loadorder(to_load)
        logger.info("Modules to load, ordered: %s", str([m.__name__ for m in to_load_ordered]))

        # Instantiate all Modules in correct order
        for mcls in to_load_ordered:
            if mcls is self.__class__:
                # We're already instantiated.
                continue

            classname = mcls.__name__

            if mcls.allow_maininstance and not mcls.allow_instances:
                # Only a main instance expected
                if settings.bool(f'{classname}/__load', True):
                    self.add_module_instance(mcls)

            elif mcls.allow_instances and not mcls.allow_maininstance:
                # Iterate over instances
                instance_settings = new_settings_instance(classname)
                for instancename in instance_settings.childGroups():
                    if instance_settings.bool(f'{instancename}/__load', True):
                        self.add_module_instance(mcls, instancename)
            else:
                logger.error('For now, only one attribute (allow_maininstance or allow_instances)'
                             ' may set to True: %s', str(mcls))

        # Properties should be all created now

        Property.listmodel.reload()

        # Start modules
        Module.load_modules()

        Property.create_links()

        Property.start_worker()

        if 'PROP_EXPORT' in sys.argv:
            logger.info('Done loading modules. Writing properties_export.html once.')
            propertydict_to_html(self._root_properties)

    def add_module_instance(self, class_or_class_str: Union[Type[ModuleBase], str], instancename: str = None):
        logger.debug('Adding module instance %s:%s', class_or_class_str, instancename)
        if type(class_or_class_str) is str:
            mcls = self.all_modules_classes_by_str.get(class_or_class_str)
        elif issubclass(class_or_class_str, ModuleBase):
            mcls = class_or_class_str
        else:
            logger.error('Could not find module class or invalid class type: %s', class_or_class_str)
            return

        try:
            m = None
            if issubclass(mcls, ThreadModuleBase):
                m = ThreadModule(mcls, instancename=instancename, parent=self.mainapp)
            elif issubclass(mcls, ModuleBase):
                m = Module(mcls, instancename=instancename, parent=self.mainapp)
            else:
                logger.error('Unsupported class to be used as Module: %s', repr(mcls))
        except Exception as e:
            logger.error('Initialization of Module %s failed: %s', mcls, e)
            return

        if not m or m.module_instance is None:
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
        engine = self.mainapp and self.mainapp.engine or False
        if not engine:
            return

        cprops = obj.qml_context_properties()
        if not cprops:
            return

        root_context = engine.rootContext()

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
            rp[classname] = ModuleMainProperty(m)

        elif m.allow_instances and not m.allow_maininstance:
            # Only instances expected
            instances_property = rp.get(classname)

            if instances_property is None:
                # Prepare new PropertyDict for first instance
                instances_property = rp[classname] = Property(DataType.PROPERTYDICT, desc='Instances of ' + classname)

            instances_property[instancename] = ModuleMainProperty(m)

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
        print("### Modules.shutdown")
        logcall(Module.unload_modules)
        logcall(properties_stop)
        del cls._root_properties

    def unload(self):
        del self.mainapp
        del self.all_modules_classes
        del self.all_modules_classes_by_str
        del self.module_categories

    @QtProperty('QVariantMap', notify=categories_changed)
    def categories_dict(self) -> Dict[str, List[str]]:
        """
        Active categories which resolve into list of module instance paths
        """
        return ModuleInstancePropertyDict.catlist_by_cat

    @QtProperty('QVariantList', notify=categories_changed)
    def categories_list(self) -> List[str]:
        """
        Plain list of all active categories
        """
        return [cat[0] for cat in ModuleInstancePropertyDict.active_categories]

    @QtProperty('QVariantList', notify=slides_changed)
    def slides(self) -> List[str]:
        """
        Modules that are registered as own slides
        """
        return ['Module 1', 'Module 2']  # todo: slides

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
