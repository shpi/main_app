# This Python file uses the following encoding: utf-8
from hardware.IIO import IIO
from hardware.Wifi import Wifi
from hardware.Alsa import AlsaMixer
from hardware.Leds import Led
from hardware.System import SystemInfo
from hardware.InputDevs import InputDevs
from hardware.HWMon import HWMon
from hardware.Backlight import Backlight
from core.ModuleManager import ModuleManager
from core.Inputs import InputsDict
from core.Appearance import Appearance
from core.HTTPServer import HTTPServer
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QSettings
from PySide2.QtCore import QTimer, QUrl
import time
import logging
import sys
import signal
import os


os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# os.environ["QT_QPA_PLATFORM"] = "eglfs"
# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/usr/local/qt5pi/plugins/platforms"
# os.environ["LD_LIBRARY_PATH"]= "/usr/local/qt5pi/lib"
# os.environ["GST_DEBUG"] = "omx:4"
# os.environ["QT_QPA_EGLFS_PHYSICAL_WIDTH"] = "85"
# os.environ["QT_QPA_EGLFS_PHYSICAL_HEIGHT"] = "51"
# os.environ["XDG_RUNTIME_DIR"] = "/home/pi/qmlui"


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
    safe_timer(1000, check_loop)

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

    systeminfo.update()
    appearance.update()

    #wifi.update()

    inputs.update(lastupdate)

    lastupdate = time.time()
    modules.update()

systeminfo = SystemInfo()
settings = QSettings("SHPI GmbH", "Main")
backlight = Backlight()
hwmon = HWMon()
inputs = InputsDict(settings)
httpserver = HTTPServer(inputs, settings)

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
inputs.add(inputdevs.get_inputs())
inputs.add(backlight.get_inputs())
inputs.add(systeminfo.get_inputs())

appearance = Appearance(inputs, settings)
modules = ModuleManager(inputs, settings)

def KillThreads():
    for key in inputs.entries:
        if key.endswith('thread'):
            inputs.entries[key]['set'](0)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(KillThreads)
    app.setApplicationName("Main")
    app.setOrganizationName("SHPI GmbH")
    app.setOrganizationDomain("shpi.de")

    engine = QQmlApplicationEngine()

    engine.rootContext().setContextProperty("inputs", inputs)
    engine.rootContext().setContextProperty('wifi', wifi)
    engine.rootContext().setContextProperty("appearance", appearance)
    engine.rootContext().setContextProperty("modules", modules)

    # 'available' -> for ENUM datatype, list of option for dropdown box
    # 'lastupdate' -> lastupdate
    # 'call' -> for get actual sensor value
    # 'step', 'min', 'max'  -> for integer slides
    # 'value' -> cached sensor value
    # 'thread' -> thread for input devices
    # 'type' -> datatype of sensor
    # 'description' -> description
    # 'set' -> outputs have set function
    # 'interrupts' -> for input devices, could be reworked to events for multipurpose
    # 'interval'  -> #  1 =  update through class, 0 =  one time,  > 0 = update throug  call function
    """
    print('<tr>')
    print('<td>key</td>')
    print('<td>description</td>')
    print('<td>lastupdate</td>')
    print('<td>value</td>')
    print('<td>type</td>')
    print('<td>set</td>')
    print('<td>call</td>')
    print('<td>interval</td>')
    print('<td>available</td>')
    print('<td>min</td>')
    print('<td>max</td>')
    print('<td>step</td>')
    print('</tr>')

    for key, value in inputs.entries.items():
        print('<tr>')
        print('<td>' + key + '</td>')
        print('<td>' + str(value.get('description', '')) + '</td>')
        print('<td>' + str(value.get('lastupdate', '')) + '</td>')
        print('<td>' + str(value.get('value', '')) + '</td>')
        print('<td>' + str(value.get('type', '')) + '</td>')
        print('<td>' + str(value.get('set', '')) + '</td>')
        print('<td>' + str(value.get('call', '')) + '</td>')
        print('<td>' + str(value.get('interval', '')) + '</td>')
        print('<td>' + str(value.get('available', '')) + '</td>')
        print('<td>' + str(value.get('min', '')) + '</td>')
        print('<td>' + str(value.get('max', '')) + '</td>')
        print('<td>' + str(value.get('step', '')) + '</td>')

        print('</tr>')

    """
    setup_interrupt_handling()

    filename = os.path.join(os.path.dirname(
                            os.path.realpath(__file__)), "qml/main.qml")

    engine.load(QUrl.fromLocalFile(filename))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
