import os
import time
from functools import partial

class Led:

    def __init__(self,  parent=None):

        super(Led, self).__init__()

        self.ledpath = "/sys/class/leds/"

        self.inputs = dict()
        self.leds = dict()

        if os.path.isdir(self.ledpath):
            for file in os.listdir(self.ledpath):
                if os.path.exists(self.ledpath + file + "/brightness"):
                    self.leds[file] = dict()
                    self.inputs['leds/' + file] = dict()
                    self.inputs['leds/' + file]['description'] = 'brightness of led in %'
                    self.inputs['leds/' + file]['type'] = 'percent'

                    with open(self.ledpath + file + "/brightness") as led_brightness:
                         self.leds[file]['rawvalue'] = (int)(led_brightness.readline())

                    if os.path.exists(self.ledpath + file
                                      + "/max_brightness"):
                        with open(self.ledpath + file +
                             "/max_brightness") as max_led:
                             self.leds[file]['max'] = (int)(max_led.readline())
                             self.inputs['leds/' + file]['steps'] = self.leds[file]['max']
                             self.inputs['leds/' + file]['value'] = 100 / self.leds[file]['max'] * self.leds[file]['rawvalue']
                             self.inputs['leds/' + file]['lastupdate'] = time.time()
                             self.inputs['leds/' + file]['interval'] = -1
                             self.inputs['leds/' + file]['call'] = partial(self.get_brightness, file)
                             self.inputs['leds/' + file]['set'] = partial(self.set_brightness, file)


    def get_inputs(self) -> dict:
        return self.inputs


    def set_brightness(self,file, brightness):

            setbrightness = int((self.leds[file]['max'] / 100) * brightness)

            with open(self.ledpath + file + "/brightness", "w") as bright:
                bright.write(str(setbrightness))
                self.leds[file]['rawvalue'] = setbrightness
                self.inputs['leds/' + file]['value'] = brightness
                self.inputs['leds/' + file]['lastupdate'] = time.time()
                bright.close()



    def get_brightness(self,file):
        with open(self.ledpath + file + "/brightness", "w") as bright:
                self.leds[file]['rawvalue'] = int(bright.readline().rstrip())
                self.inputs['leds/' + file]['value'] = int((100 / self.leds[file]['max'])
                                       * self.leds[file]['rawvalue'] )

        return self.inputs['leds/' + file]['value']

