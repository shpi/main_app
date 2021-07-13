# This Python file uses the following encoding: utf-8
import logging
import os
import signal
import sys
import time

from PySide2 import QtCore
from PySide2.QtCore import QSettings, qInstallMessageHandler
from PySide2.QtCore import QTimer
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWidgets import QApplication

from core.Appearance import Appearance
from core.Git import Git
from core.HTTPServer import HTTPServer
from core.Inputs import InputsDict
from core.Logger import LogModel, MessageHandler
from core.MLX90615 import MLX90615
from core.ModuleManager import ModuleManager
from core.Wifi import Wifi
from hardware.Alsa import AlsaMixer
from hardware.Backlight import Backlight
from hardware.CPU import CPU
from hardware.Disk import DiskStats
from hardware.HWMon import HWMon
from hardware.IIO import IIO
from hardware.InputDevs import InputDevs
from hardware.Leds import Led
from hardware.System import SystemInfo

import files

# from PySide2.QtQml import QQmlDebuggingEnablers

logs = LogModel()
handler = MessageHandler(logs)

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d %(module)s - %(funcName)s: %(message)s',
    datefmt='%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("debug.log"),
        handler
    ]
)


def qml_log(mode, context, message):
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
    safe_timer(1000, check_loop)  # not below 1000, because timeschedule in input class works with integers


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

last_update = 0  # to initialize everything
ready = True


def check_loop():
    global last_update, ready

    if ready:
        ready = False
        inputs.update(last_update)
        last_update = int(time.time())
        ready = True


settings = QSettings('settings.ini', QSettings.IniFormat)
inputs = InputsDict(settings)

core_modules = dict()

core_modules['systeminfo'] = SystemInfo()
core_modules['cpu'] = CPU()
core_modules['iio'] = IIO()
core_modules['leds'] = Led()
core_modules['hwmon'] = HWMon()
core_modules['git'] = Git(settings)
core_modules['disk'] = DiskStats()
core_modules['inputdevs'] = InputDevs()
core_modules['backlight'] = Backlight()
core_modules['wifi'] = Wifi(settings)
core_modules['httpserver'] = HTTPServer(inputs, settings)
core_modules['mlx90615'] = MLX90615(inputs, settings)
core_modules['alsamixer'] = AlsaMixer(inputs, settings)


for core_module in core_modules:
    inputs.add(core_modules[core_module].get_inputs())

core_modules['appearance'] = Appearance(inputs, settings)

inputs.add(core_modules['appearance'].get_inputs())

modules = ModuleManager(inputs, settings)


def killThreads():
    for key in inputs.entries:
        if key.endswith('thread'):
            inputs.entries[key].set(0)

    httpserver.server.shutdown()
    httpserver.server_thread.join()


# debug = QQmlDebuggingEnabler()


app = QApplication(sys.argv)

QFontDatabase.addApplicationFont("./fonts/dejavu-custom.ttf")

qInstallMessageHandler(qml_log)

app.aboutToQuit.connect(killThreads)
app.setApplicationName("Main")
app.setOrganizationName("SHPI GmbH")
app.setOrganizationDomain("shpi.de")

app.setFont(QFont('Dejavu', 11))

engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty("applicationDirPath", os.path.abspath(os.path.dirname(sys.argv[0])));
engine.rootContext().setContextProperty("logs", logs)
engine.rootContext().setContextProperty("inputs", inputs)
engine.rootContext().setContextProperty('wifi', core_modules['wifi'])
engine.rootContext().setContextProperty('git', core_modules['git'])
engine.rootContext().setContextProperty("appearance", core_modules['appearance'])
engine.rootContext().setContextProperty("modules", modules)

setup_interrupt_handling()

# filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "qml/main.qml")
engine.load("qrc:/qml/main.qml")
#engine.load("qml/main.qml")

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec_())
