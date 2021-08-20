# -*- coding: utf-8 -*-

from logging import getLogger
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Any, Union, Iterator
from threading import Event as _Event, Thread

from core.Logger import LogCall

logger = getLogger(__name__)
logcall = LogCall(logger)


class Event:
    __slots__ = "_table", "_on_time", "_event_func", "_event_data", "_allow_reschedule"

    def __init__(self, table: "EventTable", now: datetime = None, seconds: float = None):
        self._table = table
        self._on_time: Optional[datetime] = None

        if now is not None:
            if seconds is None:
                self._on_time = now
            else:
                self._on_time = now + timedelta(seconds=seconds)

        self._event_func: Union[Callable[[datetime, Any], Any], Callable[[datetime], Any], None] = None
        self._event_data = None

    @property
    def on_time(self) -> Optional[datetime]:
        return self._on_time

    def set_event(self, func: Union[Callable[[datetime, Any], Any], Callable[[datetime], Any]], data=NotImplemented):
        self._event_func = func
        self._event_data = data

    def emit(self):
        if not self._event_func:
            logger.error("Event has no event function assigned. It will be deactivated now.")
            self._table.remove_event(self)
            return

        if self._event_data is NotImplemented:
            args = (self._on_time, )
        else:
            args = (self._on_time, self._event_data)

        try:
            logcall(
                self._event_func,
                *args,
                errmsg=f"Exception occured during calling event's function '{self._event_func!r}': %s",
                stack_trace=True,
            )
        except Exception as e:
            logger.error("Critical error. logcall failed: %s", e, exc_info=True)

    def reschedule(self, new_time: datetime, additional_seconds: float = None):
        if additional_seconds is None:
            self._on_time = new_time
        else:
            self._on_time = new_time + timedelta(seconds=additional_seconds)

        self.activate()

    def activate(self):
        if self._table:
            # print("## calling activate")
            self._table.schedule_event(self)

    def deactivate(self):
        self._on_time = None
        if self._table:
            self._table.remove_event(self)

    def unload(self):
        if self._table:
            t = self._table
            self._table = None
            t.remove_event(self, full=True)
            del self._event_func
            del self._event_data

    def __repr__(self):
        return f"<Event[@{self._on_time}: {self._event_func}(data={self._event_data})]>"


def _get_time(e: Event) -> datetime:
    return e.on_time


class EventTable:
    __slots__ = "_active_events", "_all_events", "_event_loop_running", "_t_event", "_event_thread", "_name"

    def __init__(self, name: str):
        self._name = name
        self._active_events: List[Event] = []
        self._all_events: List[Event] = []
        self._event_loop_running = False
        self._t_event = _Event()
        self._event_thread: Optional[Thread] = None

    def __iter__(self) -> Iterator[Event]:
        return iter(self._all_events)

    def create_event(self, now: datetime = None, secs: float = None, func=None, func_data=NotImplemented) -> Event:
        e = Event(self, now, secs)

        # event.reschedule must be used.
        self._all_events.append(e)

        if func:
            e.set_event(func, func_data)

        if now is not None:
            self._active_events.append(e)
            self._t_event.set()  # Trigger eventloop wait to restart.

        return e

    def remove_event(self, event: Event, full=False):
        # Prevent from emitting anyway. Remove from queue.
        if event in self._active_events:
            # print("removing event", event)
            self._active_events.remove(event)
            self._t_event.set()  # Trigger eventloop wait to restart.

        if full:
            # Remove event completely
            if event in self._all_events:
                self._all_events.remove(event)

            # Full kill or just a one time event
            # Try unload if remove_event wasn't called by event.unload()
            event.unload()

    def schedule_event(self, event: Event):
        # print("## rescheduling event", event)
        if event in self._active_events:
            # print("already scheduled", event)
            # Already scheduled and in queue
            return

        if event not in self._all_events:
            raise AttributeError("Event unknown.")

        if event.on_time is None:
            raise AttributeError("Event does not have a scheduled time.")

        self._active_events.append(event)
        self._t_event.set()  # Trigger eventloop wait to restart.

    def get_next_event(self) -> Optional[Event]:
        if not self._active_events:
            # Empty event list
            return None

        # Get lowest event
        event = min(self._active_events, key=_get_time)
        return event

    def handle_events_until(self, until: datetime):
        while True:
            e = self.get_next_event()
            if e is None:
                # List empty
                break

            if e.on_time <= until:
                self._handle_event(e)

            else:
                # Event not yet due
                break

    def _handle_event(self, e: Event):
        # Remember original time of event
        now = e.on_time

        # Call event functions
        # print("emit", e)
        e.emit()

        if e.on_time <= now:
            # Not rescheduled. Remove it.
            # print("remove")
            self.remove_event(e)
        else:
            self._t_event.set()  # Trigger eventloop wait to restart.

    def event_loop_stop(self):
        self._event_loop_running = False
        self._t_event.set()  # Trigger eventloop wait to restart.
        if self._event_thread and self._event_thread.is_alive():
            self._event_thread.join(5)

        self._event_thread = None

    def event_loop_start(self):
        """
        Starts a new thread
        """
        if self._event_loop_running:
            raise RecursionError("event_loop already running.")

        name = "EventTable_eventloop"
        if self._name:
            name += "_" + self._name

        self._event_thread = Thread(target=self.event_loop, name=name)
        self._event_thread.start()

    def event_loop(self):
        if self._event_loop_running:
            raise RecursionError("event_loop already running.")

        try:
            self._event_loop_running = True

            while self._event_loop_running:
                e = self.get_next_event()
                if e is None:
                    # No events. Sleep a little bit or wakeup on event changes
                    if self._t_event.wait(2.):
                        # wait was interrupted. Events changed.
                        self._t_event.clear()
                    continue

                # Remaining time
                diff = (e.on_time - datetime.now()).total_seconds()
                # print("remaining:", diff, "on_time was:", e.on_time, e)
                if diff > 0.:
                    # Still time to wait.
                    if self._t_event.wait(diff):
                        # Events changed. Maybe some event must be emitted ealier. Restart loop.
                        self._t_event.clear()
                        continue
                    # else: We waited the exact time to emit the event.

                if self._event_loop_running:
                    self._handle_event(e)

        finally:
            self._event_loop_running = False

    def activate_all(self):
        for e in self._all_events:
            if e.on_time:
                e.activate()

    def deactivate_all(self):
        for e in self._all_events:
            e.deactivate()

    def unload(self):
        self.event_loop_stop()

        for e in self._all_events.copy():
            e.unload()

        self._all_events.clear()
        self._active_events.clear()
