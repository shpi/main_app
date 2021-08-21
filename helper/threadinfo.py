# -*- coding: utf-8 -*-

import threading
import os
import time
from pathlib import Path


_mainpid = os.getpid()
_mainthread_dir = Path('/proc', str(_mainpid))
_threads_dir = _mainthread_dir / 'task'
# _stat_path = _mainthread_dir / 'stat'


_known_threads = {}


_tick = os.sysconf("SC_CLK_TCK")


def _stat_array(stat_file: Path):
    """
    Returns an array of data beginning after thread name
    https://man7.org/linux/man-pages/man5/proc.5.html
    """
    data_str = stat_file.read_text()
    # pos1 = data_str.find('(')
    pos2 = data_str.find(')')
    # name = data_str[pos1+1:pos2]
    data_str = data_str[pos2 + 2:-1]
    return data_str.split()


class ThreadInfo:
    def __init__(self, path: Path, python_tname: str = None):
        # Thread name
        self._threadname = 'Thread'  # Fallback
        if python_tname:
            # Force use this name. Only python knows his internal threadnames.
            self._threadname = python_tname
        else:
            # Get threadname from kernel
            name_path = path / 'comm'
            if name_path.is_file():
                self._threadname = name_path.read_text().strip()

        self._stat_path = path / 'stat'

        # Read stats to determine startime
        data = _stat_array(self._stat_path)
        self._starttime = int(data[19]) / _tick

    def update_stats(self):
        try:
            data = _stat_array(self._stat_path)
        except FileNotFoundError:
            # Thread disappeared during iteration.
            return

        utime = int(data[11]) / _tick
        stime = int(data[12]) / _tick
        total_load = utime + stime

        boot_time = time.clock_gettime(time.CLOCK_BOOTTIME)
        runtime = boot_time - self._starttime

        if runtime > 0:
            runtime_load_avg = total_load / runtime * 100
            print('Thread:', self._threadname, " runtime:", round(runtime), "s  cputime:", round(total_load, 4), "s  fractional cputime:", round(runtime_load_avg, 4), '%')


def check_threads():
    current = {int(t) for t in _known_threads}
    python_threadname = {t.native_id: t.name for t in threading.enumerate()}

    print("\n=== Thread info ===")

    for t in _threads_dir.iterdir():
        pid = int(t.name)

        prop = _known_threads.get(str(pid))
        if prop is None:
            # It's a new thread
            prop = _known_threads[str(pid)] = ThreadInfo(t, python_threadname.get(pid))
        else:
            # pid still Exists
            current.remove(pid)

        prop.update_stats()

    # Disappeared threads
    for t in current:
        del _known_threads[str(t)]


# def example_thread():
#     while True:
#         time.sleep(1.)


# Start a test thread
# t1 = threading.Thread(target=example_thread, name="example_thread")
# t1.start()
#
#
# while True:
#     # Check thread in your app.
#     time.sleep(5.)
#     check_threads()

def _own_thread(seconds: int):
    while True:
        time.sleep(seconds)
        check_threads()


def start_own_thread(seconds: int) -> threading.Thread:
    t = threading.Thread(target=_own_thread, name="threadinfo_thread", args=(seconds, ), daemon=True)
    t.start()
    return t
