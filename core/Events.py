# -*- coding: utf-8 -*-

from logging import getLogger
import inspect
from typing import NoReturn, Callable, Any, Dict, Iterable, Union
from threading import Event, Lock
from functools import partial


logger = getLogger(__name__)

callback_function = Union[Callable[[Any], NoReturn], Callable[[], NoReturn]]
function = Union[Callable[[Any], NoReturn], Callable[[Any, Any], NoReturn]]


class EventManager:
    __slots__ = "_source", "_emit_fncs", "_is_emitting", "_waitable_events", "_lock"

    def __init__(self, source_element: Any, eventids: Iterable):
        self._source = source_element
        self._emit_fncs: Dict[Any, Dict[callback_function, function]] = {evid: dict() for evid in eventids}
        self._is_emitting: Dict[Any, bool] = {evid: False for evid in eventids}
        self._waitable_events: Dict[Any, Event] = {}
        self._lock = Lock()

    def subscribe(self, fnc: callback_function, eventid):
        if eventid not in self._emit_fncs:
            raise KeyError("eventid unknown: " + str(eventid))

        if not inspect.isfunction(fnc) and not inspect.ismethod(fnc):
            raise ValueError("fnc must be callable. Provide a method or function.")

        event_dict = self._emit_fncs[eventid]

        if fnc in event_dict:
            raise KeyError("Function is already subscribed.")

        # Check parameters count
        sig = inspect.signature(fnc)
        argcount = len(sig.parameters)

        if argcount in {1, 2}:
            # arg1 of fnc receives the source object
            # arg2 of fnc received data
            event_dict[fnc] = fnc

        elif argcount == 0:  # Function has no arguments and does not care about source object
            # Wrap function
            event_dict[fnc] = lambda x: partial(fnc)

        else:
            raise ValueError("Function in fnc must provide either one or none arguments.")

    def unsubscribe(self, fnc: callback_function, eventid):
        if eventid not in self._emit_fncs:
            raise KeyError("eventid unknown: " + str(eventid))

        event_dict = self._emit_fncs[eventid]

        if fnc not in event_dict:
            raise KeyError("Function is not subscribed.")

        del event_dict[fnc]

    def emit(self, eventid, value=None):
        if self._is_emitting[eventid]:
            # Because may be called multiple times.
            return

        event_dict = self._emit_fncs[eventid]
        try:
            self._is_emitting[eventid] = True
            for fnc in tuple(event_dict.values()):  # Original Dict may get changed during calling events
                try:
                    if value is None:
                        fnc(self._source)
                    else:
                        fnc(self._source, value)
                except Exception as e:
                    logger.error('Exception while calling event %s during calling function %r which'
                                 ' has subscribed for %r: %s', eventid, fnc, self._source, e)
        finally:
            self._is_emitting[eventid] = False

        e = self._waitable_events.get(eventid)
        if e:
            # Trigger waiting threads
            e.set()
            e.clear()

    def wait_for_event(self, eventid, timeout) -> bool:
        """
        Waits until value of Property has changed.
        Exits after timeout.

        Should run in seperate thread to not disturb program execution.

        :param eventid: The particular eventid
        :param timeout: Timeout in seconds after this method exits at least.
        :returns: True if value has changed or False on timeout.
        """

        with self._lock:
            if eventid in self._waitable_events:
                event = self._waitable_events[eventid]
            else:
                event = self._waitable_events[eventid] = Event()

        return event.wait(timeout)

    def unload(self):
        del self._source
        self._emit_fncs.clear()
        del self._emit_fncs
        self._waitable_events.clear()
        del self._waitable_events
