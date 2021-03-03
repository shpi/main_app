import os
import time
from functools import partial
from core.DataTypes import DataType
from core.Property import EntityProperty


class Led:
    ledpath = "/sys/class/leds/"

    def __init__(self):

        self.properties = list()

        if os.path.isdir(Led.ledpath):
            for file in os.listdir(Led.ledpath):
                if os.path.exists(Led.ledpath + file + "/brightness"):

                    with open(Led.ledpath + file + "/brightness") as led_brightness:
                        rawvalue = int(led_brightness.readline())

                    if os.path.exists(Led.ledpath + file + "/max_brightness"):
                        with open(Led.ledpath + file + "/max_brightness") as max_led:
                            max = int(max_led.readline())
                            self.properties.append(EntityProperty(parent=self,
                                                                  category='output',
                                                                  entity='leds',
                                                                  name=file,
                                                                  description='brightness of led in %',
                                                                  type=DataType.PERCENT_FLOAT,
                                                                  value=100 / max * rawvalue,
                                                                  set=partial(self.set_brightness, file, max),
                                                                  call=partial(self.get_brightness, file, max),
                                                                  interval=-1))

    def get_inputs(self) -> list:
        return self.properties

    @staticmethod
    def set_brightness(file, max, brightness):

        setbrightness = int((max / 100) * brightness)
        with open(Led.ledpath + file + "/brightness", "w") as bright:
            bright.write(str(setbrightness))

    @staticmethod
    def get_brightness(file,max):
        with open(Led.ledpath + file + "/brightness") as bright:
            #self.leds[file]['rawvalue'] = int(bright.readline().rstrip())
            pbrightness = int((100 / max) * int(bright.readline().rstrip()))
            return pbrightness
        return 0
