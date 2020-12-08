import os
import time
from DataTypes import DataType


class Backlight:

    def __init__(self, parent=None):

        super(Backlight, self).__init__()

        backlightpath = "/sys/class/backlight/"
        self.BACKLIGHT = ""
        self.MAX_BACKLIGHT = 0
        self.BL_POWER = 0
        self._brightness = 1
        self.blinputs = dict()
        if os.path.isdir(backlightpath):
            for file in os.listdir(backlightpath):
                if os.path.exists(backlightpath + file + "/brightness"):
                    self.BACKLIGHT = backlightpath + file
                    if os.path.exists(backlightpath + file
                                      + "/max_brightness"):
                        with open(backlightpath + file +
                                  "/max_brightness") as max_backlight:
                            self.MAX_BACKLIGHT = (int)(
                                max_backlight.readline())
                    if os.path.exists(backlightpath + file + "/bl_power"):
                        self.BL_POWER = 1

        self.blinputs['backlight/brightness'] = {"description": 'BL brightness in %',
                                                 "type": DataType.PERCENT_INT,
                                                 "interval": 10,
                                                 "lastupdate": 0,
                                                 "call": self.get_brightness,
                                                 "set": self.set_brightness}

    def get_inputs(self) -> dict:
        return self.blinputs

    def set_brightness(self, brightness):

        if ((len(self.BACKLIGHT) > 0) & (self.MAX_BACKLIGHT > 0)):
            setbrightness = int((self.MAX_BACKLIGHT / 100) * brightness)

            if setbrightness == 0 and brightness > 0:
                setbrightness = 1

            with open(self.BACKLIGHT + "/brightness", "w") as bright:
                bright.write(str(setbrightness))
                self._brightness = brightness
                self.blinputs['backlight/brightness']['value'] = brightness
                self.blinputs['backlight/brightness']['lastupdate'] = time.time()
                bright.close()

            if (self.BL_POWER > 0):
                with open(self.BACKLIGHT + "/bl_power", "w") as bright:
                    if (brightness < 1):
                        bright.write("4")
                    else:
                        bright.write("0")
            bright.close()

    def get_brightness(self):
        if ((len(self.BACKLIGHT) > 0) & (self.MAX_BACKLIGHT > 0)):
            with open(self.BACKLIGHT + "/brightness", "r") as bright:
                self._brightness = int((100 / self.MAX_BACKLIGHT)
                                       * int(bright.readline().rstrip()))
                # if (self._brightness != self.blinputs['backlight/brightness']['value']):
                #self.blinputs['backlight/brightness']['value'] = self._brightness
                #self.blinputs['backlight/brightness']['lastupdate'] = time.time()
        return self._brightness
