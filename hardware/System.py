import os
import sys

from core.DataTypes import DataType
from core.Property import EntityProperty, StaticProperty

from interfaces.Module import ModuleBase, ModuleCategories


class SystemInfo(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = "System Info"
    categories = ModuleCategories._INTERNAL, ModuleCategories._AUTOLOAD, ModuleCategories.INFO

    def __init__(self):
        ModuleBase.__init__(self)

        self.properties = []
        # self.name = 'system'

        self.properties.append(StaticProperty(name='is64bit',
                                              category='core',
                                              entity='system',
                                              parent=self,
                                              value=SystemInfo.is64bit(),
                                              description='is 64bit System?',
                                              type=DataType.BOOLEAN,
                                              exposed=False))

        self.properties.append(StaticProperty(name='ram_amount',
                                              category='system',
                                              entity='ram',
                                              parent=self,
                                              value=SystemInfo.ram_amount(),
                                              description='installed ram in MB',
                                              type=DataType.INTEGER,
                                              exposed=False))

        self.properties.append(EntityProperty(name='ram_used',
                                              category='system',
                                              entity='ram',
                                              parent=self,
                                              call=SystemInfo.ram_used,
                                              description='used ram in MB',
                                              type=DataType.INTEGER,
                                              interval=60))

        self.properties.append(EntityProperty(name='ram_free',
                                              category='system',
                                              entity='ram',
                                              parent=self,
                                              call=SystemInfo.ram_free,
                                              description='used ram in MB',
                                              type=DataType.INTEGER,
                                              interval=60))

        self.properties.append(EntityProperty(name='ram_buff',
                                              category='system',
                                              entity='ram',
                                              parent=self,
                                              call=SystemInfo.ram_buff,
                                              description='used ram as buffer in MB',
                                              type=DataType.INTEGER,
                                              interval=60))

        self.properties.append(EntityProperty(name='uptime',
                                              category='core',
                                              entity='system',
                                              parent=self,
                                              call=SystemInfo.get_uptime,
                                              description='uptime in seconds',
                                              type=DataType.INTEGER,
                                              interval=60))

    def get_inputs(self) -> list:
        return self.properties

    def load(self):
        pass

    def unload(self):
        pass

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
