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
import logging
from typing import Optional, Union, Any, Callable, Iterable, Dict, ValuesView, ItemsView, KeysView, Generator, Set, Type
from time import time
from threading import Lock, RLock
from re import compile
from contextlib import suppress
from enum import EnumMeta

from PySide2.QtCore import Property as QtProperty, Signal

from interfaces.DataTypes import DataType
from core.Events import EventManager
from core.EventTable import EventTable
from core.Settings import settings, new_settings_instance, Settings
from core.Logger import LogCall


logger = logging.getLogger(__name__)
logcall = LogCall(logger)

NotLoaded = object()
_valid_key = compile(r"[a-zA-Z0-9_]+")


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

    __slots__ = "parentproperty", "_loaded", "_data"
    _root_instance: Optional["PropertyDict"] = None

    path_sep = '/'

    CHANGED = object()

    @classmethod
    def root(cls, allowcreate=False) -> Optional["PropertyDict"]:
        """Get root PropertyDict and allow creation if it does not yet exist."""
        if cls._root_instance is None and allowcreate:
            # Create a first instance.
            PropertyDict._root_instance = PropertyDict()

        # Get root instance
        return cls._root_instance

    def __init__(self, **kwargs):
        """
        Initializes a new PropertyDict object.

        :param desc: Optional description of list. May be visible in raw propertysystem access methods.
        :param kwargs: Initial properties.
        """
        # QObject.__init__(self, parent)
        self._data = {}
        self._loaded = False

        self.parentproperty: Optional["Property"] = None  # Parent property if set

        if PropertyDict._root_instance is None:
            # First instance of PropertyDict becomes root
            PropertyDict._root_instance = self

        for key, prop in kwargs.items():
            if not _valid_key.fullmatch(key):
                raise ValueError("Key must only consist out of chars: a-z, A-Z, 0-9, '_'.")
            self[key] = prop

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, key: str):
        return key in self._data

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

    def get(self, path: str, default: "Property" = None) -> Optional["Property"]:
        with suppress(KeyError):
            return self[path]
        return default

    def __getitem__(self, key: str) -> "Property":
        """
        Gets a Property from PropertyDict instance by key or path.
        Paths may be provided as key. Property will be acquired recursively.

        :param key: Simple key string "myproperty" or a path "sublist.myproperty" relative to this instance.
        :return: Found Property or KeyError
        """

        if type(key) is int:
            key = str(key)

        elif type(key) is not str:
            raise TypeError("Key must be a string.")

        if self.path_sep in key:
            # Dig deeper in tree structure.
            keys = key.split(self.path_sep, maxsplit=1)
            return self[keys[0]][keys[1]]

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
            raise TypeError("Invalid chars in key. Allowed characters for keys: A-Z, a-z, 0-9, '_'")

        if key in self._data:
            raise TypeError("Key already present in PropertyDict.")

        if isinstance(item, PropertyDict):
            # Wrap in Property
            item.parentproperty = item = Property(datatype=DataType.PROPERTYDICT, initial_value=item,
                                                  desc="Nested PropertyDict (automatically wrapped)", persistent=False)

        if not isinstance(item, Property):
            # Not allowed. Wrap object in new simple Property
            raise ValueError("Items in PropertyDict must be Property or PropertyDict.")

        if item.parentdict is not None:
            raise TypeError("Property already assigned to another PropertyDict")

        # Link parent
        item.parentdict = self

        # Collect new Property
        self._data[key] = item
        item._key = key

        if self._loaded:
            # Late load instantly
            logcall(item.load, errmsg="Exception on calling Property.load(): %s")

        if self.parentproperty:
            self.parentproperty.events.emit(self.CHANGED)  # ToDo: context manager for event emit

    def __delitem__(self, key: str):
        # Deep deletes allowed (key = relative path)

        if self.path_sep in key:
            # Delegate deep delete
            pd_path, key = key.rsplit(self.path_sep, 1)
            del self[pd_path][key]
            return

        delitem: Property = self._data.get(key)

        if delitem is None:
            raise KeyError(f"Property '{key}' not found.")

        logcall(delitem.unload, errmsg="Exception on unloading Property: %s")
        self._data.pop(key)

        if self.parentproperty and self.parentproperty.events:
            self.parentproperty.events.emit(self.CHANGED)  # ToDo: context manager for event emit

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
        if self.is_root:
            return f"<{self.__class__.__name__} ROOT ({len(self._data)} elements)>"

        if isinstance(self.parentproperty, Property):
            return f"<{self.__class__.__name__} key='{self.parentproperty.key}' ({len(self._data)} elements)>"

        return f"{self.__class__.__name__} ORPHAN ({len(self._data)} elements)"

    def load(self):
        if self._loaded:
            return

        for prop in self._data.values():
            if not isinstance(prop, Property):
                continue
            logcall(prop.load, errmsg=f"Exception on {self.__class__!s}.load():Property.load() [{prop!r}]: %s")
        self._loaded = True

    def unload(self):
        for prop in self._data.values():
            if isinstance(prop, Property):
                logcall(prop.unload, errmsg="Exception on unloading Property: %s")

        self._data.clear()
        del self._data

        if isinstance(self.parentproperty, Property):
            self.parentproperty.value = None  # remove me there
        self.parentproperty = None


class PersistentPropertyDict(PropertyDict):
    __slots__ = "_child_property_class", "_settings_group",

    def __init__(self, child_property_class: Type["Property"]):
        PropertyDict.__init__(self)
        self._child_property_class = child_property_class
        self._settings_group: Optional[Settings] = None

    def load(self):
        if self._loaded:
            return

        if not (self.parentproperty and self.parentproperty.path_is_absolute):
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


class Property:  # QObject
    """
    Defines a simple property with an initial value of any type.
    Provides a value-property for read and write access.

    A Property may be parented to a PropertyDict.
    When parented, it is accessable by key in the PropertyDict as key-value-pair.
    Properties may contain another sub PropertyDicts.
    """

    __slots__ = "_value", "parentdict", "_path", "_id", "desc", "_lock", "_valuepool", "_event_manager", \
                "_datatype", "_is_persistent", "_default_value", "_loaded", "_key", "_native_datatype", "_changetime"

    _classlock = Lock()  # For incrementing instance counters
    _last_id = 0
    _instances_by_id: Dict[int, "Property"] = {}
    _changed_properties: Set["Property"] = set()
    _changed_properties_save_timeout = 5.

    # For storing meta information beyond the persistent value of the property.
    namespace_sep = ':'

    UPDATED = object()
    UPDATED_AND_CHANGED = object()
    _eventids = {UPDATED, UPDATED_AND_CHANGED, PropertyDict.CHANGED}

    @classmethod
    def check_unsaved_changes(cls):
        for p in Property._changed_properties.copy():  # type: Property
            if p._changetime is None or time() >= p._changetime + Property._changed_properties_save_timeout:
                p.save_setting(p._value, p._datatype, ensure_path_absolute=False)
                p._changetime = None
                Property._changed_properties.discard(p)

    @classmethod
    def get_by_id(cls, pr_id: int) -> Optional["Property"]:
        # Speedup accessing by id instead of paths. Usecase in http, mqtt etc.
        return cls._instances_by_id.get(pr_id)

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
        self.parentdict: Optional[PropertyDict] = None  # ToDo: Use QObject.parent only?
        self._valuepool = valuepool
        self._event_manager: Optional[EventManager] = EventManager(self, self._eventids) if self._eventids else None
        self._changetime: Optional[float] = None

        if datatype is DataType.PROPERTYDICT or isinstance(initial_value, PropertyDict):
            # This Property contains a subordinal PropertyDict.
            self._is_persistent = False  # Force
            self._datatype = DataType.PROPERTYDICT  # Force
            self._native_datatype = None
            self._value = initial_value  # Collect PropertyDict
            self._default_value = None

            if not isinstance(initial_value, PropertyDict):
                raise PropertyException('If providing datatype as PROPERTYDICT you also have to provide '
                                        'a new instance of PropertyDict.')

            if initial_value.parentproperty is not None:
                raise ValueError("PropertyDict already contained by other Property.")
            initial_value.parentproperty = self

        else:
            # Any other value
            self._datatype = datatype
            self._native_datatype = DataType.to_basic_type(datatype)
            self._default_value = initial_value
            self._is_persistent = persistent
            self._value = NotLoaded if persistent else initial_value

            if self._datatype is DataType.ENUM:
                if not isinstance(type(initial_value), EnumMeta):
                    raise ValueError('DataType.ENUM requires initial_value to be a member of an enum.')

                if valuepool is None:
                    # Create valuepool from Enum
                    enum = type(initial_value)
                    self._valuepool = {e: e.value for e in enum}

        with Property._classlock:
            # Unique numeric ID for fast access and easier identification
            self._id = Property._last_id = Property._last_id + 1

            # Collect all instances
            Property._instances_by_id[self._id] = self

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
        self.load_value(ensure_path_absolute=False)  # For persistent values or sub property dicts

        # Load other attributes: logging, exposed...

        self._loaded = True

    def load_value(self, ensure_path_absolute=True):
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
                    logger.warning('Found unknown enum member in settings. Reverting to default for %r.', (self,))
                    self.value_to_default()
            else:
                self.value = settings.get(self.path, self._default_value, self._datatype)

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
        if self._datatype is DataType.PROPERTYDICT:
            raise ValueError('Setting a new value on a Property containing a PropertyDict is not allowed.')

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

            if self._is_persistent:
                if not self.path_is_absolute:
                    logger.error(f"Could not save new value of Property because path is not yet defined: {self!r}")
                    return

                # Mark as unsaved
                self._changetime = time()
                Property._changed_properties.add(self)

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
        if self._event_manager:
            self._event_manager.unload()
        self._event_manager = None

        if isinstance(self._value, PropertyDict):
            logcall(self._value.unload, errmsg="Exception during unloading nested PropertyDict: %s")

        del self._value
        del self.parentdict
        del self._path
        del self._valuepool

        if self._lock:
            self._lock = None

        if self._id in self._instances_by_id:
            self._instances_by_id.pop(self._id)
        else:
            logger.warning("My id was not found in _instances_by_id for removal.")

    def __repr__(self):
        ret = f"<{self.__class__.__name__} key='{self.key}', type={self._datatype}, default={self._default_value}, desc='{self.desc}'"

        if self.parentdict is not None:
            ret += f", bound to {self.parentdict!r}"

        if self._is_persistent:
            ret += ", persistent"

        return ret + ">"

    def __contains__(self, key: str):
        return key in self.value

    def __getitem__(self, key: str):
        return self.value[key]

    def __delitem__(self, key: str):
        del self.value[key]

    def __bool__(self):
        return bool(self.value)

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __str__(self):
        return str(self.value)


class SelectProperty(Property):
    """
    Binds to a specific Property which is interchangeable.
    """
    __slots__ = "_selected_property", "_expected_datatype",

    SELECTED = object()
    _eventids = Property._eventids | {SELECTED}

    def __init__(
            self,
            expected_datatype: DataType,
            default_path: str = None,
            valuepool: Union[Iterable, Dict[Any, str]] = None,
            desc: str = None,
            persistent=True
    ):
        # This property practically contains the path to another Property
        super().__init__(datatype=DataType.STRING, initial_value=default_path, valuepool=valuepool, desc=desc,
                         persistent=persistent)

        self._selected_property: Optional[Property] = None
        self._expected_datatype = expected_datatype

    @property
    def is_selected(self) -> bool:
        return isinstance(self._selected_property, Property)

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
    def selected_path(self) -> Optional[str]:
        return super().value

    @selected_path.setter
    def selected_path(self, newpath: Optional[str]):
        self.selected_property = PropertyDict.root().get(newpath) if newpath else None
        if newpath and self._selected_property is None:
            logger.warning('Path for selection does not exist (anymore): "%s". Selection has been removed.', (newpath,))

    @property
    def selected_property(self) -> Optional[Property]:
        """Returns the selected Property if set or None."""
        return self._selected_property

    @selected_property.setter
    def selected_property(self, new_property: Optional[Property]):
        if self.events:
            if isinstance(self._selected_property, Property):
                # Unsubscribe from previously selected property
                for eventid, func in self._event_mapping.items():
                    self._selected_property.events.unsubscribe(func, eventid)

            if isinstance(new_property, Property):
                # Subscribe to events from new property
                for eventid, func in self._event_mapping.items():
                    self._selected_property.events.subscribe(func, eventid)

        changed = self.events and self._selected_property is not new_property

        # Remember new property
        self._selected_property = new_property

        # Set path also
        # Call base classes' setter of value.
        Property.value.__set__(self, new_property.path if new_property else None)

        if changed:
            self.events.emit(self.SELECTED)

    def load(self):
        super().load()
        self.selected_path = self._value

    @property
    def value(self):
        # "value" always refers to the selected property's value. Not to self.value which contains the path.

        # Property must be set here
        if self._selected_property is None:
            raise ValueError("A Property has not been selected yet. No value available.")

        return self._selected_property.value

    @value.setter
    def value(self, newvalue):
        # if not self._allowwrite:
        raise PropertyException("Setting new values to selected properties is not allowed. "
                                "They're supposed to be read only.")

    def __repr__(self):
        ret = super().__repr__()[:-1]
        ret += f", selected property='{self._selected_property!r}'"
        return ret + ">"

    def unload(self):
        self._selected_property = None
        super().unload()


class ROProperty(Property):
    """
    This type of Property holds a static value.
    Mutable object's contents can still be changed.
    """
    __slots__ = "_locked",

    DEFINED = object()
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
        # Getter
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
    __slots__ = "_func", "_maxage", "_time", "args", "kwargs"

    BEFORE_FUNC_CALL = object()
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
        self._func = getterfunc
        self._maxage = maxage
        self._time = 0.

        self.args = list(args) if args else []
        self.kwargs = dict(kwargs) if kwargs else {}

    @property
    def cachevalid(self) -> bool:
        """Is the cached value valid?"""
        return self.age < self._maxage

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
                self._func,
                errmsg="Exception caught during getting value of FunctionProperty: %s",
                stack_trace=True,
                *self.args,
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
        ret = super().__repr__()[:-1]
        ret += f", func={self._func!r}, maxage={self._maxage}"
        return ret + ">"

    def unload(self):
        del self._func
        del self.kwargs
        del self.args
        super().unload()


class IntervalProperty(Property):
    _event_table = EventTable()

    @classmethod
    def run_event_loop(cls):
        for e in cls._event_table:
            e.activate()

        # Start the blocking loop.
        cls._event_table.event_loop_start()

        # Loop finished. Cleanup.
        for e in cls._event_table:
            e.deactivate()

    @classmethod
    def stop_event_loop(cls):
        cls._event_table.event_loop_stop()

    def __init__(
            self,
            callback_func,
            default_interval=1.,
            desc: str = None,
            persistent_interval=True,
    ):

        Property.__init__(
            self,
            datatype=DataType.TIMERANGE,
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
    _event_table = EventTable()

    def __init__(
            self,
            timeout_func,
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
            self.restart()

    @property
    def timeout_active(self) -> bool:
        return self._event.on_time is not None


class QtPropLink(QtProperty):
    def __init__(self, datatype, path: str, notify: Signal = None):
        """
        datatype: Datatype in Qt format
        path: Path to linked Property relative to Module class
            "instancename/propertykey" or for main instance: "propertykey"
        notify: Signal to notify or None for constant properties
        """
        QtProperty.__init__(
            self,
            type=datatype,
            fget=self.f_get,
            fset=self.f_set,
            notify=notify,
            constant=notify is None
        )
        self._notify = str(notify)[:-2]  # Remember name of signal only
        self._path = path

        # ToDo: Property-Changes -> Qt-Notify

    def f_get(self, modinst):
        prop: Property = modinst.properties[self._path]

        # Return bare value
        return prop.value

    def f_set(self, modinst, newvalue):
        # Get signal from parent which has the emit function.
        prop: Property = modinst.properties[self._path]
        prop.value = newvalue

        # Notify change
        notify = getattr(modinst, self._notify)
        notify.emit()


class QtPropLinkEnum(QtPropLink):
    def f_get(self, modinst):
        prop: Property = modinst.properties[self._path]
        # Convert Enum to str for Qml
        return prop.value.name

    # Property.setter will convert string to enum.


class QtPropLinkSelect(QtPropLink):
    def f_get(self, modinst):
        prop: SelectProperty = modinst.properties[self._path]

        # Qml uses path only
        return prop.selected_path

    def f_set(self, modinst, newvalue):
        # Get signal from parent which has the emit function.
        prop: SelectProperty = modinst.properties[self._path]

        # Set new path
        prop.selected_path = newvalue

        # Notify change
        notify = getattr(modinst, self._notify)
        notify.emit()