from time import sleep
from datetime import time

from interfaces.DataTypes import DataType
from interfaces.Module import ThreadModuleBase, ModuleBase
from interfaces.PropertySystem import Property, ModuleInstancePropertyDict, Input


class DemoModule(ModuleBase):
    allow_maininstance = False
    allow_instances = True
    description = "Demo thread module (multi instances)"
    categories = "Demo",

    def __init__(self, parent, instancename: str = None):
        ModuleBase.__init__(self, parent=parent, instancename=instancename)

        self.properties = ModuleInstancePropertyDict(
            a_time_str=Property(Input, DataType.TIME, time(20, 0), desc='Static TIME property demo')
        )

    def load(self):
        print("Loading another instance...")

    def unload(self):
        print("Unload called")


class DemoThreadModule(ThreadModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = "Demo thread module"
    categories = "Demo",

    def __init__(self, parent, instancename: str = None):
        ThreadModuleBase.__init__(self, parent=parent, instancename=instancename)

    def load(self):
        print("Loading module", self.modulename(), self.instancename())

    def unload(self):
        pass

    def run(self):
        print("Start thread")

        while self.sleep(10):
            print("Hello from thread with instancename:", self.instancename())

        print("Exit thread")

    def stop(self):
        print("Stop called")


class EndlessThreadModule(DemoThreadModule):
    description = "Demo thread module with endless loop"

    def run(self):
        print("Starting endless thread")

        while True:
            sleep(5)
            print("Hello from thread with instancename:", self.instancename())

        # I don't want to stop! Kill me if you can!
