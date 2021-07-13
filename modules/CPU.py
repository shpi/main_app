# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Dict, List

from interfaces.DataTypes import DataType
from interfaces.Module import ModuleBase
from interfaces.PropertySystem import ModuleInstancePropertyDict, FunctionProperty


class CPU(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = 'CPU info'
    categories = 'Sensors', 'Temperature', 'Hardware'

    CPU_PATH = Path('/sys/devices/system/cpu')
    STAT_PATH = Path('/proc/stat')
    CPU_TEMP_PATH = Path('/sys/class/thermal/thermal_zone0/temp')

    def __init__(self, parent, instancename: str = None):
        super().__init__(parent=parent, instancename=instancename)

        self.properties = ModuleInstancePropertyDict()

        if self.CPU_PATH.exists():
            self._freq_files: Dict[str, Path] = \
                {file.parent.parent.name: file for file in self.CPU_PATH.glob('cpu*/cpufreq/scaling_cur_freq')}

            if 'cpu0' in self._freq_files:
                # At least one core
                self._cpu0 = self._freq_files['cpu0']
                self.properties["cpu_freq"] = \
                    FunctionProperty(DataType.INTEGER, self.get_cpu_freq, maxage=1., desc='CPU frequency')

        self.properties["cpu_load"] = \
            FunctionProperty(DataType.PERCENT_FLOAT, self.get_cpu_load, maxage=1., desc='CPU usage (core average)')

        self.properties["cpu_temp"] = \
            FunctionProperty(DataType.TEMPERATURE, self.get_cpu_temp, maxage=1., desc='CPU temperature')

    def load(self):
        pass

    def unload(self):
        pass

    def get_cpu_freq(self) -> int:
        """
        This function seems to be very slow, use with care
        """
        return int(self._cpu0.read_text().strip())

    @staticmethod
    def get_cpu_load() -> float:
        # /proc/loadavg maybe better for processcount
        return os.getloadavg()[0] / os.cpu_count() * 100

    # we will use this later and dont use os!
    @classmethod
    def get_cpu_seconds(cls) -> List[float]:
        if not cls.STAT_PATH.is_file():
            return [0.]

        with cls.STAT_PATH.open(encoding="ascii") as stat_file:
            line1_str_array = next(stat_file).split()[1:]
            return [int(seconds) / 100 for seconds in line1_str_array]

    if CPU_TEMP_PATH.is_file():
        # Temp path available
        @classmethod
        def get_cpu_temp(cls) -> float:
            return int(cls.CPU_TEMP_PATH.read_text().strip()) / 1000

    else:
        # No cpu temp available
        @staticmethod
        def get_cpu_temp() -> float:
            # Dummy function for speedup
            return 0.
