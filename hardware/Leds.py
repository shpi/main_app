import os
import time
from functools import partial
from core.DataTypes import DataType


class Led:

    def __init__(self):

        super(Led, self).__init__()

        self.ledpath = "/sys/class/leds/"

        self.inputs = dict()
        self.leds = dict()

        if os.path.isdir(self.ledpath):
            for file in os.listdir(self.ledpath):
                if os.path.exists(self.ledpath + file + "/brightness"):

                    with open(self.ledpath + file + "/brightness") as led_brightness:
                        self.leds[file] = dict()
                        self.leds[file]['rawvalue'] = (
                            int)(led_brightness.readline())

                    if os.path.exists(self.ledpath + file
                                      + "/max_brightness"):
                        with open(self.ledpath + file +
                                  "/max_brightness") as max_led:
                            self.leds[file]['max'] = int(max_led.readline())
                            self.inputs['leds/' + file] = {
                                'description': 'brightness of led in %',
                                'type': DataType.PERCENT_FLOAT,
                                'min': 0,
                                'max': self.leds[file]['max'],
                                'value': 100 / self.leds[file]['max'] * self.leds[file]['rawvalue'],
                                'lastupdate': time.time(),
                                'interval': 60,
                                'call': partial(self.get_brightness, file),
                                'set': partial(self.set_brightness, file)}

    def get_inputs(self) -> dict:
        return self.inputs

    def set_brightness(self, file, brightness):

        setbrightness = int((self.leds[file]['max'] / 100) * brightness)

        with open(self.ledpath + file + "/brightness", "w") as bright:
            bright.write(str(setbrightness))
            self.leds[file]['rawvalue'] = setbrightness
            self.inputs['leds/' + file]['value'] = brightness
            self.inputs['leds/' + file]['lastupdate'] = time.time()


    def get_brightness(self, file):
        with open(self.ledpath + file + "/brightness") as bright:
            self.leds[file]['rawvalue'] = int(bright.readline().rstrip())
            pbrightness = int((100 / self.leds[file]['max'])
                              * self.leds[file]['rawvalue'])
            self.inputs['leds/' + file]['value'] = pbrightness
            self.inputs['leds/' + file]['lastupdate'] = time.time()

        return pbrightness
