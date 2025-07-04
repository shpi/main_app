import os
import sys
import glob
import shutil

from core.DataTypes import DataType
from core.Property import EntityProperty, StaticProperty


class SystemInfo:
    name = 'system'

    _properties = None

    @staticmethod
    def get_inputs():
        if SystemInfo._properties is None:
            SystemInfo._properties = [
                StaticProperty(
                    name='is64bit',
                    category='system',
                    value=int(sys.maxsize > 2 ** 32),
                    description='is 64bit System?',
                    type=DataType.BOOL,
                    exposed=False
                ),
                StaticProperty(
                    name='ram_amount',
                    category='system',
                    value=SystemInfo.ram_amount(),
                    description='installed ram in MB',
                    type=DataType.INT,
                    exposed=False
                ),
                EntityProperty(
                    name='ram_used',
                    category='system',
                    call=lambda: SystemInfo.ram_used(),
                    description='used ram in MB',
                    type=DataType.INT,
                    interval=60
                ),
                EntityProperty(
                    name='ram_free',
                    category='system',
                    call=lambda: SystemInfo.ram_free(),
                    description='used ram in MB',
                    type=DataType.INT,
                    interval=60
                ),
                EntityProperty(
                    name='ram_buff',
                    category='system',
                    call=lambda: SystemInfo.ram_buff(),
                    description='used ram as buffer in MB',
                    type=DataType.INT,
                    interval=60
                ),
                EntityProperty(
                    name='uptime',
                    category='system',
                    call=lambda: SystemInfo.get_uptime(),
                    description='uptime in seconds',
                    type=DataType.INT,
                    interval=60
                ),
                EntityProperty(
                    name='cpu_load',
                    category='system',
                    call=lambda: SystemInfo.cpu_usage(),
                    description='CPU usage %',
                    type=DataType.PERCENT_INT,
                    interval=10
                ),
                EntityProperty(
                                category='system',
                                name='disk_usage',
                                description='disk usage',
                                type=DataType.INT,
                                call=SystemInfo.disk_used,
                                interval=600
                ),
                StaticProperty(
                               category='system',
                               name='disk_size',
                               value=SystemInfo.disk_total(),
                               description='disk total size',
                               type=DataType.INT)

            ]
        return SystemInfo._properties

    @staticmethod
    def ram_amount():
        return int((os.popen('free -m').readlines()[1].split())[1])

    @staticmethod
    def ram_used():
        return int((os.popen('free -m').readlines()[1].split())[2])

    @staticmethod
    def ram_buff():
        return int((os.popen('free -m').readlines()[1].split())[5])

    @staticmethod
    def ram_free():
        return int((os.popen('free -m').readlines()[1].split())[3])


    @staticmethod
    def disk_total():
        # total used free
        # /proc/properties for io rates
        return list(shutil.disk_usage("/"))[0]

    @staticmethod
    def disk_used():
        # total used free
        # /proc/properties for io rates
        return list(shutil.disk_usage("/"))[1]


    @staticmethod
    def get_uptime(stat_path='/proc/uptime'):
        if os.path.isfile(stat_path):
            with open(stat_path) as stat_file:
                return int(float(next(stat_file).split()[0]))
        return 0

    @staticmethod
    def get_cpu_freq():
        cpu_freq = 0
        for cpu in glob.iglob('/sys/devices/system/cpu/cpu[0-9]*'):
            path = cpu + '/cpufreq/scaling_cur_freq'
            if os.path.isfile(path):
                with open(path) as cpu_file:
                    cpu_freq += int(next(cpu_file).rstrip())
        return cpu_freq

    @staticmethod
    def cpu_usage():
        try:
            return int(os.getloadavg()[0] / os.cpu_count() * 100)
        except:
            return 0

    @staticmethod
    def get_cpu_seconds(stat_path='/proc/stat'):
        if os.path.isfile(stat_path):
            with open(stat_path) as stat_file:
                return next(stat_file).split()[1:]
        return []
