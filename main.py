# This Python file uses the following encoding: utf-8
import logging
import os
import signal
import sys
import time
from subprocess import check_output

from PySide2 import QtCore
from PySide2.QtCore import QSettings, qInstallMessageHandler
from PySide2.QtCore import QTimer, QUrl
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWidgets import QApplication

from core.Appearance import Appearance
from core.HTTPServer import HTTPServer
from core.Inputs import InputsDict
from core.ModuleManager import ModuleManager
from hardware.Alsa import AlsaMixer
from hardware.Backlight import Backlight
from hardware.HWMon import HWMon
from hardware.IIO import IIO
from hardware.InputDevs import InputDevs
from hardware.Leds import Led
from hardware.System import SystemInfo
from hardware.Wifi import Wifi
from core.Logger import LogModel, MessageHandler

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

if check_output(['uname', '-m']).startswith(b'armv6'):
    os.environ["QT_QPA_PLATFORM"] = "eglfs"
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/usr/local/qt5pi/plugins/platforms"
    os.environ["LD_LIBRARY_PATH"] = "/usr/local/qt5pi/lib"
    os.environ["GST_DEBUG"] = "omx:4"
    os.environ["QT_QPA_EGLFS_FORCE888"] = "1"
    # os.environ["QT_QPA_EGLFS_PHYSICAL_WIDTH"] = "85"
    # os.environ["QT_QPA_EGLFS_PHYSICAL_HEIGHT"] = "51"
    # os.environ["XDG_RUNTIME_DIR"] = "/home/pi/qmlui"


logs = LogModel()
handler = MessageHandler(logs)

logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s.%(msecs)03d %(module)s - %(funcName)s: %(message)s',
                datefmt='%m-%d %H:%M:%S',
                handlers=[
                        logging.FileHandler("debug.log"),
                        handler , logging.StreamHandler()
                    ]
            )


def qml_error(mode, context, message):
    if mode == QtCore.QtInfoMsg:
        logging.info("%s (%d, %s)" % (message, context.line, context.file))
    elif mode == QtCore.QtWarningMsg:
        logging.warning("%s (%d, %s)" % (message, context.line, context.file))
    elif mode == QtCore.QtCriticalMsg:
        logging.critical("%s (%d, %s)" % (message, context.line, context.file))
    elif mode == QtCore.QtFatalMsg:
        logging.error("%s (%d, %s)" % (message, context.line, context.file))
    else:
        logging.debug("%s (%d, %s)" % (message, context.line, context.file))


def setup_interrupt_handling():
    """Setup handling of KeyboardInterrupt (Ctrl-C) for PyQt."""
    signal.signal(signal.SIGINT, _interrupt_handler)
    safe_timer(1000, check_loop)


def _interrupt_handler(signum, frame):  # signum, frame
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

last_update = 0 # to initialize everything
ready = True


def check_loop():
    global last_update, ready

    if ready:
        ready = False
        inputs.update(last_update)
        last_update = int(time.time())
        ready = True


settings = QSettings("SHPI GmbH", "Main")
inputs = InputsDict(settings)
systeminfo = SystemInfo()
iio = IIO()
leds = Led()
hwmon = HWMon()
inputdevs = InputDevs()
backlight = Backlight()
wifi = Wifi(settings)
httpserver = HTTPServer(inputs, settings)
alsamixer = AlsaMixer(inputs, settings)
inputs.add(iio.get_inputs())
inputs.add(wifi.get_inputs())
inputs.add(leds.get_inputs())
inputs.add(hwmon.get_inputs())
inputs.add(inputdevs.get_inputs())
inputs.add(systeminfo.get_inputs())
inputs.add(backlight.get_inputs())

appearance = Appearance(inputs, settings)
inputs.add(appearance.get_inputs())

modules = ModuleManager(inputs, settings)

def killThreads():
    for key in inputs.entries:
        if key.endswith('thread'):
            inputs.entries[key]['set'](0)

    httpserver.server.shutdown()
    httpserver.server_thread.join()

app = QApplication(sys.argv)
qInstallMessageHandler(qml_error)
app.aboutToQuit.connect(killThreads)
app.setApplicationName("Main")
app.setOrganizationName("SHPI GmbH")
app.setOrganizationDomain("shpi.de")

engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty("logs", logs)
engine.rootContext().setContextProperty("inputs", inputs)
engine.rootContext().setContextProperty('wifi', wifi)
engine.rootContext().setContextProperty("appearance", appearance)
engine.rootContext().setContextProperty("modules", modules)


setup_interrupt_handling()

filename = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "qml/main.qml")

engine.load(QUrl.fromLocalFile(filename))

if not engine.rootObjects():
        sys.exit(-1)

sys.exit(app.exec_())
