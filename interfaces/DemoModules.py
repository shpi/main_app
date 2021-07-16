from time import sleep

from interfaces.DataTypes import DataType
from interfaces.Module import ThreadModuleBase, ModuleBase
from interfaces.PropertySystem import Property, ModuleInstancePropertyDict


class DemoModule(ModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = "Demo thread module"
    categories = "Demo",

    def __init__(self, parent, instancename: str = None):
        ModuleBase.__init__(self, parent=parent, instancename=instancename)

        self.properties = ModuleInstancePropertyDict(
            a_time_str=Property(DataType.TIME_STR, '10:00', desc='Static TIME_STR property demo')
        )

    def load(self):
        print("Loading...")

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
        print("Loading...")

    def unload(self):
        print("Unload called")

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
