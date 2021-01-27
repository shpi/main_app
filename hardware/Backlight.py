import os
import logging
import time
from core.DataTypes import DataType


class Backlight:

    def __init__(self):

        super(Backlight, self).__init__()

        backlightpath = "/sys/class/backlight/"

        self.BACKLIGHT = ""
        self.MAX_BACKLIGHT = 0
        self.BL_POWER = 0
        self._brightness = 1
        self.module_inputs = dict()
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

        self.module_inputs['backlight/brightness'] = {"description": 'BL brightness in %',
                                                      "type": DataType.PERCENT_INT,
                                                      "interval": 10,
                                                      "lastupdate": 0,
                                                      "call": self.get_brightness,
                                                      "set": self.set_brightness}

    def delete_inputs(self):
        del self.module_inputs  # does this delete references in inputs?

    def get_inputs(self) -> dict:
        return self.module_inputs

    def set_brightness(self, brightness):

        # logging.debug("set_brightness({brightness})")

        if ((len(self.BACKLIGHT) > 0) & (self.MAX_BACKLIGHT > 0)):
            setbrightness = int((self.MAX_BACKLIGHT / 100) * brightness)

            if setbrightness == 0 and brightness > 0:
                setbrightness = 1

            # logging.debug("hardware brightness level: {setbrightness}")

            if self.BL_POWER > 0:
                try:
                    with open(self.BACKLIGHT + "/bl_power", "w") as bright:
                        if brightness < 1:
                            bright.write("4")
                            # logging.debug(f"bl_power: 4")
                        else:
                            bright.write("0")
                            # logging.debug(f"bl_power: 0")
                except Exception as e:
                    logging.error(str(e))

            try:
                with open(self.BACKLIGHT + "/brightness", "w") as bright:
                    bright.write(str(setbrightness))
                    self._brightness = brightness
                    self.module_inputs['backlight/brightness']['value'] = brightness
                    self.module_inputs['backlight/brightness']['lastupdate'] = time.time()
            except Exception as e:
                logging.error(str(e))

    def get_brightness(self):
        if (len(self.BACKLIGHT) > 0) & (self.MAX_BACKLIGHT > 0):
            with open(self.BACKLIGHT + "/brightness", "r") as bright:
                self._brightness = int((100 / self.MAX_BACKLIGHT)
                                       * int(bright.readline().rstrip()))
        return self._brightness
