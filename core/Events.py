# -*- coding: utf-8 -*-

import logging
from typing import NoReturn, Callable, Any, Dict, Iterable, Set
from threading import Event, Lock

callback_function = Callable[[Any], NoReturn]


class EventManager:
    __slots__ = "_source", "_emit_fncs", "_is_emitting", "_waitable_events", "_lock"

    def __init__(self, source_element: Any, eventids: Iterable):
        self._source = source_element
        self._emit_fncs: Dict[Any, Set[callback_function]] = {evid: set() for evid in eventids}
        self._is_emitting: Dict[Any, bool] = {evid: False for evid in eventids}
        self._waitable_events: Dict[Any, Event] = {}
        self._lock = Lock()

    def subscribe(self, fnc: callback_function, eventid):
        if eventid not in self._emit_fncs:
            raise KeyError("eventid unknown: " + str(eventid))

        add_set = self._emit_fncs[eventid]

        if fnc in add_set:
            raise KeyError("Function is already subscribed.")
        add_set.add(fnc)

    def unsubscribe(self, fnc: callback_function, eventid):
        if eventid not in self._emit_fncs:
            raise KeyError("eventid unknown: " + str(eventid))

        del_set = self._emit_fncs[eventid]

        if fnc not in del_set:
            raise KeyError("Function is not subscribed.")

        del_set.remove(fnc)

    def emit(self, eventid):
        if self._is_emitting[eventid]:
            # Because may be called multiple times.
            return

        funcset = self._emit_fncs[eventid]
        try:
            self._is_emitting[eventid] = True
            for fnc in funcset.copy():  # Original Set may get changed during calling events
                try:
                    fnc(self._source)
                except Exception as e:
                    logging.error(f"Exception while calling event {eventid!s} during calling function {fnc!r} which"
                                  f" has subscribed for {self._source!r}: {e}")
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
