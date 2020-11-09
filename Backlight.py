import os
from PySide2.QtCore import QObject, Property,Signal, Slot


class Backlight(QObject):

    def __init__(self):
        QObject.__init__(self)

        backlightpath = "/sys/class/backlight/"
        self.BACKLIGHT = ""
        self.MAX_BACKLIGHT = 0
        self.BL_POWER = 0
        self._brightness = 1
        if os.path.isdir(backlightpath):
            for file in os.listdir(backlightpath):
                if os.path.exists(backlightpath + file + "/brightness"):
                    self.BACKLIGHT = backlightpath + file
                    print("FOUND BACKLIGHT:" + self.BACKLIGHT)
                    if os.path.exists(backlightpath + file
                                      + "/max_brightness"):
                        with open(backlightpath + file +
                             "/max_brightness") as max_backlight:
                             self.MAX_BACKLIGHT = (int)(max_backlight.readline())
                    if os.path.exists(backlightpath + file + "/bl_power"):
                        self.BL_POWER = 1
        #self.set_brightness(0)
        #self.set_brightness(100)

    def get_inputs(self) -> dict:
        blinputs = dict()
        blinputs['backlight/brightness'] = dict({"description" : 'Backlight brightness in %',
        "rights" : 0o644,
        "type" : 'percent',
        "interval" : 0,
        "call" : self.get_brightness})

        return blinputs

    def set_brightness(self, brightness):

        if ((len(self.BACKLIGHT) > 0) & (self.MAX_BACKLIGHT > 0)):
            setbrightness = ((self.MAX_BACKLIGHT / 100) * brightness)

            with open(self.BACKLIGHT + "/brightness","w") as bright:
                bright.write(str(int(setbrightness)))
                self._brightness = brightness
                bright.close()

            if (self.BL_POWER > 0):
                with open(self.BACKLIGHT + "/bl_power","w") as bright:
                    if (brightness < 1):
                        bright.write("4")
                    else:
                        bright.write("0")
            bright.close()
            print(brightness)


    def get_brightness(self):
        if ((len(self.BACKLIGHT) > 0) & (self.MAX_BACKLIGHT > 0)):
            with open(self.BACKLIGHT + "/brightness","r") as bright:
                self._brightness = int((100 / self.MAX_BACKLIGHT) * int(bright.readline().rstrip()))
        return self._brightness


    @Signal
    def brightnessChanged(self):
            pass

    brightness = Property(int, get_brightness, set_brightness, notify=brightnessChanged)





