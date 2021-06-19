from time import sleep

from interfaces.Module import ThreadModuleBase, ModuleCategories


class DemoThreadModule(ThreadModuleBase):
    allow_maininstance = True
    allow_instances = True
    description = "Demo thread module"
    categories = (ModuleCategories.USER_MODULE, )

    def __init__(self, parent, instancename: str = None):
        ThreadModuleBase.__init__(self, parent=parent, instancename=instancename)

    def load(self):
        print("Loading...")

    def run(self):
        print("Start thread")

        while self.sleep(10):
            print("Hello from thread with instancename:", self.instancename())

        print("Exit thread")

    def stop(self):
        print("Stop called")

    def unload(self):
        print("Unload called")

    def get_inputs(self) -> list:
        return []


class EndlessThreadModule(DemoThreadModule):
    description = "Demo thread module with endless loop"

    def run(self):
        print("Starting endless thread")

        while True:
            sleep(5)
            print("Hello from thread with instancename:", self.instancename())

        # I don't want to stop! Kill me if you can!
