import os
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
                            lmax = int(max_led.readline())
                            self.properties.append(EntityProperty(
                                                                  category='output/leds',
                                                                  name=file,
                                                                  min=0,
                                                                  max=100,
                                                                  step=1,
                                                                  description='brightness of led in %',
                                                                  type=DataType.PERCENT_INT,
                                                                  value=100 / lmax * rawvalue,
                                                                  set=partial(self.set_brightness, file, lmax),
                                                                  call=partial(self.get_brightness, file, lmax),
                                                                  interval=-1))

    def get_inputs(self) -> list:
        return self.properties

    @staticmethod
    def set_brightness(file, lmax, brightness):

        setbrightness = int((lmax / 100) * brightness)
        with open(Led.ledpath + file + "/brightness", "w") as bright:
            bright.write(str(setbrightness))

    @staticmethod
    def get_brightness(file, lmax):
        with open(Led.ledpath + file + "/brightness") as bright:
            # self.leds[file]['rawvlalue'] = int(bright.readline().rstrip())
            pbrightness = int((100 / lmax) * int(bright.readline().rstrip()))
            return pbrightness
