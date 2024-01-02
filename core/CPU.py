import glob
import os

from core.DataTypes import DataType
from core.Property import EntityProperty


class CPU:

    def __init__(self):

        self.properties = list()

        """
        we don't need that 

        self.properties.append(EntityProperty(name='cpu_freq',
                                              category='core',
                                              entity='cpu',
                                              
                                              call=CPU.get_cpu_freq,
                                              description='CPU freq sum over all cores (slow function)',
                                              type=DataType.INT,
                                              interval=60))
        """

        self.properties.append(EntityProperty(name='cpu_load',
                                              category='system',
                                              call=CPU.cpu_usage,
                                              description='CPU usage %',
                                              type=DataType.PERCENT_INT,
                                              interval=10))

    def get_inputs(self) -> list:
        return self.properties

    @staticmethod
    def get_cpu_freq():
        """
        This function seems to be very slow, use with care
        """
        cpu_freq = 0
        # if os.path.isdir('/sys/devices/system/cpu/'):
        for cpu in glob.iglob('/sys/devices/system/cpu/cpu*'):
            if os.path.isfile(cpu + '/cpufreq/scaling_cur_freq'):
                with open(cpu + '/cpufreq/scaling_cur_freq') as cpu_file:
                    cpu_freq += int(next(cpu_file).rstrip())
        return cpu_freq

    @staticmethod
    def cpu_usage():
        # /proc/loadavg maybe better for processcount
        return int(os.getloadavg()[0] / os.cpu_count() * 100)

    # we will use this later and dont use os!
    @staticmethod
    def get_cpu_seconds(stat_path='/proc/stat'):
        if os.path.isfile(stat_path):
            with open(stat_path) as stat_file:
                return next(stat_file).split()[1:]
