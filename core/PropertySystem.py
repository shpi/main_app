# -*- coding: utf-8 -*-

"""
Defining, storing, sharing, controlling and announcing of values defined by paths.
"""

import logging
from collections import UserDict
from typing import Optional, Union, Any, Callable, Iterable, Coroutine, Tuple, List, Dict
from time import time
from threading import Lock, RLock

from core.Events import SubscriptionManager
from core.DataTypes import DataType
from core.Settings import settings

NotLoaded = object()


class PropertyDict(UserDict):
    """
    Holds key, value structured properties.
    Contains inherited classes of Property which wrap any data type or even sub PropertyLists.

    Properties belonging related to root instance should only be created in modules within define_properties().
    PropertyLists and Properties are meant to be static, once created. Removing and extending later is prohibited.
    Use appropriate values with specific data types for more flexible functions.

    Each PropertyList may be represented by a path.
    The first created PropertyDict (root) has path=None.
    Lose PropertyDicts have their path=".".
    PropertyDicts bound in other PropertyDicts get their path fetched from containing Property.path.
    """
    __slots__ = "parentproperty"
    _root_instance: Optional["PropertyDict"] = None

    @classmethod
    def find_property(cls, path: str) -> Optional["Property"]:
        if PropertyDict._root_instance is None:
            raise KeyError("No root instance available.")

        return PropertyDict._root_instance.get(path)

    @classmethod
    def root(cls, allowcreate=False) -> Optional["PropertyDict"]:
        """Get root PropertyDict and allow creation if it does not yet exist."""
        if PropertyDict._root_instance is None and allowcreate:
            # Create a first instance.
            PropertyDict._root_instance = PropertyDict()

        # Get root instance
        return PropertyDict._root_instance

    def __init__(self, **kwargs):
        """
        Initializes a new PropertyDict object.

        :param desc: Optional description of list. May be visible in raw propertysystem access methods.
        :param kwargs: Initial properties.
        """
        UserDict.__init__(self)
        self.parentproperty: Optional["Property"] = None  # Parent property if set

        if PropertyDict._root_instance is None:
            # First instance of PropertyDict becomes root
            PropertyDict._root_instance = self

        for key, prop in kwargs.items():
            self[key] = prop

    @property
    def is_root(self) -> bool:
        """Checks for instance is root instance."""
        return self is PropertyDict._root_instance

    @property
    def path(self) -> Optional[str]:
        """
        Returns the path representation of this PropertyDict.
        root PropertyDict returns: None
        Lose PropertyDicts are relative and return "."
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
            return "."

    def __getitem__(self, key: str) -> "Property":
        """
        Gets a Porperty from PropertyDict instance.
        Paths may be provided as key. Property will be acquired recursively.

        :param key: Simple key string "myproperty" or a path "sublist.myproperty" relative to this instance.
        :return: Found Property or KeyError
        """

        if type(key) is not str:
            raise TypeError("Key must be a string.")

        if "." in key:
            # Dig deeper in tree structure.
            keys = key.split(".", maxsplit=1)
            return self[keys[0]][keys[1]]
        else:
            if key in self.data:
                return self.data[key]

        raise KeyError(key)

    def __setitem__(self, key: str, item: Union["PropertyDict", "Property"]):
        """
        Add Property (or any Value which will be wrapped into a new Property) to list.
        Key has to be unique in this list.

        :param key: String, no dots and spaces allowed.
        :param item: Property, PropertyDict which are not bound yet or any other object or value.
        """

        if type(key) is not str:
            raise TypeError("Key must be a string.")

        if "." in key or " " in key:
            raise TypeError("Key must not contain a dot '.' or spaces")

        if key in self.data:
            raise TypeError("key already in PropertyDict. Properties can't be changed after once added. You may "
                            "want to assign a new value to the existing property's 'value'?")

        if isinstance(item, PropertyDict):
            # Wrap in Property
            item.parentproperty = item = Property(datatype=DataType.PROPERTYDICT, initial_value=item,
                                                  desc="This Property contains a nested PropertyDict", persistent=False)

        if not isinstance(item, Property):
            # Not allowed. Wrap object in new simple Property
            raise ValueError("Items in PropertyDict must be Property or PropertyDict.")

        if item.parentdict is not None:
            raise TypeError("Property already assigned to another PropertyDict")

        # Link parent
        item.parentdict = self

        # Collect new Property
        self.data[key] = item

        # Give it a hint of it's key
        item._key = key

    def __delitem__(self, key: str):
        delitem: Property = self.data.get(key)

        if delitem is None:
            raise KeyError(f"Property '{key}' not found.")

        try:
            delitem.unload()
        except Exception as e:
            print("Exception on unloading Property:", str(e))
        finally:
            self.data.pop(key)

    def __contains__(self, key: str):
        return key in self.data

    def __repr__(self):
        if self.is_root:
            return f"PropertyDict ROOT ({len(self.data)} elements)"
        if self.parentproperty is not None:
            return f"PropertyDict '{self.parentproperty.key}' ({len(self.data)} elements)"
        else:
            return f"PropertyDict ORPHAN ({len(self.data)} elements)"

    def unload(self):
        for prop in self.data.values():
            if isinstance(prop, Property):
                try:
                    prop.unload()
                except Exception as e:
                    logging.error("Exception on unloading Property: " + str(e))

        self.data.clear()
        if isinstance(self.parentproperty, Property):
            self.parentproperty.desc = "PropertyDict hast been unloaded."
            self.parentproperty.value = None  # remove me there

        self.parentproperty = None


class Property:
    """
    Defines a simple property with an initial value of any type.
    Provides a value-property for read and write access.

    A Property may be parented to a PropertyDict.
    When parented, it is accessable by key in the PropertyDict as key-value-pair.
    Properties may contain another sub PropertyDicts.
    """

    __slots__ = "_value", "parentdict", "_key", "_path", "_id", "desc", "_lock", "_valuepool", "_subscr_mgr", \
                "_datatype", "_is_persistent", "_default_value"
    _classlock = Lock()  # For incrementing instance counters
    _last_id = 0
    _instances_by_id: Dict[int, "Property"] = {}

    UPDATED = object()
    UPDATED_AND_CHANGED = object()
    _eventids = {UPDATED, UPDATED_AND_CHANGED}

    @classmethod
    def get_by_id(cls, pr_id: int) -> Optional["Property"]:
        return cls._instances_by_id.get(pr_id)

    def __init__(
            self,
            datatype: DataType,
            initial_value: Any = None,
            valuepool: Union[Iterable, Dict[Any, str]] = None,
            desc: str = None,
            persistent=True
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
        self._key: Optional[str] = None  # Cache attribute
        self._path: Optional[str] = None  # Cache attribute
        self.desc: str = desc
        self.parentdict: Optional[PropertyDict] = None
        self._valuepool = valuepool
        self._subscr_mgr: Optional[SubscriptionManager] = \
            SubscriptionManager(self, self._eventids) if self._eventids else None
        self._is_persistent = persistent

        with Property._classlock:
            # Unique numeric ID for fast access and easier identification
            self._id = Property._last_id = Property._last_id + 1

            # Collect all instances
            Property._instances_by_id[self._id] = self

        if isinstance(initial_value, PropertyDict):
            # This Property contains a subordinal PropertyDict.
            if persistent:
                raise ValueError("Setting persistency is not allowed with PropertyDicts as value.")

            self._datatype = DataType.PROPERTYDICT  # Force
            self._value = initial_value  # Collect PropertyDict
            if initial_value.parentproperty is not None:
                raise ValueError("PropertyDict already contained by other Property.")
            initial_value.parentproperty = self
        else:
            # Any other value
            self._datatype = datatype
            if persistent:
                # Property with default but load from settings
                self._default_value = initial_value
                self._value = NotLoaded  # Load on first read (when path has been built)
            else:
                # Property which has some value
                self._default_value = initial_value
                self._value = initial_value  # Directly cache this value

    @property
    def id(self) -> int:
        """Temporary numeric id of property. May change on next program run. Do not hard rely on that."""
        return self._id

    @property
    def events(self) -> Optional[SubscriptionManager]:
        return self._subscr_mgr

    @property
    def valuepool(self) -> Union[Iterable, Dict[Any, str], None]:
        return self._valuepool

    @property
    def value(self) -> Any:
        v = self._value

        if v is NotLoaded:
            # It's a persistent property. Let's load the value from settings.
            path = self._path
            if path is None or path.startswith("."):
                raise ValueError("Can't read persistent value before path has been defined. "
                                 "'value' getter has been called too early.")
            v = settings.get(path, self._datatype)

        return v

    @value.setter
    def value(self, newvalue: Any):
        with self._lock:
            # Also check if value has really changed.
            changed = self._value != newvalue

            # Set new value
            self._value = newvalue

            if not self._subscr_mgr:
                # No events.
                return

            self._subscr_mgr.emit(self.UPDATED)
            if changed:
                self._subscr_mgr.emit(self.UPDATED_AND_CHANGED)

            if self._is_persistent:
                path = self._path
                if path is None or path.startswith("."):
                    raise ValueError("Can't write persistent value before path has been defined. "
                                     "'value' setter has been called too early.")
                settings.set(path, newvalue, self._datatype)

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

        if parentpath == ".":
            # lose
            newpath = f".{self._key}"
        else:
            # lose or absolute
            newpath = f"{parentpath}.{self._key}"

        if not newpath.startswith("."):
            # Will not change. Cache it.
            self._path = newpath

        return newpath

    def unload(self):
        if self._subscr_mgr:
            self._subscr_mgr.unload()
            del self._subscr_mgr

        if isinstance(self._value, PropertyDict):
            try:
                self._value.unload()
            except Exception as e:
                logging.error("Exception during unloading PropertyDict: %s", str(e))

        self.parentdict = None
        self._value = None
        self._key = None
        self._path = None
        self._valuepool = None
        self._lock = None
        self._instances_by_id.pop(self._id)

    def __repr__(self):
        ret = f"<{self.__class__.__name__} key='{self._key}', type={self._datatype}, default={self._default_value}"

        if self.parentdict is not None:
            ret += f", bound to {self.parentdict!r}"

        if callable(self._value):
            ret += ", callable"

        if self._is_persistent:
            ret += ", persistent"

        return ret + ">"

    def __contains__(self, key: str):
        return key in self.value

    def __getitem__(self, key: str):
        return self.value[key]

    def __bool__(self):
        return bool(self.value)

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __str__(self):
        return str(self.value)

    def __call__(self, *args, **kwargs):
        self.value(*args, **kwargs)

    @property
    def is_callable(self) -> bool:
        return callable(self._value)


class SelectProperty(Property):
    """
    Binds to a master Property which is interchangeable.
    """
    __slots__ = "_selected_property",

    SELECTED = object()
    _eventids = Property._eventids | {SELECTED}

    def __init__(
            self,
            datatype: DataType,
            default_path: str = None,
            valuepool: Union[Iterable, Dict[Any, str]] = None,
            desc: str = None,
            persistent=True
    ):
        super().__init__(datatype=datatype, initial_value=default_path, desc=desc, persistent=persistent)

    @property
    def is_selected(self) -> bool:
        return self._masterproperty is not None

    @property
    def select(self) -> Optional[Property]:
        """Returns the master Property if set or None."""
        return self._masterproperty

    @select.setter
    def masterproperty(self, newmaster: Optional[Property]):
        if isinstance(self._masterproperty, Property):
            self._masterproperty.remove_subscription(id(self))

        if isinstance(newmaster, Property):
            newmaster.add_subscription(fnc=self._mastervaluechanged, key=id(self))

        self._masterproperty = newmaster

    @property
    def masterpath(self) -> Optional[str]:
        """Returns the master Property path if set or None."""
        if isinstance(self._masterproperty, Property):
            return self._masterproperty.path
        else:
            return None

    @masterpath.setter
    def masterpath(self, newmasterpath: str):
        newprop = PropertyDict.find_property(newmasterpath)

        if newprop is None:
            raise KeyError("Could not find masterproperty by path:" + str(newmasterpath))

        self.masterproperty = newprop

    @property
    def _value(self):
        return self._masterproperty.value

    @_value.setter
    def _value(self, newvalue):
        if self._masterproperty is None:
            # Just write nowhere then. Should not write during __init__ before masteproperty is set.
            return
        Property.value.__set__(self._masterproperty, newvalue)

    @property
    def value(self):
        if self._masterproperty is None:
            raise ValueError("Master property has not been set yet. No value available.")

        return self._value

    @value.setter
    def value(self, newvalue):
        if not self._allowwrite:
            raise ValueError("Setting new value is not allowed.")
        self._value = newvalue

    def __repr__(self):
        ret = f"<{self.__class__.__name__} key='{self._key}', containing property='{repr(self._masterproperty)}'"

        if self.parentdict is not None:
            ret += f", bound to {repr(self.parentdict)}"

        if isinstance(self._masterproperty, Property):
            if self._masterproperty.callable():
                ret += ", callable"

        return ret + ">"

    def __call__(self, *args, **kwargs):
        self._masterproperty.value(*args, **kwargs)

    def callable(self) -> bool:
        return self._masterproperty.callable()

    def unload(self):
        self.masterproperty = None
        super().unload()


class ROProperty(Property):
    """
    This type of Property holds a static value.
    Mutable object's contents can still be changed.
    """
    __slots__ = "_locked"

    _eventids = None

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
        Property.__init__(self, datatype=datatype, initial_value=value, valuepool=valuepool, desc=desc)
        self._locked = locknow

    @property
    def value(self):
        # Getter
        if not self._locked:
            raise ValueError(f"Read only value has not been set yet: {self!r}")

        return super().value

    @value.setter
    def value(self, newvalue):
        if self._locked:
            raise ValueError("Read only value has already been set before.")

        # Set value
        Property.value.__set__(self, newvalue)

        # Disallow further value sets
        self._locked = True

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

    def __init__(
            self,
            datatype: DataType,
            getterfunc: Callable,
            args: list = None,
            kwargs: dict = None,
            maxage=0.,
            valuepool: Union[Iterable, Dict[Any, str]] = None,
            desc: str = None
    ):
        """
        Creates a Property sourcing it's value from a function

        :param datatype: DataType specification for this property
        :param getterfunc: Function to get called on request. Return value is used.
        :param args, kwargs: Static arguments for calls of getterfunc.
        :param maxage: Max age in seconds the value in cache is valid before function will be called again.
        :param desc: Description of Property
        """
        if not callable(getterfunc):
            raise TypeError("getterfunc must provide a callable object.")

        Property.__init__(self, datatype=datatype, valuepool=valuepool, desc=desc, persistent=False)
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

            if not self.cachevalid:
                # Cache is outdated

                # Call the function
                try:
                    newvalue = self._func(*self.args, **self.kwargs)

                except Exception as e:
                    logging.error(f"Exception caught during getting value of {self!r}: {e!s}")
                    return self._value  # Return at least cached value

                # Remember time
                self._time = time()

                # Save new value in cache
                Property.value.__set__(self, newvalue)

            # Return cached value
            return super().value

    @value.setter
    def value(self, newvalue):
        raise ValueError("New values for FunctionProperty cannot be assigned.")

    def __repr__(self):
        ret = super().__repr__()[:-1]

        ret += f", func={self._func!r}, maxage={self._maxage}"

        return ret + ">"

    def unload(self):
        self._func = None
        super().unload()
