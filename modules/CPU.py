# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Dict, List

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import Property, Function, IntervalProperty, PropertyDictProperty, PropertyDict, Output


class CPU(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = 'CPU info'
    categories = 'Sensors', 'Temperature', 'Hardware'

    CPU_PATH = Path('/sys/devices/system/cpu')
    STAT_PATH = Path('/proc/stat')
    UPTIME_PATH = Path('/proc/uptime')
    LOAD_PATH = Path('/proc/loadavg')
    CPU_TEMP_PATH = Path('/sys/class/thermal/thermal_zone0/temp')

    _cpu_count = os.cpu_count()

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)

        if self.CPU_PATH.exists():
            self._freq_files: Dict[str, Path] = \
                {file.parent.parent.name: file for file in self.CPU_PATH.glob('cpu*/cpufreq/scaling_cur_freq')}

            if 'cpu0' in self._freq_files:
                # At least one core
                self._cpu0 = self._freq_files['cpu0']
                self.properties['cpu_freq'] = Property(Function, DataType.FREQUENCY, self.get_cpu_freq,
                                                       desc='CPU frequency', function_poll_min_def=(5, 30))

        if self.LOAD_PATH.exists():
            self.properties['cpu_load_interval'] = IntervalProperty(self._read_cpu_load, 5., 'Interval for reading cpu_load')

            pd = PropertyDict()
            self.properties['cpu_load'] = PropertyDictProperty(pd, 'Average CPU load')

            p1 = pd['last_1_min'] = Property(Output, DataType.FLOAT, 0., desc='CPU load (last 1 minute)', persistent=False)
            p2 = pd['last_5_min'] = Property(Output, DataType.FLOAT, 0., desc='CPU load (last 5 minutes)', persistent=False)
            p3 = pd['last_15_min'] = Property(Output, DataType.FLOAT, 0., desc='CPU load (last 15 minutes)', persistent=False)

            loads_props = p1, p2, p3
            self._set_cpu_load_funcs = tuple(p.get_setvalue_func() for p in loads_props)
            for p in loads_props:
                p._floatprec_default = 2

        if self.CPU_TEMP_PATH.exists():
            self.properties['cpu_temp'] = Property(Function, DataType.TEMPERATURE, self.get_cpu_temp,
                                                   desc='CPU temperature', function_poll_min_def=(1, 5))

    def load(self):
        pass

    def unload(self):
        pass

    def _read_cpu_load(self):
        load_info = self.LOAD_PATH.read_text().split()
        for i in range(3):
            self._set_cpu_load_funcs[i](float(load_info[i]) / self._cpu_count)

    def get_cpu_freq(self) -> int:
        """
        This function seems to be very slow, use with care
        """
        return int(self._cpu0.read_text()) * 1000

    # we will use this later and dont use os!
    @classmethod
    def get_cpu_seconds(cls) -> List[float]:
        if not cls.STAT_PATH.is_file():
            return [0.]

        with cls.STAT_PATH.open(encoding="ascii") as stat_file:
            line1_str_array = next(stat_file).split()[1:]
            return [int(seconds) / 100 for seconds in line1_str_array]

    def get_cpu_temp(self) -> float:
        return float(self.CPU_TEMP_PATH.read_text()) / 1000
