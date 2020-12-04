# This Python file uses the following encoding: utf-8
import os

os.environ["QT_WAYLAND_FORCE_DPI"] = "128"
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
#os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
#os.environ["QT_QPA_PLATFORM"] = "eglfs"
#os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/usr/local/qt5pi/plugins/platforms"
#os.environ["LD_LIBRARY_PATH"]= "/usr/local/qt5pi/lib"
#os.environ["GST_DEBUG"] = "omx:4"
#os.environ["QT_QPA_EGLFS_PHYSICAL_WIDTH"] = "85"
#os.environ["QT_QPA_EGLFS_PHYSICAL_HEIGHT"] = "51"
#os.environ["XDG_RUNTIME_DIR"] = "/home/pi/qmlui"

import signal
import sys
import logging
import time

from PySide2.QtCore import Qt, QTimer, QUrl
from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine

from Backlight import Backlight
from Appearance import Appearance
from Weather import WeatherWrapper
from HWMon import HWMon
from Inputs import InputsDict
from InputDevs import InputDevs
from System import SystemInfo
from Leds import Led
from Alsa import AlsaMixer
from Wifi import Wifi
from Shutter import Shutter

from IIO import IIO

logging.basicConfig(
    # filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


def setup_interrupt_handling():
    """Setup handling of KeyboardInterrupt (Ctrl-C) for PyQt."""
    signal.signal(signal.SIGINT, _interrupt_handler)
    """Timer"""
    safe_timer(3000, check_loop)

# Define this as a global function to make sure it is not garbage
# collected when going out of scope:


def _interrupt_handler(signum, frame):
    """Handle KeyboardInterrupt: quit application."""
    app.quit()
    app.exit()
    sys.exit()


def safe_timer(timeout, func, *args, **kwargs):
    """
    Create a timer that is safe against garbage collection and overlapping
    calls.
    """
    def timer_event():
        try:
            func(*args, **kwargs)
        finally:
            QTimer.singleShot(timeout, timer_event)
    QTimer.singleShot(timeout, timer_event)


""" Loop for checking logic regularly """

lastupdate = time.time()


def check_loop():
    global lastupdate
    weather[0].update()
    SystemInfo.update()
    alsamixer.update()
    appearance.update()
    wifi.update()
    inputs.update(lastupdate)
    lastupdate = time.time()


settings = QSettings()
weather = []
weather.append(WeatherWrapper('weather', settings))
backlight = Backlight()
hwmon = HWMon()
inputs = InputsDict()
try:
    iio = IIO()
except:
    pass

leds = Led()
alsamixer = AlsaMixer(settings)
wifi = Wifi(settings)
inputs.add(wifi.get_inputs())
try:
    inputs.add(iio.get_inputs())
except:
     pass

inputs.add(alsamixer.get_inputs())
inputs.add(leds.get_inputs())
inputs.add(hwmon.get_inputs())
inputdevs = InputDevs()
inputs.add(inputdevs.inputs)
inputs.add(backlight.get_inputs())
inputs.add(SystemInfo.get_inputs())

appearance = Appearance(inputs,settings)
shutter = Shutter(inputs, settings)

for subweather in weather:
    inputs.add(subweather.get_inputs())


if __name__ == "__main__":

    app = QApplication(sys.argv)
    #app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setApplicationName("Main")
    app.setOrganizationName("SHPI GmbH")
    app.setOrganizationDomain("shpi.de")

    engine = QQmlApplicationEngine()

    engine.rootContext().setContextProperty("inputs", inputs)
    engine.rootContext().setContextProperty('weather', weather)
    engine.rootContext().setContextProperty('wifi', wifi)
    engine.rootContext().setContextProperty('shutter2', shutter)
    engine.rootContext().setContextProperty("appearance", appearance)

    setup_interrupt_handling()

    filename = os.path.join(os.path.dirname(
                            os.path.realpath(__file__)), "qml/main.qml")

    engine.load(QUrl.fromLocalFile(filename))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
