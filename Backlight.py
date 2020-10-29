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
        self.min_brightness = 1
        self.max_brightness = 100
        if os.path.isdir(backlightpath):
            dirs = os.listdir(backlightpath)
            for file in dirs:
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
        return int(self._brightness)


    def set_city(self, city: str) -> None:
         self._city = city
         self.cityChanged.emit()

    def read_city(self):
            return self._city


    @Signal
    def brightnessChanged(self):
            pass

    brightness = Property(int, get_brightness, set_brightness, notify=brightnessChanged)


    @Slot(result=int)
    def get_min_brightness(self):
        return int(self.min_brightness)

    @Slot(result=int)
    def get_max_brightness(self):
        return int(self.max_brightness)

    @Slot(int)
    def set_max_brightness(self, brightness):
        self.max_brightness = brightness
        self.set_brightness(brightness)

    @Slot(int)
    def set_min_brightness(self, brightness):
            self.min_brightness = brightness


