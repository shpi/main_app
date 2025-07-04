import os
from functools import partial

from core.DataTypes import DataType
from core.Property import EntityProperty


class Led:
    name = 'led'
    led_path = "/sys/class/leds/"

    @staticmethod
    def get_inputs():
        properties = []

        if os.path.isdir(Led.led_path):
            for file in os.listdir(Led.led_path):
                if os.path.exists(Led.led_path + file + "/brightness"):

                    with open(Led.led_path + file + "/brightness") as led_brightness:
                        rawvalue = int(led_brightness.readline())

                    if os.path.exists(Led.led_path + file + "/max_brightness"):
                        with open(Led.led_path + file + "/max_brightness") as max_led:
                            lmax = int(max_led.readline())
                            properties.append(EntityProperty(
                                                                  category='output/leds',
                                                                  name=file,
                                                                  min=0,
                                                                  max=100,
                                                                  step=1,
                                                                  description='brightness of led in %',
                                                                  type=DataType.PERCENT_INT,
                                                                  value=100 / lmax * rawvalue,
                                                                  set=partial(Led.set_brightness, file, lmax),
                                                                  call=partial(Led.get_brightness, file, lmax),
                                                                  interval=-1))

        return properties



    @staticmethod
    def set_brightness(file, lmax, brightness):

        setbrightness = int((lmax / 100) * brightness)
        with open(Led.led_path + file + "/brightness", "w") as bright:
            bright.write(str(setbrightness))

    @staticmethod
    def get_brightness(file, lmax):
        with open(Led.led_path + file + "/brightness") as bright:
            pbrightness = int((100 / lmax) * int(bright.readline().rstrip()))
            return pbrightness
