# -*- coding: utf-8 -*-

"""
Old MainApp
Thread: MainThread  runtime: 168 s  cputime: 14.81 s  fractional cputime: 8.8378 %
Thread: Thread-4  runtime: 160 s  cputime: 0.14 s  fractional cputime: 0.0874 %
Thread: Thread-6  runtime: 160 s  cputime: 2.16 s  fractional cputime: 1.3492 %
Thread: Thread-7  runtime: 160 s  cputime: 3.88 s  fractional cputime: 2.4237 %
Thread: VCHIQ completio  runtime: 159 s  cputime: 0.08 s  fractional cputime: 0.0504 %
Thread: HDispmanx Notif  runtime: 159 s  cputime: 0.0 s  fractional cputime: 0.0 %
Thread: HTV Notify  runtime: 159 s  cputime: 0.0 s  fractional cputime: 0.0 %
Thread: HCEC Notify  runtime: 159 s  cputime: 0.0 s  fractional cputime: 0.0 %
Thread: QEvdevTouchScre  runtime: 159 s  cputime: 0.12 s  fractional cputime: 0.0757 %
Thread: QQmlThread  runtime: 158 s  cputime: 1.91 s  fractional cputime: 1.2051 %
Thread: FileInfoThread  runtime: 155 s  cputime: 0.0 s  fractional cputime: 0.0 %
Thread: QSGRenderThread  runtime: 155 s  cputime: 1.74 s  fractional cputime: 1.1247 %
Thread: threadinfo_thread  runtime: 154 s  cputime: 1.48 s  fractional cputime: 0.9621 %
Thread: 3edd8cdc14e1  runtime: 153 s  cputime: 0.0 s  fractional cputime: 0.0 %
Thread: 19ed1dc1e1  runtime: 153 s  cputime: 4.45 s  fractional cputime: 2.9031 %
Thread: 18ed416dc38fe16  runtime: 153 s  cputime: 0.32 s  fractional cputime: 0.2087 %
Thread: mlx90615  runtime: 153 s  cputime: 4.12 s  fractional cputime: 2.6877 %



MainApp v4

Thread info: MainThread 14.822910505084389
Thread info: VCHIQ completio 0.008601728296805061
Thread info: HDispmanx Notif 0.0
Thread info: HTV Notify 0.0
Thread info: HCEC Notify 0.0
Thread info: QEvdevTouchScre 0.0
Thread info: QQmlThread 1.1268717708525717
Thread info: EventTable_eventloop_IntervalProperty 3.716894172389195
Thread info: input_event2 0.0
Thread info: MLX90615 10.31121899020477
Thread info: Property_worker 1.38661886574521
Thread info: FileInfoThread 0.008933284428694059
Thread info: QSGRenderThread 0.6612046675299257


"""


import os
import sys
import threading
import time
from pathlib import Path

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import Property, Output, ROProperty, PropertyDictProperty, PropertyDict, IntervalProperty


_print_threads = 'THREAD_STATS' in sys.argv


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


_tick = os.sysconf("SC_CLK_TCK")
_page_size = 4 * 1024


class ThreadProperty(PropertyDictProperty):
    __slots__ = '_stat_path', '_is_main', '_set_thread_state', '_set_utime', '_set_stime', \
                '_set_runtime', '_set_total_time', '_set_runtime_load_avg', '_threadname'

    _boot_time = time.clock_gettime(time.CLOCK_BOOTTIME)  # 2362835.656699579

    def __init__(self, path: Path, is_mainthread: bool, python_tname: str = None):
        self._is_main = is_mainthread

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

        pd = PropertyDict()
        PropertyDictProperty.__init__(self, pd, 'Thread info for: ' + self._threadname)

        pd['name'] = ROProperty(DataType.STRING, self._threadname, desc='Name of the thread')

        self._stat_path = path / 'stat'

        p = pd['state'] = Property(Output, DataType.STRING, '?', desc='Thread state', persistent=False)
        self._set_thread_state = p.get_setvalue_func()

        p = pd['utime'] = Property(Output, DataType.TIMEDELTA, 0., desc='User mode time', persistent=False)
        self._set_utime = p.get_setvalue_func()

        p = pd['stime'] = Property(Output, DataType.TIMEDELTA, 0., desc='Kernel mode time', persistent=False)
        self._set_stime = p.get_setvalue_func()

        p = pd['total_time'] = Property(Output, DataType.TIMEDELTA, 0., desc='CPU load time', persistent=False)
        self._set_total_time = p.get_setvalue_func()

        p = pd['runtime'] = Property(Output, DataType.TIMEDELTA, 0., desc='Thread run time', persistent=False)
        self._set_runtime = p.get_setvalue_func()

        p = pd['runtime_load_avg'] = Property(Output, DataType.PERCENT_FLOAT, 0., desc='Average CPU load since start', persistent=False)
        self._set_runtime_load_avg = p.get_setvalue_func()

        data = _stat_array(self._stat_path)
        self._starttime = int(data[19]) / _tick

    def update_stats(self):
        try:
            data = _stat_array(self._stat_path)
        except FileNotFoundError:
            # Thread disappeared during iteration.
            return

        self._set_thread_state(data[0])

        utime = int(data[11]) / _tick
        self._set_utime(utime)

        stime = int(data[12]) / _tick
        self._set_stime(stime)

        total_load = utime + stime
        self._set_total_time(total_load)

        boot_time = time.clock_gettime(time.CLOCK_BOOTTIME)
        runtime = boot_time - self._starttime
        self._set_runtime(runtime)

        if runtime > 0:
            runtime_load_avg = total_load / runtime * 100
            self._set_runtime_load_avg(runtime_load_avg)

            if _print_threads:
                print('Thread:', self._threadname, " runtime:", round(runtime), "s  cputime:", round(total_load, 4),
                      "s  fractional cputime:", round(runtime_load_avg, 4), '%')


class MainApp_Info(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = 'MainApp info'
    categories = ()
    _mainpid = os.getpid()
    _mainthread_dir = Path('/proc', str(_mainpid))
    _threads_dir = _mainthread_dir / 'task'
    _stat_path = _mainthread_dir / 'stat'

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)

        # Main pid
        self.properties['pid'] = ROProperty(DataType.INTEGER, self._mainpid, desc='Main process id')

        # Memory and load
        self.properties['interval'] = IntervalProperty(self._check, 5., 'Check interval')

        # Threads info
        self.properties['threads_interval'] = IntervalProperty(self._check_threads, 5., 'Check threads interval')

        p = self.properties['virt_mem'] = Property(Output, DataType.BYTES, 0, desc='Virtual memory size', persistent=False)
        self._set_virt_mem = p.get_setvalue_func()

        p = self.properties['res_mem'] = Property(Output, DataType.BYTES, 0, desc='Resident memory size', persistent=False)
        self._set_res_mem = p.get_setvalue_func()

        self._threads = PropertyDict()
        self.properties['threads'] = PropertyDictProperty(self._threads, 'Threads of MainApp')

    def _check(self):
        data = _stat_array(self._stat_path)
        self._set_virt_mem(int(data[20]))
        self._set_res_mem(int(data[21]) * _page_size)

    def _check_threads(self):
        current = {int(t) for t in self._threads}
        python_threadname = {t.native_id: t.name for t in threading.enumerate()}

        if _print_threads:
            print("\n=== Thread info ===")

        for t in self._threads_dir.iterdir():
            pid = int(t.name)

            prop = self._threads.get(str(pid))
            if prop is None:
                # It's a new thread
                prop = self._threads[str(pid)] = ThreadProperty(t, pid == self._mainpid, python_threadname.get(pid))
            else:
                # pid still Exists
                current.remove(pid)

            prop.update_stats()

        # Disappeared threads
        for t in current:
            del self._threads[str(t)]

    def load(self):
        pass

    def unload(self):
        pass
