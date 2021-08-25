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

    - IntervalProperty
        Contains a float value which represents the intervall to call a function.

    - TimeoutProperty
        Contains a float which represents a timeout that can be started by restart() and stopped with stop()
        On timeout, the function is being called once unless restarted again.


Properties considered as Module "outputs"
"Output" means, the Module itself modifies its property values.
    - Property
        May set new values from a threaded loop.
        May set new values by events emitted by other inputs or outputs

    - ROProperty
        Set the value on init or write the value once when the constant information is available.
"""

import datetime
import weakref
from functools import partial
from logging import getLogger
from typing import Optional, Union, Any, Callable, Iterable, Dict, ValuesView, ItemsView, KeysView, Generator, List, \
    Tuple, Iterator, Set
from time import time, sleep
from threading import RLock, Thread, Lock
from re import compile
from contextlib import suppress
from enum import EnumMeta, Enum
from weakref import WeakValueDictionary

from PySide2.QtCore import Property as QtProperty, Signal, QObject, Slot, QAbstractListModel, Qt, QModelIndex, \
    QSortFilterProxyModel

from interfaces.DataTypes import DataType, datatype_to_basic_type, datatype_tohuman_func
from interfaces.Module import ModuleBase
from core.Events import EventManager
from core.EventTable import EventTable
from core.Settings import settings
from core.Logger import LogCall
from core.Toolbox import AutoEnum, StandardListModel, LockReleaseTrigger


logger = getLogger(__name__)
logcall = LogCall(logger)

NotLoaded = object()
_valid_key = compile(r'[a-zA-Z0-9_.]+')
_invalid_chars = compile(r'[^a-zA-Z0-9_.]')


class PropertyEvent:
    """
    Dummy class which just provides a verbose repr value.
    Instances are singleton tokens and are checked by identity directly.
    """
    __slots__ = '_name',

    def __init__(self, name_for_repr: str):
        self._name = name_for_repr

    def __repr__(self):
        return self._name


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
    def parentdict(self) -> Optional["PropertyDict"]:
        prop = self.parentproperty
        return prop and prop.parentdict

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

    def update(self, **new_properties: "Property"):
        existing_keys = set(self.keys())
        new_keys = set(new_properties.keys())

        conflict = new_keys & existing_keys
        if conflict:
            raise KeyError('Could not update() the PropertyDict. These keys do already exist: %s', ', '.join(conflict))

        for key, prop in new_properties.items():
            self[key] = prop

    @property
    def transaction(self) -> "LockReleaseTrigger":
        return Property.listmodel.transaction

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
        # if type(key) is int:
        #     key = str(key)
        #
        # elif type(key) is not str:
        #     raise TypeError("Key must be a string.")
        #

        try:
            return self._data[key]
        except KeyError:
            pass

        if self.path_sep in key:
            # Dig deeper in tree structure.
            keys = key.split(self.path_sep, maxsplit=1)

            if keys[0]:
                # Below this PropertyDict
                return self[keys[0]][keys[1]]

            # Relative to root
            return self.root()[keys[1]]

        raise KeyError(key)

    def __setitem__(self, key: str, item: Union["PropertyDict", "Property"]):
        """
        Add Property to collection.
        Key has to be unique in this list.

        :param key: String, no dots and spaces allowed.
        :param item: Property, PropertyDict which are not bound yet or any other object or value.
        """

        if type(key) is not str:
            raise TypeError('Key must be a string.')

        if not _valid_key.fullmatch(key):
            raise TypeError('Invalid chars in key. Allowed characters for keys: A-Z, a-z, 0-9, "_": ' + key)

        if key in self._data:
            raise TypeError('Key already present in PropertyDict.')

        if isinstance(item, PropertyDict):
            # Wrap PropertyDict in Property
            item = PropertyDictProperty(item, 'Nested PropertyDict (automatically wrapped)')

        if not isinstance(item, Property):
            # Not allowed. Wrap object in new simple Property
            raise ValueError('Items in PropertyDict must be Property or PropertyDict.')

        if item.parentdict is not None:
            raise TypeError('Property already assigned to another PropertyDict')

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
            logcall(item.load, errmsg='Exception on calling Property.load(): %s')

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

        delitem: Property = self._data[key]

        logcall(delitem.unload, errmsg='Exception on unloading Property: %s')
        del self._data[key]

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
            return f'<{self.__class__.__name__} ROOT ({len(self._data)} elements{loaded_status})>'

        if isinstance(self.parentproperty, Property):
            return f'<{self.__class__.__name__} {self.parentproperty.key} ({len(self._data)} elements{loaded_status})>'

        return f'<{self.__class__.__name__} ORPHAN ({len(self._data)} elements{loaded_status})>'

    def load(self):
        if self._loaded:
            return

        for prop in self._data.values():
            if isinstance(prop, Property):
                logcall(prop.load,
                        errmsg=f'Exception in PropertyDict {self.__class__!s}.load()->{prop!r}.load(): %s',
                        stack_trace=True)
        self._loaded = True

    def unload(self):
        if self._data:
            for prop in self._data.values():
                if isinstance(prop, Property):
                    logcall(prop.unload, errmsg='Exception on unloading Property: %s')

            self._data.clear()
        self._data = None

        pp = self.parentproperty
        if isinstance(pp, Property):
            pp._value = None  # remove me there
        self._parentproperty_ref = None
        self._loaded = False


class PType(Enum):
    Input = 1
    # ToDo: Input sync rw funcs
    Output = 2
    Function = 3  # Like output
    PropertyDict = 4


# Speedup enum access and use
Input = PType.Input
Output = PType.Output
Function = PType.Function


def _prop_module_path(prop: "Property") -> str:
    if not prop.owner:
        return ''
    instancename = prop.owner.instancename()
    return prop.owner.modulename() + ('/' + instancename if instancename else '')


def _prop_uirelevant(prop: "Property") -> bool:
    if not isinstance(prop.parentdict, ModuleInstancePropertyDict):
        return True

    return prop.key not in ModuleInstancePropertyDict.reserved


def _prop_direction(prop: "Property") -> str:
    if prop.ptype is Output or prop.ptype is Function:
        return 'OUT'

    if prop.ptype is Input:
        return 'IN'

    return ''


def _value_len(prop: "Property"):
    if isinstance(prop.cached_value, ModuleInstancePropertyDict):
        # Do not count hidden elements
        return len(prop.cached_value) - len(ModuleInstancePropertyDict.reserved)
    else:
        return len(prop.cached_value)


_icon_from_ptype = {
    PType.PropertyDict: '📁',
    PType.Input: '↘',
    PType.Output: '↗',
    PType.Function: '⌛',
}


def _prop_icon(prop: "Property") -> str:
    if prop is None:
        return ''
    return _icon_from_ptype.get(prop.ptype, '')


def _set_floatprec(prop: "Property", newvalue: int) -> bool:
    try:
        prop.floatprec = newvalue
        return True
    except Exception as e:
        logger.error('Could not set float precision: %s', repr(e))
        return False


def _set_interval(prop: "Property", newvalue: Optional[int]) -> bool:
    try:
        prop.poll_interval = newvalue
        return True
    except Exception as e:
        logger.error('Could not set interval: %s', repr(e))
        return False


def _set_value(prop: "Property", newvalue) -> bool:
    try:
        prop.value = newvalue
        return True
    except Exception as e:
        logger.error('Could not set value: %s', repr(e))
        return False


class PropertiesListModel(StandardListModel):
    auto = AutoEnum(1000)
    RawProperty = auto()  # 1256 ...
    IDRole = auto()  # Temporary numeric id for faster and easier access.
    IORole = auto()  # Input or Output
    PTypeRole = auto()
    PathRole = auto()
    KeyRole = auto()
    ValueRole = auto()  # Value which may be fetched first
    ValueHumanRole = auto()  # Human readable string output
    CachedRole = auto()  # Value from cache (fast)
    CachedHumanRole = auto()  # Human readable string output
    DefaultRole = auto()
    DefaultHumanRole = auto()
    DescriptionRole = auto()
    DataTypeRole = auto()
    PersistentRole = auto()
    ModuleName = auto()
    ModulePath = auto()
    UIRelevant = auto()
    IsLinked = auto()
    FloatPrec = auto()
    IsFunction = auto()
    Interval = auto()
    IntervalMin = auto()
    IntervalDef = auto()
    IsPropertyDict = auto()
    ValueLen = auto()
    UnicodeIcon = auto()
    # LinkedProperty = auto()

    rolenames = {
        RawProperty: b'raw_property',
        IDRole: b'id',
        IORole: b'io',
        PTypeRole: b'ptype',
        PathRole: b'path',
        KeyRole: b'key',
        ValueRole: b'value',
        ValueHumanRole: b'value_human',
        CachedRole: b'cache',
        CachedHumanRole: b'cache_human',
        DefaultRole: b'default',
        DefaultHumanRole: b'default_human',
        DescriptionRole: b'description',
        DataTypeRole: b'datatype',
        PersistentRole: b'persistent',
        ModuleName: b'modulename',
        ModulePath: b'modulepath',
        UIRelevant: b'uirelevant',
        IsLinked: b'is_linked',
        FloatPrec: b'floatprec',
        IsFunction: b'is_function',
        Interval: b'interval',
        IntervalMin: b'interval_min',
        IntervalDef: b'interval_def',
        IsPropertyDict: b'is_propertydict',
        ValueLen: b'value_len',
        UnicodeIcon: b'icon',
    }

    dataroles_read_funcs = {
        RawProperty: lambda prop: prop,
        IDRole: lambda prop: prop.id,
        IORole: _prop_direction,
        PTypeRole: lambda prop: prop.ptype.name,
        KeyRole: lambda prop: prop.key,
        PathRole: lambda prop: prop.path,
        ValueRole: lambda prop: str(prop.value),
        CachedRole: lambda prop: str(prop.cached_value),
        ValueHumanRole: lambda prop: prop.as_human(prop.value),
        CachedHumanRole: lambda prop: prop.as_human(prop.cached_value),
        DefaultRole: lambda prop: prop.default_value,
        DefaultHumanRole: lambda prop: prop.as_human(prop.default_value),
        DescriptionRole: lambda prop: prop.desc,
        DataTypeRole: lambda prop: prop.datatype and prop.datatype.name,
        PersistentRole: lambda prop: prop.is_persistent,
        ModuleName: lambda prop: prop.owner and prop.owner.modulename(),
        ModulePath: _prop_module_path,
        UIRelevant: _prop_uirelevant,
        IsLinked: lambda prop: prop.is_linked,
        FloatPrec: lambda prop: prop.floatprec,
        IsFunction: lambda prop: prop.ptype is Function,
        Interval: lambda prop: prop.poll_interval,
        IntervalMin: lambda prop: prop.poll_interval_min,
        IntervalDef: lambda prop: prop.poll_interval_def,
        IsPropertyDict: lambda prop: prop.datatype is DataType.PROPERTYDICT,
        ValueLen: _value_len,
        UnicodeIcon: _prop_icon,
    }

    dataroles_write_funcs = {
        ValueRole: _set_value,
        FloatPrec: _set_floatprec,
        Interval: _set_interval,
    }

    item_flags = \
        Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren

    INSERT = object()
    REMOVE = object()

    def __init__(self, parent: QObject):
        StandardListModel.__init__(self, parent=parent, data=None)
        self._lock_counter = LockReleaseTrigger(self.transaction_exit)
        self._lock = Lock()
        self._insert_candidates: List[Any] = []
        self._indices_to_remove: List[int] = []

    @property
    def transaction(self) -> LockReleaseTrigger:
        """
        Supresses emits on at least one active transaction.
        """
        return self._lock_counter

    def transaction_exit(self, operations: Set[Any]):
        full_reload_needed = False

        with self._lock:
            if self.REMOVE in operations and self._indices_to_remove:
                sorted_indices = sorted(self._indices_to_remove)
                count = len(sorted_indices)
                if sorted_indices[0] == sorted_indices[-1] + count - 1:
                    # Linear slice remove
                    try:
                        self.beginRemoveRows(self._invalid_index, sorted_indices[0], sorted_indices[-1])
                        del self._data[sorted_indices[0]:sorted_indices[-1]+1]
                        self._indices_to_remove.clear()
                    finally:
                        self.endRemoveRows()

                else:
                    # Multiple delete positions not in a straight row.
                    full_reload_needed = True
                    for index in reversed(sorted_indices):
                        del self._data[index]

            if self.INSERT in operations and self._insert_candidates:
                if full_reload_needed:
                    # Just extend and trigger reload later
                    self._data.extend(self._insert_candidates)
                else:
                    # Simple linear insert of multiple items
                    current_size = len(self._data)
                    try:
                        self.beginInsertRows(self._invalid_index,
                                             current_size,
                                             current_size + len(self._insert_candidates) - 1)
                        self._data.extend(self._insert_candidates)
                    finally:
                        self.endInsertRows()
                self._insert_candidates.clear()

            if full_reload_needed:
                self.reload()

    def _item_from_index(self, index: QModelIndex) -> Optional["Property"]:
        # Override to strip weakref
        wref = StandardListModel._item_from_index(self, index)

        if wref is None:
            return None

        prop = wref()
        if prop is None:
            logger.warning('Found dead weakref to missing property.')

        return prop

    def data_changed(self, prop: "Property", roles=(ValueRole, CachedRole, ValueHumanRole, CachedHumanRole)):
        """
        Called from internal property operations to annouce changes to the model
        """
        wref = weakref.ref(prop)

        StandardListModel.data_changed(self, wref, roles)

    def add_to_model(self, prop: "Property"):
        if prop is None:
            logger.warning('Tried to add None instad of Property to this model.')
            return

        with self._lock:
            wref = weakref.ref(prop)

            if wref in self._data:
                logger.warning('Property is already in this model: %s', repr(prop))
                return

            if self._lock_counter.active:
                self._lock_counter.trigger_action(self.INSERT)
                self._insert_candidates.append(wref)
                return

            new_pos = len(self._data)

            self.beginInsertRows(self._invalid_index, new_pos, new_pos)
            self._data.append(wref)
            self.endInsertRows()

    def remove_from_model(self, prop: "Property"):
        if prop is None:
            logger.warning('Tried to remove None instad of Property from this model.')
            return

        with self._lock:
            wref = weakref.ref(prop)

            if wref not in self._data:
                logger.warning('Property is not in this model. Cannot remove: %s', repr(prop))
                return

            remove_pos = self._data.index(wref)
            if self._lock_counter.active:
                self._lock_counter.trigger_action(self.REMOVE)
                self._indices_to_remove.append(remove_pos)
                return

            try:
                remove_index = self.index(remove_pos)
            except RuntimeError:
                # App shutdown
                return

            del self._data[remove_pos]
            self.dataChanged.emit(remove_index, remove_index, [])

    def unload(self):
        StandardListModel.unload(self)
        self._lock_counter.unload()


class PropertiesByDataTypeModel(QSortFilterProxyModel):
    def __init__(self, for_datatype: DataType, sourcemodel: PropertiesListModel):
        self._datatype = for_datatype
        QSortFilterProxyModel.__init__(self, sourcemodel)
        self.setSourceModel(sourcemodel)
        self.setFilterRole(PropertiesListModel.DataTypeRole)
        self.setFilterFixedString(for_datatype.name)


class PropertiesByUIRelevant(QSortFilterProxyModel):
    def __init__(self, sourcemodel: PropertiesListModel):
        QSortFilterProxyModel.__init__(self, sourcemodel)
        self.setSourceModel(sourcemodel)
        self.setFilterRole(PropertiesListModel.UIRelevant)
        self.setFilterFixedString('true')
        self.setSortRole(PropertiesListModel.PathRole)


class PropertyNavigateModel(QSortFilterProxyModel):
    def __init__(self, sourcemodel: PropertiesListModel):
        QSortFilterProxyModel.__init__(self, sourcemodel)
        self.setSourceModel(sourcemodel)
        self._source_model = sourcemodel
        self.setSortRole(PropertiesListModel.PathRole)
        self.sort(0, Qt.AscendingOrder)
        self._match_parentpd: Optional[PropertyDict] = None  # PD to show items from
        self._match_self: Optional[Property] = None

    path_changed = Signal()

    @Slot('QVariant')
    def set_path(self, prop: Optional["Property"]):
        self._match_self = prop
        self._match_parentpd = prop and prop.cached_value or PropertyDict.root()
        self.path_changed.emit()  # ToDo: Racing condition problem
        self.invalidateFilter()

    @Slot()
    def go_up(self):
        self.set_path(self._match_self and self._match_self.parentproperty)

    def get_path(self):
        p = (self._match_self and self._match_self.path) or ''
        return p

    path = QtProperty(str, get_path, notify=path_changed)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self._source_model.index(source_row, 0, source_parent)

        prop: Property = index.data(PropertiesListModel.RawProperty)
        if not prop:
            return False

        return prop.parentdict is self._match_parentpd or prop is self._match_self


class PropertyLink:
    __slots__ = '_source', '_destinations'

    def __init__(self, src_prop: "Property"):
        if src_prop.ptype not in {Output, Function}:
            raise ValueError(f'Source Property type must be Output or Function: {src_prop!r}')

        if src_prop.is_linked:
            raise ValueError(f'Source Property is already linked: {src_prop!r}')

        self._source = src_prop
        self._destinations: List[Property] = []
        src_prop._link = self
        src_prop.updated_link()

    def propagate(self):
        v = self._source.cached_value
        for d_input in self._destinations:
            d_input._set_value(v)

    @property
    def source(self) -> "Property":
        return self._source

    # def destinations(self) -> List["Property"]:
    #     return self._destinations
    #

    def link_destination(self, dest_prop: "Property"):
        if dest_prop.ptype is not Input:
            raise ValueError(f'Destination Property type must be Input: {dest_prop!r}')

        if dest_prop in self._destinations or dest_prop._link is self:
            # Already linked? Ok.
            return

        if dest_prop.is_linked:
            # Destination already linked. Removing old link.
            dest_prop._link.unlink_destination(dest_prop)

        # Append to destination list
        self._destinations.append(dest_prop)

        # Link destination to this Link
        dest_prop._link = self
        dest_prop.updated_link()

    def unlink_destination(self, dest_prop: "Property"):
        if dest_prop not in self._destinations:
            raise ValueError(f'Property is not part of current destinations: {dest_prop!r}')

        self._destinations.remove(dest_prop)
        dest_prop._link = None
        dest_prop.updated_link()

        if not self._destinations:
            # Last destination was removed
            self.unlink_source()

    def unlink_source(self):
        for dest_prop in self._destinations:
            dest_prop._link = None
            dest_prop.updated_link()
        self._destinations.clear()

        self._source._link = None
        self._source.updated_link()
        self.unload()

    def unload(self):
        del self._source
        del self._destinations


class PropLog:  # ToDo: PropLog
    def __init__(self, prop: "Property"):
        self._prop = weakref.ref(prop)

    def unload(self):
        pass

    def debug(self, msg: str, *args):
        pass

    def info(self, msg: str, *args):
        pass

    def warning(self, msg: str, *args):
        pass

    def error(self, msg: str, *args, stack_trace=False):
        pass

    def log(self, level: int, msg: str, *args, stack_trace=False):
        pass


def _null_setter(_):
    pass


def _null_getter():
    return None


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
                '_owner', '__weakref__', '_link', '_ptype', '_setfunc', '_getfunc', '_log', '_poll_interval', \
                '_poll_interval_min_default', '_value_time', '_in_model', '_floatprec', '_floatprec_default', 'as_human'

    _exclude_from_model = frozenset((DataType.UNDEFINED, ))  # DataType.PROPERTYDICT, DataType.ENUM
    _classlock = RLock()  # For incrementing instance counters
    _last_id = 0
    _instances_by_id: Dict[int, "Property"] = WeakValueDictionary()
    _changed_properties: List["Property"] = []
    _changed_properties_save_timeout = 5.

    listmodel: Optional[PropertiesListModel] = None  # Raw model which contains all relevant properties
    uirelevantmodel: Optional[QSortFilterProxyModel] = None  # Raw model which contains all ui relevant properties
    navigatemodel: Optional[PropertyNavigateModel] = None
    _models: Dict[str, QSortFilterProxyModel] = {}  # Filter models defined by string key like "datatype:TIME"

    # For storing meta information beyond the persistent value of the property.
    namespace_sep = ':'

    _link_namespace = 'linked_to'
    _interval_namespace = 'interval'
    _floatprec_namespace = 'float_prec'

    UPDATED = PropertyEvent('UPDATED')
    UPDATED_AND_CHANGED = PropertyEvent('UPDATED_AND_CHANGED')
    _eventids = {UPDATED, UPDATED_AND_CHANGED, PropertyDict.CHANGED}

    _worker_thread_run = False
    _worker_thread: Optional[Thread] = None
    _unresolved: List["Property"] = []
    _poll_service: List["Property"] = []  # ToDo: Deque, circular iterator etc.
    _poll_pointer = 0
    _save_pointer = 0

    _floatprec_class_default = 2  # Digits after decimal sign

    @classmethod
    def init_class(cls, parent: QObject):
        cls.listmodel = PropertiesListModel(parent)
        cls.uirelevantmodel = PropertiesByUIRelevant(cls.listmodel)
        cls.navigatemodel = PropertyNavigateModel(cls.uirelevantmodel)

    @classmethod
    def early_stop(cls):
        cls._worker_thread_run = False

        if cls._worker_thread is None:
            return

        if cls._worker_thread.is_alive():
            try:
                cls._worker_thread.join(2)
            except Exception as e:
                logger.error('Error on stopping/joining worker_thread: %s', repr(e))

        cls._worker_thread = None
        for p in tuple(cls._changed_properties):
            # immediate save
            cls._save_now(p)

    @classmethod
    def quit(cls):
        for m in cls._models.values():
            m.deleteLater()
        cls._models.clear()

        if cls.navigatemodel:
            cls.navigatemodel.deleteLater()
            cls.navigatemodel = None

        if cls.uirelevantmodel:
            cls.uirelevantmodel.deleteLater()
            cls.uirelevantmodel = None

        if cls.listmodel:
            cls.listmodel.unload()
            cls.listmodel = None

    @classmethod
    def _async_worker(cls):
        # Runs as thread
        while cls._worker_thread_run:
            sleep(0.1)

            if cls._poll_service:
                if cls._poll_pointer + 1 > len(cls._poll_service):
                    # End of list reached
                    cls._poll_pointer = 0

                p = cls._poll_service[cls._poll_pointer]
                if p._loaded:
                    try:
                        p._getfunc()
                        if p._poll_interval is None:
                            # That was a one time poll
                            del cls._poll_service[cls._poll_pointer]
                        else:
                            # Process next
                            cls._poll_pointer += 1
                    except Exception as e:
                        logger.error('Exception during calling Function from poll_service on %s: %s', repr(p), repr(e))
                        cls._poll_service.remove(p)

            if cls._changed_properties:
                if cls._save_pointer > len(cls._changed_properties) - 1:
                    # End of list reached
                    cls._save_pointer = 0

                p = cls._changed_properties[cls._save_pointer]
                if p._savetime is None or time() >= p._savetime:
                    # Save
                    cls._save_now(p)
                    del cls._changed_properties[cls._save_pointer]
                else:
                    # Check next
                    cls._save_pointer += 1

    @classmethod
    def _save_now(cls, prop: "Property"):
        with cls._classlock:
            logger.debug('Saving property %s=%s', str(prop.path), str(prop._value))
            prop.save_setting(prop._value, prop._datatype, ensure_path_absolute=False)
            prop._savetime = None

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

    @classmethod
    def start_worker(cls):
        if cls._worker_thread_run:
            raise RuntimeError('Property worker thread already running.')

        cls._worker_thread_run = True
        cls._worker_thread = Thread(target=cls._async_worker, name='Property_worker', daemon=True)
        cls._worker_thread.start()

    @classmethod
    def create_links(cls):
        # Resolve temporary str paths in self._link to PropertyLink object
        root = PropertyDict.root()
        for inp_prop in cls._unresolved:
            if not isinstance(inp_prop._link, str):
                continue

            out_prop = root.get(inp_prop._link)
            if out_prop is None:
                # Delete broken link
                logger.warning('Linked Property to get value from does not exist. Removing link to: %s', inp_prop._link)
                inp_prop.delete_setting(cls._link_namespace, ensure_path_absolute=False)
                inp_prop._link = None
                continue

            # Create/update link
            out_prop._link_to(inp_prop)

        cls._unresolved.clear()

    def __init__(
            self,
            ptype: PType,
            datatype: DataType,
            initial_value: Any = None,
            valuepool: Optional[Dict[Any, str]] = None,
            desc: str = None,
            persistent=True,
            function_poll_min_def: Optional[Tuple[int, Optional[int]]] = None
    ):
        """
        Creates a simple Property instance.

        :param ptype: General direction of this Property in context of the module
                Input: Other Properties or UI may set the value of this Property
                Output: Only the Module sets the value of this Property
        :param datatype: DataType specification for this property
        :param initial_value: Initial value for Property. If persistent=True, this value represents the default value.
        :param valuepool: Optional iterable or dictionary containing values for this Property.
                If a dictionary is chosen, the dictkey represents the value, the dictvalue represents
                the visible text for the value.
        :param desc: Description of Property
        """
        self._lock = RLock()
        self._loaded = False
        self._ptype = ptype
        self._key: Optional[str] = None  # Cache attribute
        self._path: Optional[str] = None  # Cache attribute
        self.desc = desc
        self._parentdict_ref: Optional[Any] = None
        self._valuepool = valuepool
        self._savetime: Optional[float] = None
        self._owner: Optional[ModuleBase] = None
        self._event_manager: Optional[EventManager] = EventManager(self, self._eventids) if self._eventids else None
        self._link: Union[str, PropertyLink, None] = None
        self._log = PropLog(self)  # Log interface
        self._value_time = 0.
        self._poll_interval = None
        self._poll_interval_min_default = None
        self._in_model = False  # until actually appended
        self._datatype = datatype
        self._native_datatype = datatype_to_basic_type(datatype)
        self._default_value = None
        self._floatprec_default = self._floatprec_class_default
        self._floatprec: Optional[float] = None
        self.as_human = str

        if function_poll_min_def is not None and ptype is not Function:
            raise TypeError('function_poll_min_def is only available for Function Properties.')

        if datatype is DataType.PROPERTYDICT or isinstance(initial_value, PropertyDict) or ptype is PType.PropertyDict:
            # This Property contains a subordinal PropertyDict.
            self._is_persistent = False  # Force
            self._datatype = DataType.PROPERTYDICT  # Force
            self._ptype = PType.PropertyDict  # Force

            if initial_value is None:
                initial_value = PropertyDict()

            if not isinstance(initial_value, PropertyDict):
                raise PropertyException('If providing datatype as PROPERTYDICT you also have to provide '
                                        'a new instance of PropertyDict.')

            if initial_value.parentproperty is not None:
                raise ValueError("PropertyDict already contained by other Property.")

            self._value = initial_value  # Collect PropertyDict
            self._getfunc = self._from_cache
            self._setfunc = self._set_pd_err
            initial_value._parentproperty_ref = weakref.ref(self)

        elif self._ptype is Function:
            self._is_persistent = False
            self._value = None
            self._getfunc = partial(self._from_func, initial_value)
            self._setfunc = self._set_func_err
            self.as_human = datatype_tohuman_func.get(self._datatype, str)

            if not isinstance(function_poll_min_def, tuple) or \
                    len(function_poll_min_def) != 2 or \
                    not isinstance(function_poll_min_def[0], int) or \
                    not (function_poll_min_def[1] is None or isinstance(function_poll_min_def[1], int)):
                raise ValueError('function_poll_min_def is required for Function Properties and must contain a tuple of'
                                 ' ints: (pollinterval_min [int], pollinterval_default [int or None]).')

            # intify integers
            self._poll_interval_min_default = \
                tuple(int(interval) if interval is not None else None for interval in function_poll_min_def)

        else:
            # Any other value
            if self._ptype not in {Input, Output}:
                raise TypeError('Properties must have their PType explicitly set to Input, Output or Function.')

            self._default_value: Any = initial_value
            self._is_persistent = persistent
            self._value: Any = NotLoaded if persistent else initial_value

            if self._datatype is DataType.ENUM:
                if not isinstance(type(initial_value), EnumMeta):
                    raise ValueError('DataType.ENUM requires initial_value to be a member of an enum.')

                if valuepool is None:
                    # Create valuepool from Enum
                    enum = type(initial_value)
                    self._valuepool = {e: e.name for e in enum}

            self._getfunc = self._from_cache
            if self._ptype is Input:
                self._setfunc = self._set_value
            if self._ptype is Output:
                self._setfunc = self._set_output_err
            self.as_human = datatype_tohuman_func.get(self._datatype, str)

        with Property._classlock:
            # Unique numeric ID for fast access and easier identification
            self._id = Property._last_id = Property._last_id + 1

            # weakref collect all instances
            Property._instances_by_id[self._id] = self

    def load(self):
        if self._loaded:
            return
        self.ensure_path_absolute()  # Should be now!

        self._loaded = True

        # Load static value
        self.load_value(ensure_path_absolute=False)

        # Read the selected path or None
        self._link = None
        if self._ptype is Input:
            # Inputs can be linked to other outputs.
            # Fetch the path and resolve when all Properties are created.
            self._link = self.load_setting(None, DataType.STRING, self._link_namespace, ensure_path_absolute=False)
            if self._link:
                self._unresolved.append(self)  # Remember for later resolving
            # else:
            # Outputs are always set by the module explicitly.
            # They can be linked to other inputs

        if self._ptype is Function:
            # Read poll interval
            self.poll_interval = self.load_setting(self._poll_interval_min_default[1],
                                                   DataType.FLOAT,
                                                   namespace=self._interval_namespace,
                                                   ensure_path_absolute=False)

        if self._native_datatype is float and self._floatprec is None:
            self._floatprec = self.load_setting(self._floatprec_default,
                                                DataType.INTEGER,
                                                namespace=self._floatprec_namespace,
                                                ensure_path_absolute=False)

        # Create/update model
        if self._datatype not in self._exclude_from_model:
            self.listmodel.add_to_model(self)
            self._in_model = True

    def load_value(self, ensure_path_absolute=True):
        if ensure_path_absolute:
            self.ensure_path_absolute()

        if isinstance(self._value, PropertyDict):
            self._value.load()
            return

        if self._is_persistent and self._ptype in {Input, Output}:
            # Persistency on input and output only
            self._set_value(self.load_setting(self._default_value, self.datatype, ensure_path_absolute=False))

    @property
    def floatprec(self) -> Optional[int]:
        return self._floatprec

    @floatprec.setter
    def floatprec(self, newvalue: int):
        if self._native_datatype is not float:
            raise TypeError('floatprec is only available for float based datytypes.')

        self._floatprec = newvalue

        if newvalue == self._floatprec_default:
            # Remove setting
            self.delete_setting(self._floatprec_namespace, ensure_path_absolute=False)
        else:
            self.save_setting(newvalue, DataType.INTEGER, self._floatprec_namespace, ensure_path_absolute=False)

    @property
    def poll_interval_min(self) -> Optional[float]:
        if self._ptype is not Function:
            return None
        return self._poll_interval_min_default[0]

    @property
    def poll_interval_def(self) -> Optional[float]:
        if self._ptype is not Function:
            return None
        return self._poll_interval_min_default[1]

    @property
    def poll_interval(self) -> Optional[float]:
        return self._poll_interval

    @poll_interval.setter
    def poll_interval(self, new_interval: Optional[float]):
        if self._ptype is not Function:
            raise TypeError('poll_interval is only relevant to Property Functions.')

        if new_interval is None or new_interval <= 0.:
            # Disable interval
            self._poll_interval = None

            # But schedule for one time read at least
            if self not in self._poll_service:
                self._poll_service.append(self)

        else:
            # Enable interval
            self._poll_interval = float(new_interval)

        if self._poll_interval and self._poll_interval < self._poll_interval_min_default[0]:
            raise ValueError('Minimum poll intervall is: ' + str(self._poll_interval_min_default[0]))

        if self._poll_interval == self._poll_interval_min_default[1]:
            # If default, don't pollute settings
            self.delete_setting(self._interval_namespace, ensure_path_absolute=False)

        else:
            # Save varying interval
            self.save_setting(self._poll_interval, DataType.FLOAT, self._interval_namespace, ensure_path_absolute=False)

        if self._poll_interval:
            # Enabled
            if self not in self._poll_service:
                self._poll_service.append(self)
        else:
            # Disabled
            if self in self._poll_service:
                self._poll_service.remove(self)

    def updated_link(self):
        if self.is_linked:
            if self._ptype is Input:
                # Update my current value from linked source property
                self._setfunc(self._link.source.value)

            elif self._ptype in {Output, Function}:
                # Update my current value to linked input properties
                self._link.propagate()

        if self._in_model:
            # ToDo: Link source/destination
            if self._ptype is Input:
                self.listmodel.data_changed(self, (PropertiesListModel.IsLinked, ))
            elif self._ptype in {Output, Function}:
                self.listmodel.data_changed(self, (PropertiesListModel.IsLinked, ))

    def link_with(self, other_prop: "Property"):
        """
        Create a new persistent link from an Output Property to an Input Property
        """
        if self._ptype is PType.PropertyDict or other_prop._ptype is PType.PropertyDict:
            raise ValueError('Can\'t link PropertyDicts.')

        if self._ptype is Input:
            # We're an Input
            if other_prop._ptype not in {Output, Function}:
                raise ValueError('other_prop must be of type Output or Function.')

            source = self
            dest = other_prop
        else:
            # We're an Output/Function
            if other_prop._ptype is not Input:
                raise ValueError('other_prop must be of type Input.')

            source = other_prop
            dest = self

        # Create/update link object
        source._link_to(dest)

        # Save link permanent
        dest.save_setting(source.path, DataType.STRING, self._link_namespace, ensure_path_absolute=False)

    def unlink(self):
        if self._ptype is not Input:
            raise TypeError('Only Input Properties can be unlinked from a source.')

        if not self.is_linked:
            # Already unlinked
            return

        self._link.unlink_destination(self)

    @property
    def is_linked(self) -> bool:
        return isinstance(self._link, PropertyLink)

    def _link_to(self, dest: "Property"):
        if not self.is_linked:
            # First link on output. Create object.
            self._link = PropertyLink(self)

        # Append another link
        self._link.link_destination(dest)

    def set_owner(self, new_owner: ModuleBase):
        if self._owner is not None:
            raise RuntimeError('Owner has already been set before and is not changeable.')

        self._owner = new_owner
        if self._datatype is DataType.PROPERTYDICT and isinstance(self._value, PropertyDict):
            # Set recursively
            for subprop in self._value.values():  # type: Property
                subprop.set_owner(new_owner)

    @property
    def log(self) -> PropLog:
        return self._log

    @property
    def ptype(self) -> PType:
        return self._ptype

    @property
    def parentdict(self) -> Optional["PropertyDict"]:
        return self._parentdict_ref and self._parentdict_ref()

    @property
    def parentproperty(self) -> Optional["Property"]:
        pd = self.parentdict
        return pd and pd.parentproperty

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

    def save_setting(self, value, datatype: DataType, namespace: str = None, ensure_path_absolute=True):
        # Default implementation for saving values.
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

    def load_setting(self, default, datatype: DataType, namespace: str = None, ensure_path_absolute=True):
        # Default implementation for loading values.
        if ensure_path_absolute:
            self.ensure_path_absolute()
        path = self.path

        if namespace is not None:
            path = f"{path}{self.namespace_sep}{namespace}"

        if datatype is DataType.ENUM:
            if type(type(default)) is not EnumMeta:
                raise TypeError('Enum settings require an enum member as default.')

            # Convert str to enum member
            value_str = settings.str(self.path, default.name)
            enum = type(default)
            try:
                return enum[value_str]
            except KeyError:
                logger.warning('Found unknown enum member in settings. Reverting to default for %r.', self)
                return default

        return settings.get(path, default, datatype)

    def delete_setting(self, namespace: str = None, ensure_path_absolute=True):
        # Default implementation for saving values.
        if ensure_path_absolute:
            self.ensure_path_absolute()
        path = self.path

        if namespace is not None:
            path = f"{path}{self.namespace_sep}{namespace}"

        settings.remove(path)

    def value_to_default(self):
        self.value = self._default_value

    @property
    def default_value(self) -> Any:
        return self._default_value

    @property
    def is_persistent(self) -> bool:
        return self._is_persistent

    def get_setvalue_func(self) -> Callable[[Any], None]:
        if self._ptype is not Output:
            raise ValueError('get_setvalue_func is only available for Output Properties: ' + repr(self))

        return self._set_value

    def _from_cache(self):
        # Adapter function to read from cache
        return self._value

    def _set_pd_err(self, _):
        # Exception adapter
        raise ValueError('Setting a new value on a Property containing a PropertyDict not allowed: ' + repr(self))

    def _set_func_err(self, _):
        # Exception adapter
        raise ValueError('Setting a new value on a Function Property is not allowed: ' + repr(self))

    def _set_output_err(self, _):
        # Exception adapter
        raise ValueError('Setting values to Output Properties is only ollowed by get_setvalue_func: ' + repr(self))

    def _set_value(self, newvalue):
        # Standard write to cache adapter

        if not self._loaded:
            return

        with self._lock:
            if self._native_datatype is int and type(newvalue) is float:
                # Wrong datatype. Round float to int correctly.
                newvalue = round(newvalue)

            if self._native_datatype is float and newvalue is not None:
                if type(newvalue) is int:
                    newvalue = float(newvalue)

                if isinstance(self._floatprec, int):
                    newvalue = round(newvalue, self._floatprec)

            if self._datatype is DataType.ENUM and type(newvalue) is str:
                # Convert string (from qml) back to enum.
                enum = type(self._default_value)
                newvalue = enum[newvalue]

            # Also check if value has really changed.
            changed = self._value != newvalue

            # Set new value
            self._value = newvalue

            # If linked, tell destinations too
            if self._ptype in {Output, Function} and self.is_linked:
                self._link.propagate()

            if self._event_manager:
                self._event_manager.emit(self.UPDATED)

                if changed:
                    self._event_manager.emit(self.UPDATED_AND_CHANGED)
                    if self._in_model:
                        self.listmodel.data_changed(self)

            if self._is_persistent:
                if not self.path_is_absolute:
                    logger.error('Could not save new value of Property because path is not yet defined: %r', self)
                    return

                # Schedule save
                self._savetime = time() + self._changed_properties_save_timeout
                self._changed_properties.append(self)

    def _from_func(self, func):
        t = time()
        if self._poll_interval:
            # Active polling. Check value_time.
            if t < self._value_time + self._poll_interval:
                # Value still valid. Get from cache.
                return self._value

        self._value_time = t
        res = logcall(func, errmsg='Could not execute assigned function of property: %s')
        if not isinstance(res, BaseException):
            # Cache the value
            Property._set_value(self, res)
        return self._value

    @property
    def cached_value(self) -> Any:
        return self._value

    @property
    def value(self) -> Any:
        v = logcall(self._getfunc, errmsg='Error on getting value from _getfunc() of Property: %s')
        if isinstance(v, BaseException):
            # Use cached value
            return self._value

        return v

    @value.setter
    def value(self, newvalue: Any):
        if not self._loaded:
            # May be called by a different thread a little bit later after unload() has been called.
            return

        if self._ptype is Input and self.is_linked:
            # Remove the link because explicit value was set.
            self._link.unlink_destination(self)
            self.delete_setting(self._link_namespace, ensure_path_absolute=False)

        logcall(self._setfunc, newvalue, errmsg='Error on setting value by _setfunc() of Property: %s')

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

    def __repr__(self):
        ret = f"<{self.__class__.__name__} {self._ptype.name} KEY='{self.key}', ID={self._id}, " \
              f"DType={self._datatype}, DEF={self._default_value}, DESC='{self.desc}'"

        if self.parentdict is not None:
            ret += f', PARENT={self.parentdict!r}'

        if self._is_persistent:
            ret += ', PERSISTENT'

        return ret + ('>' if self._loaded else ' NOT_LOADED>')

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

    def unload(self):
        if self._event_manager:
            self._event_manager.unload()
            self._event_manager = None

        if not self._loaded:
            return

        self._loaded = False

        # if self._is_persistent:
        #    logcall(self._save_now, self)

        # Dummy functions to avoid exceptions.
        self._getfunc = _null_getter
        self._setfunc = _null_setter

        if self.is_linked and self._ptype in {Output, Function}:
            self._link.unload()
            self._link = None

        if isinstance(self._value, PropertyDict):
            logcall(self._value.unload, errmsg="Exception during unloading nested PropertyDict: %s", stack_trace=True)

        if self._in_model and self.listmodel:
            # Remove from model
            self.listmodel.remove_from_model(self)
            self._in_model = False

        if self in self._poll_service:
            self._poll_service.remove(self)

        self._value = None
        del self._valuepool

        if self._lock:
            self._lock = None

        if self._id in self._instances_by_id:
            del self._instances_by_id[self._id]
        else:
            logger.warning('My id was not found in _instances_by_id for removal.')

    def __del__(self):
        if hasattr(self, '_loaded') and self._loaded:
            self.unload()


class PropertyDictProperty(Property):
    """
    Helper function to create subordinary PropertyDicts and avoid common argument values on init
    """
    def __init__(self, pd: PropertyDict = None, desc='Contains a PropertyDict'):
        Property.__init__(self, ptype=PType.PropertyDict, datatype=DataType.PROPERTYDICT, initial_value=pd, desc=desc)


class ModuleMainProperty(PropertyDictProperty):
    """
    This specialized Property hold the PropertyDict of a module instance.
    """
    def __init__(self, module_instance: ModuleBase):
        pd = module_instance.properties

        if not isinstance(pd, PropertyDict):
            raise TypeError('ModuleBase.properties instance mustat least be of type PropertyDict.')

        if not isinstance(pd, ModuleInstancePropertyDict):
            logger.warning('ModuleBase.properties instance should at least be of type ModuleInstancePropertyDict.')

        PropertyDictProperty.__init__(self, pd, desc=str(module_instance.description))

        # classname = module_instance.modulename()
        # instancename = module_instance.instancename()
        # self._owner = classname + ('/' + instancename if instancename else '')
        self.set_owner(module_instance)


class ROProperty(Property):
    """
    Output Property
    This type of Property holds a static value.
    Mutable object's contents can still be changed.
    """
    __slots__ = "_locked",

    DEFINED = PropertyEvent('DEFINED')
    _eventids = Property._eventids | {DEFINED}

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
        Property.__init__(
            self,
            Output,
            datatype=datatype,
            initial_value=value,
            valuepool=valuepool,
            desc=desc,
            persistent=False,
        )
        self._locked = locknow

        if locknow:
            # Always read the cache
            self._getfunc = self._from_cache

            # Further sets are not allowed.
            self._setfunc = self._value_already_set_err
        else:
            # Error until first set
            self._getfunc = self._no_value_no_get_err

            # Once time setter function
            self._setfunc = self._set_ro_value

    @property
    def is_defined(self) -> bool:
        return self._locked

    def _no_value_no_get_err(self):
        raise ValueError(f'Read only value has not been set yet: {self!r}')

    def _value_already_set_err(self):
        raise ValueError("Read only value has already been set before.")

    def _set_ro_value(self, newvalue):
        if self._locked:
            self._value_already_set_err()

        self._locked = True
        self._set_value(newvalue)
        self._getfunc = self._from_cache
        self._setfunc = self._value_already_set_err
        if self.events:
            self.events.emit(self.DEFINED)

    def __repr__(self):
        ret = super().__repr__()[:-1]

        if self._locked:
            ret += f", value='{self._value!s}'"
        else:
            ret += ", value=unset"

        return ret + ">"


class IntervalProperty(Property):
    """
    Input Property
    Executes a function periodically
    Value contains the interval which can be changed.
    Setting value to 0 or 0. creates a one shot (async call by other thread).
    """
    __slots__ = '_func', '_event'

    _event_table = EventTable('IntervalProperty')

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
            Input,
            datatype=DataType.TIMEDELTA,
            initial_value=default_interval,
            desc=desc,
            persistent=persistent_interval,
        )

        self._func = callback_func
        self._event = self._event_table.create_event(func=self._exec)

    def _exec(self, on_time: datetime.datetime):  # on_time is the planned time!
        # Call the function
        logcall(self._func)

        v = self.value

        if not v:  # Inactive: None, 0, 0.
            return

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

    def _set_value(self, newvalue):
        Property._set_value(self, newvalue)

        # Update scheduler on value changes
        if newvalue is None:
            # print("interval.value=None", self._event)
            self._event.deactivate()
        else:
            # 0 or 0. create an oneshot.
            # print("interval.value = not None:", newvalue, self._event)
            now = datetime.datetime.now()
            self._event.reschedule(now, newvalue)


class TimeoutProperty(IntervalProperty):
    """
    Input Property
    Executes the function after restart() is being called.
    Value contains the timeout which can be restarted or stopped.
    Setting value to 0 or 0. creates a one shot (async call by other thread).
    """
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

    def _set_value(self, newvalue):
        Property._set_value(self, newvalue)
        # No automatic restart unless already running.

        if self._event.on_time:
            # Is running. So let's restart with the new timout value.
            self.restart()

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
    def timeout_active(self) -> bool:
        return self._event.on_time is not None


class StringListProperty(Property):
    """
    Input or Output
    List of strings with special methods and events
    """
    ADDED = PropertyEvent('ADDED')
    REMOVED = PropertyEvent('REMOVED')
    _eventids = Property._eventids | {ADDED, REMOVED}

    def __init__(
            self,
            ptype: PType,
            initial_value: Iterable[str] = None,
            unique=False,
            desc: str = None,
            persistent=True,
    ):

        if ptype not in {Input, Output}:
            raise ValueError('StringListProperty only allowed ptype of Input or Output.')

        self.unique = unique

        if initial_value is None:
            initial_value = []

        if unique:
            initial_value = list(set(initial_value))
        else:
            initial_value = list(initial_value)

        Property.__init__(self,
                          ptype,
                          datatype=DataType.LIST_OF_STRINGS,
                          initial_value=initial_value,
                          desc=desc,
                          persistent=persistent,
                          )

        self._getfunc = self._get_as_tuple

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

    def _get_as_tuple(self):
        return tuple(self._value)

    def _set_value(self, newvalue):
        if not isinstance(newvalue, Iterable):
            raise ValueError('StringListProperty\'s value must be iterable of strings')

        old = self._value
        if not isinstance(old, list):
            old = ()

        if self.unique:
            newvalue = set(newvalue)

        Property._set_value(self, list(newvalue))

        if not self._event_manager:
            return

        # ToDo: merge changes
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

    reserved = {'__load', '__in_categories'}  # Will not be relevant to ui

    def __init__(self, **kwargs):
        PropertyDict.__init__(self, **kwargs)
        self._load_module = self['__load'] = \
            Property(Input, DataType.BOOLEAN, True, desc="Load/enable this module instance")
        self._in_categories = self['__in_categories'] = \
            StringListProperty(Input, initial_value=['All'], unique=True, desc='List of assigned categories')

        self._in_categories.events.subscribe(self._added, StringListProperty.ADDED)
        self._in_categories.events.subscribe(self._removed, StringListProperty.REMOVED)
        self._in_categories.events.subscribe(self._qt_emit, Property.UPDATED_AND_CHANGED)

    def _qt_emit(self):
        if not self.changed_callback:
            return
        self.changed_callback()

    def _added(self, _, cat: str):
        if cat in self.catlist_by_cat:
            catlist = self.catlist_by_cat[cat]
        else:
            # New category
            catlist = self.catlist_by_cat[cat] = []
            self.active_categories.append((cat, catlist))

        # Add our instance path to the specific category
        catlist.append(self.path)

    def _removed(self, _, cat: str):
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

            del self.active_categories[delindex]

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
        self._notify = notify  # The notify signal has no name until the Module has been instantiated
        self._path = path

        # Collect instances used in classes for proper unload
        self._instances.append(self)

        # ToDo: Property-Changes -> Qt-Notify

    def f_get(self, modinst):
        if not self.connect:
            return None

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

        # Convert Enum to str for Qml
        value = QtPropLink.f_get(self, modinst)
        return value.name

    # Property.setter will convert string to enum.


class QtPropLinkSelect(QtPropLink):
    """
    Mapping for class level Qt-Properties to instance-properties
    Ability to get or set the link of Input Properties
    """
    def f_get(self, modinst):
        if not self.connect:
            return

        prop: Property = modinst.properties[self._path]

        if prop.ptype is not Input:
            logger.error('QtPropLinkSelect can only be linked to Input Properties: %s', repr(prop))
            return ''

        if not prop.is_linked:
            # Not (yet) linked
            return ''

        # Qml uses path only
        return prop._link.source.path

    def f_set(self, modinst, newvalue):
        if not self.connect:
            return

        # Get signal from parent which has the emit function.
        prop: Property = modinst.properties[self._path]

        if prop.ptype is not Input:
            logger.error('QtPropLinkSelect can only be linked to Input Properties: %s', repr(prop))
            return ''

        if not newvalue:
            # Remove link
            prop.unlink()
            return

        source = PropertyDict.root().get(newvalue)
        if source is None:
            logger.error('Cannot find Property to link with: %s', newvalue)
            return

        changed = prop._link is not source._link

        # Add/change link
        source.link_with(prop)

        # Notify change
        if changed:
            notify = getattr(modinst, str(self._notify)[:-2])
            notify.emit()


class PropertyAccess(QObject):
    def __init__(self, parent, root_pd: PropertyDict):
        QObject.__init__(self, parent)
        self._root_pd = root_pd

    @Slot(str, result=QObject)
    def get_properties_by_datatype_model(self, datatype: str):
        dt = DataType.str_to_type(datatype)
        if dt is DataType.UNDEFINED:
            raise ValueError('DataType unknown: ' + repr(datatype))
        return Property.get_datatype_model(dt)

    @Slot(result=QObject)
    def get_property_navigator_model(self):
        Property.navigatemodel.set_path(None)
        return Property.navigatemodel

    @Slot(result=QObject)
    def get_properties_model(self):
        return Property.uirelevantmodel

    def unload(self):
        self._root_pd = None


def properties_start(parent: QObject):
    print("### properties_start")
    logcall(Property.init_class, parent)
    logcall(IntervalProperty.init_class)


def properties_early_stop():
    print("### properties_early_stop")
    logcall(Property.early_stop)
    logcall(IntervalProperty.quit)
    ModuleInstancePropertyDict.changed_callback = None
    QtPropLink.quit()


def properties_stop():
    print("### properties_stop")
    logcall(Property.quit)

    root = PropertyDict.root()
    if root is not None:
        logcall(root.unload, errmsg='Error during unloading all properties: %s')
