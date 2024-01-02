import os
import sys

from core.DataTypes import DataType
from core.Property import EntityProperty, StaticProperty


class SystemInfo:

    def __init__(self):
        self.properties = list()
        self.name = 'system'

        self.properties.append(StaticProperty(name='is64bit',
                                              category='system',
                                              value=SystemInfo.is64bit(),
                                              description='is 64bit System?',
                                              type=DataType.BOOL,
                                              exposed=False))

        self.properties.append(StaticProperty(name='ram_amount',
                                              category='system',
                                              value=SystemInfo.ram_amount(),
                                              description='installed ram in MB',
                                              type=DataType.INT,
                                              exposed=False))

        self.properties.append(EntityProperty(name='ram_used',
                                              category='system',
                                              call=SystemInfo.ram_used,
                                              description='used ram in MB',
                                              type=DataType.INT,
                                              interval=60))

        self.properties.append(EntityProperty(name='ram_free',
                                              category='system',
                                              call=SystemInfo.ram_free,
                                              description='used ram in MB',
                                              type=DataType.INT,
                                              interval=60))

        self.properties.append(EntityProperty(name='ram_buff',
                                              category='system',
                                              call=SystemInfo.ram_buff,
                                              description='used ram as buffer in MB',
                                              type=DataType.INT,
                                              interval=60))

        self.properties.append(EntityProperty(name='uptime',
                                              category='system',
                                              call=SystemInfo.get_uptime,
                                              description='uptime in seconds',
                                              type=DataType.INT,
                                              interval=60))

    def get_inputs(self) -> list:
        return self.properties

    @staticmethod
    def is64bit():
        return int(sys.maxsize > 2 ** 32)  # is 64bits

    @staticmethod
    def ram_amount():
        # total        used        free      shared  buff/cache   available
        # for future /proc/meminfo
        return int((os.popen('free -m').readlines()[1].split())[1])

    @staticmethod
    def ram_used():
        # total        used        free      shared  buff/cache   available
        # for future /proc/meminfo
        return int((os.popen('free -m').readlines()[1].split())[2])

    @staticmethod
    def ram_buff():
        # total        used        free      shared  buff/cache   available
        # for future /proc/meminfo
        return int((os.popen('free -m').readlines()[1].split())[5])

    @staticmethod
    def ram_free():
        # total        used        free      shared  buff/cache   available
        # for future /proc/meminfo
        return int((os.popen('free -m').readlines()[1].split())[3])

    @staticmethod
    def get_uptime(stat_path='/proc/uptime'):
        if os.path.isfile(stat_path):
            with open(stat_path) as stat_file:
                return int(float(next(stat_file).split()[0]))
