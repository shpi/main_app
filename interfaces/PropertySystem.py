# -*- coding: utf-8 -*-

"""
PropertySystem

Defining, storing, sharing, controlling and announcing values defined in Modules by paths.


PropertyDict
    Contains different Properties or subclasses of Property arranged as Dict per module instance and identified
    by a unique string key.

Properties considered as Module "inputs"
"Input" means, Properties should be set from UI to control or setup the Module.
    - Property
        Set a value by a widget in the UI suitable to the DataType of the property.

    - SelectProperty
        Links to another property in the UI from a list of matching DataType.

    - IntervalProperty
        Contains a float value which represents the intervall to call a function.

    - TimeoutProperty
        Contains a float which represents a timeout that can be started by restart() and stopped with stop()
        On timeout, the function is being called once unless restarted again.


Properties considered as Module "outputs"
"Output" means, the Module itself modifies its property values.
    - Property
        May set new values from a threaded loop.
        May set new values by functions called by event manager of any input property.

    - ROProperty
        Set the value on init or write the value once when the constant information is available.

    - FunctionProperty
        Value will be gathered or updated from a function defined in the module if its cached value is outdated.
"""

import datetime
import weakref
from logging import getLogger
from typing import Optional, Union, Any, Callable, Iterable, Dict, ValuesView, ItemsView, KeysView, Generator, Set, \
    Type, List, Tuple, Iterator
from time import time, sleep
from threading import RLock, Thread
from re import compile
from contextlib import suppress
from enum import EnumMeta
from weakref import WeakValueDictionary

from PySide2.QtCore import Property as QtProperty, Signal, QObject, Slot, QAbstractListModel, Qt, QModelIndex, \
    QSortFilterProxyModel

from interfaces.DataTypes import DataType, datatype_to_basic_type
from interfaces.Module import ModuleBase
from core.Events import EventManager
from core.EventTable import EventTable
from core.Settings import settings, new_settings_instance, Settings
from core.Logger import LogCall


logger = getLogger(__name__)
logcall = LogCall(logger)

NotLoaded = object()
_valid_key = compile(r'[a-zA-Z0-9_]+')
_invalid_chars = compile(r'[^a-zA-Z0-9_]')


class PropertyEvent:
    """
    Dummy class which just provides a verbose repr value.
    Instances are singleton tokens and are checked by identity directly.
    """
    __slots__ = '_name',

    def __init__(self, name_for_repr: str):
        self._name = name_for_repr

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._name}>'


class PropertyException(Exception):
    pass


class PropertyDict:
    """
    Holds key, value structured properties.
    Contains inherited classes of Property which wrap any data type or even sub PropertyDicts.

    Properties belonging related to root instance should only be created in modules within define_properties().
    PropertyDicts and Properties should be static, once created. Removing and extending later "should" not happen.

    Each PropertyDict may be represented by a path.
    The first created PropertyDict (root) has path=None.
    Lose PropertyDicts have their path=".".
    PropertyDicts bound in other PropertyDicts get their path fetched from containing Property.path.
    """

    __slots__ = '_parentproperty_ref', '_loaded', '_data', '__weakref__'
    _root_instance: Optional["PropertyDict"] = None

    path_sep = '/'

    CHANGED = PropertyEvent('CHANGED')

    @classmethod
    def root(cls, allowcreate=False) -> Optional["PropertyDict"]:
        """Get root PropertyDict and allow creation if it does not yet exist."""
        if cls._root_instance is None and allowcreate:
            # Create a first instance.
            PropertyDict._root_instance = PropertyDict()

        # Get root instance
        return cls._root_instance

    @classmethod
    def create_keyname(cls, source: str, valid_replacement='') -> str:
        return _invalid_chars.sub(valid_replacement, source)

    def __init__(self, **kwargs):
        """
        Initializes a new PropertyDict object.

        :param desc: Optional description of list. May be visible in raw propertysystem access methods.
        :param kwargs: Initial properties.
        """
        # QObject.__init__(self, parent)
        self._data: Dict[str, Property] = {}
        self._loaded = False

        self._parentproperty_ref: Optional[Any] = None  # Parent property weakref if set

        for key, prop in kwargs.items():
            self[key] = prop

    def __del__(self):
        if self.parentproperty is None:
            # PropertyDict is just not referenced anymore.
            self.unload()

    def __len__(self):
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __contains__(self, key: str):
        return key in self._data

    @property
    def parentproperty(self) -> Optional["Property"]:
        return self._parentproperty_ref and self._parentproperty_ref()

    @property
    def is_root(self) -> bool:
        """Checks for instance is root instance."""
        return self is PropertyDict._root_instance

    @property
    def path(self) -> Optional[str]:
        """
        Returns the path representation of this PropertyDict.
        root PropertyDict returns: None
        Lose PropertyDicts are relative and return path_sep ("/" or ".")
        Others get their path from outer PropertyDict and result in dotted path representations like:
           "mainlist.sublist.propertyname"

        :return: path
        """
        if self.is_root:
            # I am root.
            # My child property's keys will be first part of path.
            return None

        elif isinstance(self.parentproperty, Property):
            # Paths are handled by Properties
            return self.parentproperty.path

        else:
            # Not part of an official path hierarchy.
            return self.path_sep

    def update(self, new_properties: Dict[str, "Property"]):
        existing_keys = set(self.keys())
        new_keys = set(new_properties.keys())

        conflict = new_keys & existing_keys
        if conflict:
            raise KeyError('Could not update() the PropertyDict. These keys do already exist: %s', ', '.join(conflict))

        for key, prop in new_properties.items():
            self[key] = prop

    def get(self, path: str, default: "Property" = None) -> Optional["Property"]:
        with suppress(KeyError):
            return self[path]
        return default

    def __getitem__(self, key: str) -> "Property":
        """
        Gets a Property from PropertyDict instance by key or path.
        Paths may be provided as key. Property will be acquired recursively.

        :param key: Simple key string "myproperty" or a path "sublist.myproperty" relative to this instance.
                    Also allows leading "path_sep" to address the root propertydict: '/InputDev/0000...'
        :return: Found Property or KeyError
        """
        if type(key) is int:
            key = str(key)

        elif type(key) is not str:
            raise TypeError("Key must be a string.")

        if self.path_sep in key:
            # Dig deeper in tree structure.
            keys = key.split(self.path_sep, maxsplit=1)

            if keys[0]:
                # Below this PropertyDict
                return self[keys[0]][keys[1]]

            # Relative to root
            return self.root()[keys[1]]

        return self._data[key]  # Or KeyError

    def __setitem__(self, key: str, item: Union["PropertyDict", "Property"]):
        """
        Add Property to collection.
        Key has to be unique in this list.

        :param key: String, no dots and spaces allowed.
        :param item: Property, PropertyDict which are not bound yet or any other object or value.
        """

        if type(key) is not str:
            raise TypeError("Key must be a string.")

        if not _valid_key.fullmatch(key):
            raise TypeError("Invalid chars in key. Allowed characters for keys: A-Z, a-z, 0-9, '_': '" + key + '"')

        if key in self._data:
            raise TypeError("Key already present in PropertyDict.")

        if isinstance(item, PropertyDict):
            # Wrap PropertyDict in Property
            item = Property(datatype=DataType.PROPERTYDICT, initial_value=item,
                            desc="Nested PropertyDict (automatically wrapped)")

        if not isinstance(item, Property):
            # Not allowed. Wrap object in new simple Property
            raise ValueError("Items in PropertyDict must be Property or PropertyDict.")

        if item.parentdict is not None:
            raise TypeError("Property already assigned to another PropertyDict")

        # Link me as parent
        item._parentdict_ref = weakref.ref(self)

        # Inherit owner from my parentproperty
        owner = self.parentproperty and self.parentproperty.owner
        if owner is not None:
            item.set_owner(owner)

        # Collect new Property
        if key in self._data:
            logger.warning('Replacing existing Property with another. Key=%s, new Property: %s', key, repr(item))

        self._data[key] = item
        item._key = key

        if self._loaded:
            # Late load instantly
            logcall(item.load, errmsg="Exception on calling Property.load(): %s")

        pp = self.parentproperty
        if pp and pp.events:
            pp.events.emit(self.CHANGED)  # ToDo: context manager for event emit

    def __delitem__(self, key: str):
        # Deep deletes allowed (key = relative path)

        if self.path_sep in key:
            # Delegate deeper delete
            pd_path, key = key.rsplit(self.path_sep, 1)
            del self[pd_path][key]
            return

        delitem: Property = self._data.get(key)

        if delitem is None:
            raise KeyError(f"Property '{key}' not found.")

        logcall(delitem.unload, errmsg="Exception on unloading Property: %s")
        self._data.pop(key)

        pp = self.parentproperty
        if pp and pp.events:
            pp.events.emit(self.CHANGED)  # ToDo: context manager for event emit

    def items(self) -> ItemsView[str, "Property"]:
        return self._data.items()

    def keys(self) -> KeysView[str]:
        return self._data.keys()

    def values(self) -> ValuesView["Property"]:
        return self._data.values()

    def paths(self) -> Generator[str, None, None]:
        path = (self.parentproperty.path if isinstance(self.parentproperty, Property) else '') or ''

        for key in self._data.keys():
            yield f'{path}{self.path_sep}{key}'

    def __repr__(self):
        loaded_status = '' if self._loaded else ' not loaded'

        if self.is_root:
            return f"<{self.__class__.__name__} ROOT ({len(self._data)} elements{loaded_status})>"

        if isinstance(self.parentproperty, Property):
            return f"<{self.__class__.__name__} key='{self.parentproperty.key}' ({len(self._data)} elements{loaded_status})>"

        return f"<{self.__class__.__name__} ORPHAN ({len(self._data)} elements{loaded_status})>"

    def load(self):
        if self._loaded:
            return

        for prop in self._data.values():
            if isinstance(prop, Property):
                logcall(prop.load, errmsg=f"Exception in PropertyDict {self.__class__!s}.load()->{prop!r}.load(): %s", stack_trace=True)
        self._loaded = True

    def unload(self):
        if self._data:
            for prop in self._data.values():
                if isinstance(prop, Property):
                    logcall(prop.unload, errmsg="Exception on unloading Property: %s")

            self._data.clear()
        self._data = None

        pp = self.parentproperty
        if isinstance(pp, Property):
            pp._value = None  # remove me there
        self._parentproperty_ref = None
        self._loaded = False


class PersistentPropertyDict(PropertyDict):
    __slots__ = "_child_property_class", "_settings_group",

    def __init__(self, child_property_class: Type["Property"]):
        PropertyDict.__init__(self)
        self._child_property_class = child_property_class
        self._settings_group: Optional[Settings] = None

    def load(self):
        if self._loaded:
            return

        pp = self.parentproperty
        if not (pp and pp.path_is_absolute):
            raise PropertyException('Called load() too early on: {pd!r}'.format(pd=self))

        self._loaded = True

        # Begin group on new QSettings instance
        self._settings_group = new_settings_instance(self.path)

        sections = self._settings_group.childKeys(), self._settings_group.childGroups()
        for section in sections:
            for key in section:
                if self._child_property_class.namespace_sep in key:
                    # Skip namespace attributes
                    continue

                # Create new Property by given children class
                prop = self._child_property_class(key)

                # Collect item by base class
                PropertyDict.__setitem__(self, key, prop)

    def __delitem__(self, key: str):
        # Only deleting direct children allowed.
        delitem: Property = self._data.get(key)

        if delitem is None:
            raise KeyError(f"Property '{key}' not found.")

        deletekey = key if delitem.path_is_absolute else None

        PropertyDict.__delitem__(self, key)

        if deletekey:
            # Remove all related settings
            self._settings_group.remove(deletekey)

    def delete(self, key: str):
        del self[key]

    def __setitem__(self, key, item):
        raise KeyError('Setting an item in PersistentPropertyDict is not supported. Use add() instead.')

    def add(self, key: str):
        if type(key) is not str:
            raise TypeError("Key must be a string.")

        if not _valid_key.fullmatch(key):
            raise TypeError("Invalid chars in key. Allowed characters for keys: A-Z, a-z, 0-9, '_'")

        if key in self._data:
            raise TypeError("Key already present in PersistentPropertyDict.")

        # Create new Property by given children class
        prop = self._child_property_class(key)

        # Collect item by base class
        PropertyDict.__setitem__(self, key, prop)
        # load() should have set a value which also should be saved now.


class PropertiesListModel(QAbstractListModel):
    PathRole = Qt.UserRole + 1000
    IDRole = Qt.UserRole + 1001
    ValueRole = Qt.UserRole + 1002
    DefaultValueRole = Qt.UserRole + 1003
    DescriptionRole = Qt.UserRole + 1004
    DataTypeRole = Qt.UserRole + 1005
    PersistentRole = Qt.UserRole + 1006
    ModuleName = Qt.UserRole + 1007
    ModulePath = Qt.UserRole + 1008

    _rolenames = {
        PathRole: b"path",
        IDRole: b"id",
        ValueRole: b"value",
        DefaultValueRole: b"default",
        DescriptionRole: b"description",
        DataTypeRole: b"datatype",
        PersistentRole: b"persistent",
        ModuleName: b"modulename",
        ModulePath: b"modulepath",
    }

    _invalid_index = QModelIndex()

    def __init__(self, parent: QObject):
        QAbstractListModel.__init__(self, parent=parent)
        self._property_reflist = []

    def unload(self):
        self.beginResetModel()
        self._property_reflist.clear()
        self.endResetModel()

    def index_valid(self, index: QModelIndex) -> bool:
        return 0 <= index.row() < self.rowCount() and index.isValid()

    def check_properties_gone(self):
        """Remove disappeared properties"""
        valids = tuple(propref for propref in self._property_reflist if propref() is not None)
        if len(valids) == len(self._property_reflist):
            # Nothing has changed
            return

        # Replace items
        self.beginResetModel()
        self._property_reflist[:] = valids
        self.endResetModel()

    reload = check_properties_gone

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not self.index_valid(index):
            return None

        row = index.row()
        wref = self._property_reflist[row]
        prop = wref()

        if prop is None:
            return None

        try:
            if role == self.PathRole:
                return prop.path
            elif role == self.ValueRole:
                return prop.value
            elif role == self.DefaultValueRole:
                return prop.default_value
            elif role == self.DescriptionRole:
                return prop.desc
            elif role == self.DataTypeRole:
                return prop.datatype and prop.datatype.name
            elif role == self.PersistentRole:
                return prop.is_persistent
            elif role == self.ModuleClass:
                if not prop.owner:
                    return None
                return prop.owner.modulename()
            elif role == self.ModulePath:
                if not prop.owner:
                    return None
                instancename = prop.owner.instancename()
                return prop.owner.modulename() + ('/' + instancename if instancename else '')
            else:
                return None
        except Exception as e:
            logger.error('Exception on fetching data in SelectPropertyByDataTypeModel: %s', repr(e))

    def data_changed(self, prop: "Property"):
        wref = weakref.ref(prop)

        if wref not in self._property_reflist:
            logger.warning('Property is not in this model. Cannot update: %s', repr(prop))
            return

        changed_pos = self._property_reflist.index(wref)
        index = self.index(changed_pos)
        self.dataChanged.emit(index, index, [])

    def add(self, prop: "Property"):
        if prop is None:
            logger.warning('Tried to add None instad of Property to this model.')
            return

        wref = weakref.ref(prop)

        if wref in self._property_reflist:
            logger.warning('Property is already in this model: %s', repr(prop))
            return

        new_pos = len(self._property_reflist)
        self.beginInsertRows(self._invalid_index, new_pos, new_pos)
        self._property_reflist.append(wref)
        # index = self.index(len(self._property_reflist)-1)
        # self.dataChanged.emit(index, index, [])
        self.endInsertRows()

    def remove(self, prop: "Property"):
        if prop is None:
            logger.warning('Tried to remove None instad of Property from this model.')
            return

        wref = weakref.ref(prop)

        if wref not in self._property_reflist:
            logger.warning('Property is not in this model. Cannot remove: %s', repr(prop))
            return

        remove_pos = self._property_reflist.index(wref)
        try:
            index_start = self.index(remove_pos)
        except RuntimeError:
            # App shutdown
            return

        index_stop = self.index(len(self._property_reflist)-1)

        self._property_reflist.remove(wref)
        self.dataChanged.emit(index_start, index_stop, [])

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        self.check_properties_gone()
        return len(self._property_reflist)

    def roleNames(self):
        return self._rolenames


class PropertiesByDataTypeModel(QSortFilterProxyModel):
    def __init__(self, for_datatype: DataType, sourcemodel: PropertiesListModel):
        self._datatype = for_datatype
        QSortFilterProxyModel.__init__(self, sourcemodel)
        self.setSourceModel(sourcemodel)
        self.setFilterRole(PropertiesListModel.DataTypeRole)
        self.setFilterFixedString(for_datatype.name)


class Property:
    """
    Defines a simple property with an initial value of any type.
    Provides a value-property for read and write access.

    A Property may be parented to a PropertyDict.
    When parented, it is accessable by key in the PropertyDict as key-value-pair.
    Properties may contain another sub PropertyDicts.
    """

    __slots__ = '_value', '_parentdict_ref', '_path', '_id', 'desc', '_lock', '_valuepool', '_event_manager', \
                '_loaded', '_datatype', '_is_persistent', '_default_value',  '_key', '_native_datatype', '_savetime', \
                '_owner', '__weakref__',

    _exclude_from_model = frozenset((DataType.UNDEFINED, DataType.PROPERTYDICT, DataType.ENUM))
    _classlock = RLock()  # For incrementing instance counters
    _last_id = 0
    _instances_by_id: Dict[int, "Property"] = WeakValueDictionary()
    _changed_properties: Set["Property"] = set()
    _changed_properties_save_timeout = 5.

    listmodel: Optional[PropertiesListModel] = None  # Raw model which contains all relevant properties
    _models: Dict[str, QSortFilterProxyModel] = {}  # Filter models defined by string key like "datatype:TIME_STR"

    # For storing meta information beyond the persistent value of the property.
    namespace_sep = ':'

    UPDATED = PropertyEvent('UPDATED')
    UPDATED_AND_CHANGED = PropertyEvent('UPDATED_AND_CHANGED')
    _eventids = {UPDATED, UPDATED_AND_CHANGED, PropertyDict.CHANGED}

    _run_save_thread = False
    _check_unsaved_changes_thread: Optional[Thread] = None

    @classmethod
    def init_class(cls, parent: QObject):
        print("init class called")
        if cls._run_save_thread:
            raise RuntimeError('Save thread already running.')

        cls.listmodel = PropertiesListModel(parent)

        cls._run_save_thread = True
        cls._check_unsaved_changes_thread = Thread(target=cls.check_unsaved, name='Property_thread', daemon=True)
        cls._check_unsaved_changes_thread.start()

    @classmethod
    def quit(cls):
        if cls.listmodel:
            cls.listmodel.unload()
            cls.listmodel = None

        cls._models.clear()

        for p in cls._changed_properties.copy():
            # immediate save
            cls._save_now(p)

        cls._run_save_thread = False

        if cls._check_unsaved_changes_thread is None:
            return

        if cls._check_unsaved_changes_thread.is_alive():
            try:
                cls._check_unsaved_changes_thread.join(2)
            except Exception as e:
                logger.error('Error in Property.quit: %s', e)

        cls._check_unsaved_changes_thread = None

    @classmethod
    def check_unsaved(cls):
        # ToDo: Better solution
        while cls._run_save_thread:
            sleep(1)
            if cls._changed_properties:
                now = time()
                with cls._classlock:
                    for p in tuple(cls._changed_properties):
                        if p._savetime is None or now >= p._savetime:
                            cls._save_now(p)

    @classmethod
    def _save_now(cls, prop: "Property"):
        with cls._classlock:
            if prop in cls._changed_properties:
                logger.debug('Saving property %s=%s', str(prop.path), str(prop._value))
                prop.save_setting(prop._value, prop._datatype, ensure_path_absolute=False)
                prop._savetime = None
                cls._changed_properties.discard(prop)

    @classmethod
    def get_by_id(cls, pr_id: int) -> Optional["Property"]:
        # Speedup accessing by id instead of paths. Usecase in http, mqtt etc.
        return cls._instances_by_id.get(pr_id)

    @classmethod
    def get_model(cls, key: str, exception=True) -> Optional[QAbstractListModel]:
        model = cls._models.get(key)
        if model is None and exception:
            raise KeyError('No model found: ' + key)
        return model

    @classmethod
    def get_datatype_model(cls, for_datatype: DataType, create=True, exception=True) \
            -> Optional[PropertiesByDataTypeModel]:
        key = 'datatype:' + for_datatype.name
        model = cls.get_model(key, exception=False)
        if model is None:
            if create:
                model = cls._models[key] = PropertiesByDataTypeModel(for_datatype, sourcemodel=cls.listmodel)
            elif exception:
                raise KeyError('No model found for datatype: ' + str(for_datatype))
        return model

    def __init__(
            self,
            datatype: DataType,
            initial_value: Any = None,
            valuepool: Optional[Dict[Any, str]] = None,
            desc: str = None,
            persistent=True,
    ):
        """
        Creates a simple Property instance.

        :param datatype: DataType specification for this property
        :param initial_value: Initial value for Property. If persistent=True, this value represents the default value.
        :param valuepool: Optional iterable or dictionary containing values for this Property.
                If a dictionary is chosen, the dictkey represents the value, the dictvalue represents
                the visible text for the value.
        :param desc: Description of Property
        """
        self._lock = RLock()
        self._loaded = False
        self._key: Optional[str] = None  # Cache attribute
        self._path: Optional[str] = None  # Cache attribute
        self.desc: Optional[str] = desc
        self._parentdict_ref: Optional[Any] = None
        self._valuepool = valuepool
        self._savetime: Optional[float] = None
        self._owner: Optional[ModuleBase] = None
        self._event_manager: Optional[EventManager] = EventManager(self, self._eventids) if self._eventids else None

        with Property._classlock:
            # Unique numeric ID for fast access and easier identification
            self._id = Property._last_id = Property._last_id + 1

            # weakref collect all instances
            Property._instances_by_id[self._id] = self

        if datatype is DataType.PROPERTYDICT or isinstance(initial_value, PropertyDict):
            # This Property contains a subordinal PropertyDict.
            self._is_persistent = False  # Force
            self._datatype = DataType.PROPERTYDICT  # Force
            self._native_datatype = None

            if initial_value is None:
                initial_value = PropertyDict()

            self._value = initial_value  # Collect PropertyDict
            self._default_value = None

            if not isinstance(initial_value, PropertyDict):
                raise PropertyException('If providing datatype as PROPERTYDICT you also have to provide '
                                        'a new instance of PropertyDict.')

            if initial_value.parentproperty is not None:
                raise ValueError("PropertyDict already contained by other Property.")
            initial_value._parentproperty_ref = weakref.ref(self)

        else:
            # Any other value
            self._datatype = datatype
            self._native_datatype = datatype_to_basic_type(datatype)
            self._default_value = initial_value
            self._is_persistent = persistent
            self._value: Any = NotLoaded if persistent else initial_value

            if self._datatype is DataType.ENUM:
                if not isinstance(type(initial_value), EnumMeta):
                    raise ValueError('DataType.ENUM requires initial_value to be a member of an enum.')

                if valuepool is None:
                    # Create valuepool from Enum
                    enum = type(initial_value)
                    self._valuepool = {e: e.value for e in enum}

    def __del__(self):
        if hasattr(self, '_loaded') and self._loaded:
            self.unload()

    def set_owner(self, new_owner: ModuleBase):
        if self._owner is not None:
            raise RuntimeError('Owner has already been set before and is not changeable.')

        self._owner = new_owner
        if self._datatype is DataType.PROPERTYDICT and isinstance(self._value, PropertyDict):
            # Set recursively
            for subprop in self._value.values():  # type: Property
                subprop.set_owner(new_owner)

    @property
    def parentdict(self) -> Optional["PropertyDict"]:
        return self._parentdict_ref and self._parentdict_ref()

    @property
    def owner(self) -> Optional[ModuleBase]:
        return self._owner

    @property
    def id(self) -> int:
        """Temporary numeric id of property. May change on next program run. Do not hard rely on that."""
        return self._id

    @property
    def events(self) -> Optional[EventManager]:
        return self._event_manager

    @property
    def valuepool(self) -> Optional[Dict[Any, str]]:
        return self._valuepool

    @property
    def datatype(self) -> DataType:
        return self._datatype

    @property
    def path_is_absolute(self) -> bool:
        path = self.path
        return path is not None and not path.startswith(PropertyDict.path_sep)

    def ensure_path_absolute(self, raise_exc=True) -> bool:
        if self.path_is_absolute:
            return True

        if raise_exc:
            raise ValueError("Can't read persistent settings before path has been defined. "
                             "Function has been called too early.")
        return False

    def load(self):
        if self._loaded:
            return
        self.ensure_path_absolute()  # Should be now!

        self._loaded = True

        # Create/update model
        if self._datatype not in self._exclude_from_model:
            self.listmodel.add(self)

        self.load_value(ensure_path_absolute=False)  # For persistent values or sub property dicts

        # Load other attributes: logging, exposed...

    def load_value(self, ensure_path_absolute=True, setvalue=True):
        if ensure_path_absolute:
            self.ensure_path_absolute()

        if isinstance(self._value, PropertyDict) or self._datatype is DataType.PROPERTYDICT:
            self._value.load()
            return

        if self._is_persistent:
            # Set value from settings
            if self._datatype is DataType.ENUM:
                # Convert str to enum member
                value_str = settings.str(self.path, self._default_value.name)
                enum = type(self._default_value)
                try:
                    self.value = enum[value_str]
                except KeyError:
                    logger.warning('Found unknown enum member in settings. Reverting to default for %r.', self)
                    self.value_to_default()
            else:
                res = settings.get(self.path, self._default_value, self._datatype)
                # logger.warning("assigning %s, %s, %s, %s", self.path, self._default_value, self._datatype, res)
                if setvalue:
                    self.value = res
                return res

    def save_setting(self, value, datatype: DataType, namespace: str = None, ensure_path_absolute=True):
        # Default implementation for loading values.
        if ensure_path_absolute:
            self.ensure_path_absolute()
        path = self.path

        if namespace is not None:
            path = f"{path}{self.namespace_sep}{namespace}"

        if datatype is DataType.ENUM:
            if type(type(value)) is not EnumMeta:
                raise TypeError('Enum settings require an enum member as value.')

            value = value.name

        settings.set(path, value, datatype)

    def value_to_default(self):
        self.value = self._default_value

    @property
    def default_value(self) -> Any:
        return self._default_value

    @property
    def is_persistent(self) -> bool:
        return self._is_persistent

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, newvalue: Any):
        if not self._loaded:
            # May be called by a different thread a little bit later after unload() has been called.
            return

        if self._datatype is DataType.PROPERTYDICT:
            raise ValueError('Setting a new value on a Property containing a PropertyDict not allowed: ' + repr(self))

        with self._lock:
            if self._native_datatype is int and type(newvalue) is float:
                # Wrong datatype. Round float to int correctly.
                newvalue = round(newvalue)

            if self._datatype is DataType.ENUM and type(newvalue) is str:
                # Convert string (from qml) back to enum.
                enum = type(self._default_value)
                newvalue = enum[newvalue]

            # Also check if value has really changed.
            changed = self._value != newvalue

            # Set new value
            self._value = newvalue

            if self._event_manager:
                self._event_manager.emit(self.UPDATED)

                if changed:
                    self._event_manager.emit(self.UPDATED_AND_CHANGED)
                    if self._datatype not in self._exclude_from_model:
                        self.listmodel.data_changed(self)

            if self._is_persistent:
                if not self.path_is_absolute:
                    logger.error('Could not save new value of Property because path is not yet defined: %r', self)
                    return

                # Schedule save
                self._changed_properties.add(self)
                self._savetime = time() + self._changed_properties_save_timeout

    @property
    def key(self) -> Optional[str]:
        """Returns the key as string or None if not set."""
        return self._key

    @property
    def path(self) -> Optional[str]:
        """Returns the path as string or None if not set. Lose paths start with "." """

        if self._path:
            # Use valid cached path
            return self._path

        if not isinstance(self.parentdict, PropertyDict):
            # Must be in PropertyDict to calculate a valid path
            return None

        # Acquire path now.
        parentpath = self.parentdict.path

        if parentpath is None:
            # We're part of root PropertyDict
            # Our key is first part of path and will not change.
            self._path = self.key
            return self._path

        # Append our key to parentpath as full path.
        # parentpath may be lose (".", ".x.y") or absolute ("x.y").

        if parentpath == PropertyDict.path_sep:
            # lose
            newpath = f"{PropertyDict.path_sep}{self.key}"
        else:
            # lose or absolute
            newpath = f"{parentpath}{PropertyDict.path_sep}{self.key}"

        if not newpath.startswith(PropertyDict.path_sep):
            # Will not change. Cache it.
            self._path = newpath

        return newpath

    def unload(self):
        logcall(self._save_now, self)  # If in unsaved list

        if self._event_manager:
            self._event_manager.unload()
            self._event_manager = None

        if not self._loaded:
            return

        if isinstance(self._value, PropertyDict):
            logcall(self._value.unload, errmsg="Exception during unloading nested PropertyDict: %s", stack_trace=True)

        if self._datatype not in self._exclude_from_model:
            # Remove from model
            self.listmodel.remove(self)

        self._value = None
        del self._path
        del self._valuepool

        if self._lock:
            self._lock = None

        if self._id in self._instances_by_id:
            self._instances_by_id.pop(self._id)
        else:
            logger.warning('My id was not found in _instances_by_id for removal.')

        self._loaded = False

    def __repr__(self):
        loaded_status = '' if self._loaded else ' not loaded'

        ret = f"<{self.__class__.__name__} key='{self.key}', id={self._id}, type={self._datatype}, default={self._default_value}, desc='{self.desc}'"

        if self.parentdict is not None:
            ret += f', bound to {self.parentdict!r}'

        if self._is_persistent:
            ret += ', persistent'

        return ret + f'{loaded_status}>'

    def __contains__(self, key: str):
        return key in self.value

    def __getitem__(self, key: str):
        return self.value[key]

    def __delitem__(self, key: str):
        del self.value[key]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __bool__(self):
        # Always true. Not relevant to value for safety.
        # Allows: "if self._pr_myproperty:" shortcut.
        # If not defined, __len__ is being called which may fail.
        return True

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)


class ModuleMainProperty(Property):
    """
    This specialized Property hold the PropertyDict of a module instance.
    """
    def __init__(
            self,
            module_instance: ModuleBase
    ):
        pd = module_instance.properties

        if not isinstance(pd, PropertyDict):
            raise TypeError('ModuleBase.properties instance mustat least be of type PropertyDict.')

        if not isinstance(pd, ModuleInstancePropertyDict):
            logger.warning('ModuleBase.properties instance should at least be of type ModuleInstancePropertyDict.')

        Property.__init__(self,
                          datatype=DataType.PROPERTYDICT,
                          initial_value=pd,
                          desc=str(module_instance.description),
                          persistent=False
                          )

        # classname = module_instance.modulename()
        # instancename = module_instance.instancename()
        # self._owner = classname + ('/' + instancename if instancename else '')
        self.set_owner(module_instance)


class SelectProperty(Property):
    """
    Binds to a specific Property which is interchangeable.
    """
    __slots__ = "_selected_property_ref", "_expected_datatype",

    SELECTED = PropertyEvent('SELECTED')
    _eventids = Property._eventids | {SELECTED}

    def __init__(
            self,
            expected_datatype: Optional[DataType],
            default_path: str = None,
            valuepool: Union[Iterable, Dict[Any, str]] = None,
            desc: str = None,
            persistent=True
    ):
        if not isinstance(expected_datatype, (DataType, type(None))):
            raise TypeError('expected_datatype must be member of DataType enum or None, not:' + repr(expected_datatype))

        # This property practically contains the path to another Property
        super().__init__(datatype=DataType.STRING, initial_value=default_path, valuepool=valuepool, desc=desc,
                         persistent=persistent)

        self._selected_property_ref: Optional[Any] = None
        self._expected_datatype = expected_datatype

    def _updated_and_changed(self, prop):
        # Gets called from selected property
        self.events.emit(self.UPDATED_AND_CHANGED)

    def _updated(self, prop):
        # Gets called from selected property
        self.events.emit(self.UPDATED)

    _event_mapping = {
        Property.UPDATED: _updated,
        Property.UPDATED_AND_CHANGED: _updated_and_changed,
    }

    @property
    def is_selected(self) -> bool:
        return isinstance(self.selected_property, Property)

    @property
    def selected_path(self) -> Optional[str]:
        return super().value

    @selected_path.setter
    def selected_path(self, newpath: Optional[str]):
        selected_prop = PropertyDict.root().get(newpath)

        if newpath and selected_prop is None:
            logger.warning('Path for selection does not exist (anymore): "%s". Selection has been removed.', newpath)

        self.selected_property = selected_prop

    @property
    def expected_datatype(self) -> Optional[DataType]:
        """Returns the DataType which is used to find suitable Properties."""
        return self._expected_datatype

    @property
    def selected_property(self) -> Optional[Property]:
        """Returns the selected Property if set or None."""
        return self._selected_property_ref and self._selected_property_ref()

    @selected_property.setter
    def selected_property(self, new_property: Optional[Property]):
        current_property = self.selected_property
        if current_property is new_property:
            return

        if isinstance(current_property, Property) and current_property.events:
            # Unsubscribe from previously selected property
            for eventid, func in self._event_mapping.items():
                current_property.events.unsubscribe(func, eventid)

        if isinstance(new_property, Property) and new_property.events:
            # Subscribe to events of new property
            for eventid, func in self._event_mapping.items():
                new_property.events.subscribe(func, eventid)

        # Remember new property
        self._selected_property_ref = weakref.ref(new_property) if new_property else None

        # Set path also
        # Call base classes' setter of value.
        Property.value.__set__(self, new_property.path if new_property else None)

        if self.events:
            self.events.emit(self.SELECTED)

    def load_value(self, ensure_path_absolute=True, setvalue=True):
        self.selected_path = super().load_value(ensure_path_absolute, setvalue=False)

    @property
    def value(self):
        # "value" always refers to the selected property's value. Not to self.value which contains the path.

        # Property must be set here
        selected_property = self.selected_property

        if selected_property is None:
            raise ValueError("A Property has not been selected yet. No value available.")

        return selected_property.value

    @value.setter
    def value(self, newvalue):
        # if not self._allowwrite:
        raise PropertyException("Setting new values to selected properties is not allowed. "
                                "They're supposed to be read only.")

    def __repr__(self):
        ret = super().__repr__()[:-1]
        ret += f", selected property='{self.selected_property!r}'"
        return ret + ">"

    def unload(self):
        self._selected_property_ref = None
        super().unload()


class ROProperty(Property):
    """
    This type of Property holds a static value.
    Mutable object's contents can still be changed.
    """
    __slots__ = "_locked",

    DEFINED = PropertyEvent('DEFINED')
    _eventids = {DEFINED}

    def __init__(
            self,
            datatype: DataType,
            value: Any = None,
            locknow=True,
            valuepool: Union[Iterable, Dict[Any, str]] = None,
            desc: str = None
    ):
        """
        Creates a Property with a fixed (read only) value.

        :param value: Initial value
        :param locknow:
        If True value of constructor will be locked immediately
        If False, a value may be written once in value's setter

        :param desc: Description of Property
        """
        self._locked = False
        Property.__init__(
            self,
            datatype=datatype,
            initial_value=value,
            valuepool=valuepool,
            desc=desc,
            persistent=False
        )
        self._locked = locknow

    @property
    def is_defined(self) -> bool:
        return self._locked

    @property
    def value(self):
        if not self._locked:
            raise ValueError(f"Read only value has not been set yet: {self!r}")

        return self._value

    @value.setter
    def value(self, newvalue):
        if self._locked:
            raise ValueError("Read only value has already been set before.")

        # Set value
        Property.value.__set__(self, newvalue)

        # Disallow further value sets
        self._locked = True
        if self.events:
            self.events.emit(self.DEFINED)

    def __repr__(self):
        ret = super().__repr__()[:-1]

        if self._locked:
            ret += f", value='{self._value!s}'"
        else:
            ret += ", value=unset"

        return ret + ">"


class FunctionProperty(Property):
    """
    This type of Property will call a function when it's value is requested.
    Has caching capabilities.
    """
    __slots__ = "func", "maxage", "_time", "args", "kwargs"

    BEFORE_FUNC_CALL = PropertyEvent('BEFORE_FUNC_CALL')
    _eventids = Property._eventids | {BEFORE_FUNC_CALL}

    def __init__(
            self,
            datatype: DataType,
            getterfunc: Callable,
            args: list = None,
            kwargs: dict = None,
            maxage=0.,
            desc: str = None
    ):
        """
        Creates a Property sourcing it's value from a function

        :param datatype: DataType specification for this property
        :param getterfunc: Function to get called on request. Return value is used.
        :param args, kwargs: Static arguments for calls of getterfunc.
        :param maxage: Max age in seconds the cached value is valid before function will be called again.
        :param desc: Description of Property
        """
        if not callable(getterfunc):
            raise TypeError("getterfunc must provide a callable object.")

        Property.__init__(self, datatype=datatype, desc=desc, persistent=False)
        self.func = getterfunc
        self.maxage = maxage
        self._time = 0.

        self.args = list(args) if args else []
        self.kwargs = dict(kwargs) if kwargs else {}

    @property
    def cachevalid(self) -> bool:
        """Is the cached value valid?"""
        return self.age < self.maxage

    @property
    def age(self) -> float:
        """Age of cached value"""
        return time() - self._time

    @property
    def value(self):
        # Value requested

        with self._lock:
            # Call one by one because we're caching and calling functions.

            if self.cachevalid:
                return self._value

            # Cache is outdated

            if self.events:
                self.events.emit(self.BEFORE_FUNC_CALL)

            # Call the function
            newvalue = logcall(
                self.func,
                *self.args,
                errmsg="Exception caught during getting value of FunctionProperty: %s",
                stack_trace=True,
                **self.kwargs
            )

            if not isinstance(newvalue, BaseException):
                # Fetching value successful.

                # Remember time
                self._time = time()

                # Save new value in cache
                Property.value.__set__(self, newvalue)

        # Return new cached value
        return self._value

    @value.setter
    def value(self, newvalue):
        raise ValueError("New values for FunctionProperty cannot be assigned.")

    def __repr__(self):
        ret = Property.__repr__(self)[:-1]

        # Recursion on repr(self.func)!
        func_repr = f'<bound method {self.func.__qualname__}>'

        ret += f", func={func_repr}, maxage={self.maxage}"
        return ret + ">"

    def unload(self):
        del self.func
        del self.kwargs
        del self.args
        super().unload()


class IntervalProperty(Property):
    _event_table = EventTable()

    @classmethod
    def init_class(cls):
        cls._event_table.event_loop_start()

    @classmethod
    def quit(cls):
        cls._event_table.unload()
        del cls._event_table

    def __init__(
            self,
            callback_func: Callable[[], None],
            default_interval=1.,
            desc: str = None,
            persistent_interval=True,
    ):

        Property.__init__(
            self,
            datatype=DataType.TIMEDELTA,
            initial_value=default_interval,
            desc=desc,
            persistent=persistent_interval
        )

        self._func = callback_func
        self._event = self._event_table.create_event(func=self._exec)

    def _exec(self, on_time: datetime.datetime):  # on_time is the planned time!
        # Call the function
        logcall(self._func)

        v = self.value

        if v:  # Still active
            interval = datetime.timedelta(seconds=v)

            # Get time after function finish
            now = datetime.datetime.now()

            # This would be the exact next running time
            next_event = on_time + interval

            if now > next_event:
                # At least one event has been missed.
                # Maybe callback function ran too long.
                # Skip and reschedule from now on.
                next_event = now + interval

            self._event.reschedule(next_event)

    def load(self):
        super().load()

        if not self._is_persistent:
            # Need a manual reschedule because non persistent properties don't trigger the setter.
            v = self.value
            if v:
                now = datetime.datetime.now()
                self._event.reschedule(now, float(v))

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, newvalue: Any):
        newvalue = 0. if newvalue is None else float(newvalue)
        Property.value.__set__(self, newvalue)

        if newvalue == 0.:
            self._event.deactivate()
        else:
            now = datetime.datetime.now()
            self._event.reschedule(now, newvalue)


class TimeoutProperty(IntervalProperty):
    def __init__(
            self,
            timeout_func: Callable[[], None],
            default_timeout=1.,
            desc: str = None,
            persistent_timeout=True,
    ):

        IntervalProperty.__init__(
            self,
            callback_func=timeout_func,
            default_interval=default_timeout,
            desc=desc,
            persistent_interval=persistent_timeout,
        )

    def _exec(self, on_time: datetime.datetime):  # on_time is the planned time!
        # Call the function once
        logcall(self._func)

    def stop(self):
        self._event.deactivate()

    def restart(self):
        now = datetime.datetime.now()
        if self.value is None:
            # Timeout deactivated
            return

        self._event.reschedule(now, self._value)

    @property
    def value(self) -> Optional[float]:
        return self._value

    @value.setter
    def value(self, newvalue: Optional[float]):
        newvalue = None if newvalue is None else float(newvalue)
        Property.value.__set__(self, newvalue)
        if self._event.on_time:
            # Is running
            self.restart()

    @property
    def timeout_active(self) -> bool:
        return self._event.on_time is not None


class StringListProperty(Property):
    ADDED = PropertyEvent('ADDED')
    REMOVED = PropertyEvent('REMOVED')
    _eventids = Property._eventids | {ADDED, REMOVED}

    def __init__(
            self,
            initial_value: Iterable[str] = None,
            unique=False,
            desc: str = None,
            persistent=True,
    ):
        self.unique = unique

        if initial_value is None:
            initial_value = []

        if unique:
            initial_value = list(set(initial_value))
        else:
            initial_value = list(initial_value)

        Property.__init__(self, datatype=DataType.LIST_OF_STRINGS, initial_value=initial_value, desc=desc, persistent=persistent)

    def pop(self, index=-1, emit_update=True) -> str:
        item = self._value.pop(index)  # or IndexError

        if self._event_manager:
            self._event_manager.emit(self.REMOVED, item)
            if emit_update:
                self._event_manager.emit(self.UPDATED)
                self._event_manager.emit(self.UPDATED_AND_CHANGED)

        return item

    def remove(self, item: str, emit_update=True):
        self._value.remove(item)  # or ValueError

        if self._event_manager:
            self._event_manager.emit(self.REMOVED, item)
            if emit_update:
                self._event_manager.emit(self.UPDATED)
                self._event_manager.emit(self.UPDATED_AND_CHANGED)

    def extend(self, new_items: Iterable[str]):
        if self.unique:
            # Discard duplicates
            new_items = set(new_items) - set(self._value)

        for new_item in new_items:
            self.append(new_item, emit_update=False)

        if new_items and self._event_manager:
            self._event_manager.emit(self.UPDATED)
            self._event_manager.emit(self.UPDATED_AND_CHANGED)

    def insert(self, pos: int, new_str: str, emit_update=True):
        if self.unique and new_str in self._value:
            return

        self._value.insert(pos, new_str)

        if self._event_manager:
            self._event_manager.emit(self.ADDED, new_str)

            if emit_update:
                self._event_manager.emit(self.UPDATED)
                self._event_manager.emit(self.UPDATED_AND_CHANGED)

    def append(self, new_str: str, emit_update=True):
        self.insert(len(self._value), new_str, emit_update)

    def clear(self):
        self.value = []

    @property
    def value(self) -> Any:
        """
        A tuple is returned because the internal list should not be modified by a direct list access.
        """
        return tuple(self._value)

    @value.setter
    def value(self, newvalue: Any):
        if not isinstance(newvalue, Iterable):
            raise ValueError('StringListProperty\'s value must be iterable of strings')

        with self._lock:
            old = self._value
            if not isinstance(old, list):
                old = ()

            Property.value.fset(self, list(newvalue))

            # ToDo: merge changes
            if self._event_manager:
                for old_item in old:
                    self._event_manager.emit(self.REMOVED, old_item)

                for new_item in newvalue:
                    self._event_manager.emit(self.ADDED, new_item)

                self._event_manager.emit(self.UPDATED)
                self._event_manager.emit(self.UPDATED_AND_CHANGED)


class ModuleInstancePropertyDict(PropertyDict):
    """
    This subclass of PropertyDict adds some standard properties which are used to store meta settings for a module.
    """

    # These categories always exists even if not module instance is part of it.
    static_categories = "Home", "All"

    active_categories: List[Tuple[str, List[str]]] = [(cat, []) for cat in static_categories]
    catlist_by_cat: Dict[str, List[str]] = {cat: [] for cat in static_categories}  # to find the list in active_categories

    changed_callback = None
    # ToDo: Category order

    def __init__(self, **kwargs):
        PropertyDict.__init__(self, **kwargs)
        self._load_module = self['__load'] = Property(DataType.BOOLEAN, True, desc="Load/enable this module instance")
        self._in_categories = self['__in_categories'] = \
            StringListProperty(unique=True, initial_value=['All'], desc='List of assigned categories')

        self._in_categories.events.subscribe(self._added, StringListProperty.ADDED)
        self._in_categories.events.subscribe(self._removed, StringListProperty.REMOVED)
        self._in_categories.events.subscribe(self._qt_emit, Property.UPDATED_AND_CHANGED)

    def _qt_emit(self):
        if not self.changed_callback:
            return
        self.changed_callback()

    def _added(self, prop, cat: str):
        if cat in self.catlist_by_cat:
            catlist = self.catlist_by_cat[cat]
        else:
            # New category
            catlist = self.catlist_by_cat[cat] = []
            self.active_categories.append((cat, catlist))

        # Add our instance path to the specific category
        catlist.append(self.path)

    def _removed(self, prop, cat: str):
        if cat not in self.catlist_by_cat:
            logger.warning('Removed from a non existing category: %s', cat)
            return

        catlist = self.catlist_by_cat[cat]
        if self.path not in catlist:
            logger.warning('Has already been removed from existing category before: %s', cat)
            return

        catlist.remove(self.path)

        if not catlist and cat not in self.static_categories:
            # Remove empty category which are not static
            del self.catlist_by_cat[cat]
            delindex = None
            for category_index, category in enumerate(self.active_categories):
                if category[0] == cat:
                    delindex = category_index
                    break

            if delindex is None:
                logger.warning('Could not find and delete category from list: %s', cat)
                return

            self.active_categories.pop(delindex)

    def load(self):
        super().load()
        # Save the value to settings to ensure this PropertyDict is in settings too for future loadings.
        self._load_module.save_setting(self._load_module.value, DataType.BOOLEAN, ensure_path_absolute=False)


class QtPropLink(QtProperty):
    """
    Mapping for class level Qt-Properties to instance level properties.
    Result is a Property (QtCore.Property) which can access a Property (interfaces.PropertySystem.Property).
    When choosing and calling QtPropLink (or subclasses) from Qt/qml, the referenced Properties must exist.
    Module instances may have different Properties.
    """
    connect = True
    _instances: List["QtPropLink"] = []

    @classmethod
    def quit(cls):
        # Stop accessing our properties immediately
        cls.connect = False
        for inst in cls._instances:
            inst.unload()

    def __init__(self, datatype, path: str, notify: Signal = None):
        """
        :param datatype: Datatype in Qt format
        :param path: Path to linked Property relative to Module instance's properties
        :param notify: Signal to notify or None for constant properties
        """
        QtProperty.__init__(
            self,
            type=datatype,
            fget=self.f_get,
            fset=self.f_set,
            notify=notify,
            constant=notify is None
        )
        # self._notify = str(notify)[:-2]  # Remember name of signal only
        self._notify = notify
        self._path = path

        # Collect instances used in classes for proper unload
        self._instances.append(self)

        # ToDo: Property-Changes -> Qt-Notify

    def f_get(self, modinst):
        if not self.connect:
            return

        prop: Property = modinst.properties[self._path]

        # Return bare value
        return prop.value

    def f_set(self, modinst, newvalue):
        if not self.connect:
            return

        # Get signal from parent which has the emit function.
        prop: Property = modinst.properties[self._path]
        # ToDo: enum no change emit (enum vs. str)
        changed = prop.value != newvalue
        prop.value = newvalue

        # Notify change
        if changed:
            notify = getattr(modinst, str(self._notify)[:-2])
            notify.emit()

    def unload(self):
        self._notify = None


class QtPropLinkEnum(QtPropLink):
    """
    Mapping for class level Qt-Properties to instance-properties
    Ability to handle Enums by strings
    """

    def f_get(self, modinst):
        if not self.connect:
            return

        prop: Property = modinst.properties[self._path]
        # Convert Enum to str for Qml
        return prop.value.name

    # Property.setter will convert string to enum.


class QtPropLinkSelect(QtPropLink):
    """
    Mapping for class level Qt-Properties to instance-properties
    Ability to get or set the path of an SelectProperty
    """
    def f_get(self, modinst):
        if not self.connect:
            return

        prop: SelectProperty = modinst.properties[self._path]

        # Qml uses path only
        return prop.selected_path

    def f_set(self, modinst, newvalue):
        if not self.connect:
            return

        # Get signal from parent which has the emit function.
        prop: SelectProperty = modinst.properties[self._path]

        # Set new path
        changed = prop.selected_path != newvalue
        prop.selected_path = newvalue

        # Notify change
        if changed:
            notify = getattr(modinst, str(self._notify)[:-2])
            notify.emit()


class PropertyAccess(QObject):
    data_changed = Signal()

    def __init__(self, parent, propertydict: PropertyDict):
        QObject.__init__(self, parent)
        self._pd = propertydict

    @Slot(str, result=QObject)
    def get_properties_by_datatype_model(self, datatype: str):
        dt = DataType.str_to_type(datatype)
        if dt is DataType.UNDEFINED:
            raise ValueError('DataType unknown: ' + repr(datatype))
        return Property.get_datatype_model(dt)

    @QtProperty(QObject, notify=data_changed)
    def get_sortfilter_model(self):
        self.completelist.filter = None
        return self.completelist


def properties_start(parent: QObject):
    print("### properties_start")
    logcall(Property.init_class, parent)
    logcall(IntervalProperty.init_class)


def properties_early_stop():
    print("### properties_early_stop")
    logcall(IntervalProperty.quit)
    ModuleInstancePropertyDict.changed_callback = None
    QtPropLink.quit()


def properties_stop():
    print("### properties_stop")
    logcall(Property.quit)

    root = PropertyDict.root()
    if root is not None:
        logcall(root.unload, errmsg='Error during unloading all properties: %s')
