# This Python file uses the following encoding: utf-8
import logging
import os
import signal
import sys
import threading
import time
import shiboken2

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
from core.MQTT import MQTTClient
from core.Alsa import AlsaMixer
from core.Backlight import Backlight
from core.CPU import CPU
from core.Disk import DiskStats
from core.HWMon import HWMon
from core.IIO import IIO
from core.InputDevs import InputDevs
from core.Leds import Led
from core.System import SystemInfo

import files

# from PySide2.QtQml import QQmlDebuggingEnablers

logs = LogModel()
handler = MessageHandler(logs)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(msecs)03d %(module)s - %(funcName)s: %(message)s',
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


def setup_interrupt_handling(with_safe_timer=True):
    """Setup handling of KeyboardInterrupt (Ctrl-C) for PyQt."""
    signal.signal(signal.SIGINT, _interrupt_handler)
    if with_safe_timer:
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


def check_loop(interval: int = None):
    global last_update, ready

    while True:
        if ready:
            ready = False
            inputs.update(last_update)
            last_update = int(time.time())
            ready = True
        if interval is None:
            return

        time.sleep(interval / 1000)


settings = QSettings('settings.ini', QSettings.IniFormat)

core_modules = dict()
core_modules['mqttclient'] = MQTTClient(settings)
inputs = InputsDict(settings, core_modules['mqttclient'])

core_modules['mqttclient'].inputs = inputs

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
#core_modules['bt_xiaomi'] = BT_Xiaomi(inputs, settings)

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
engine.rootContext().setContextProperty("applicationDirPath", os.path.abspath(os.path.dirname(sys.argv[0])))
engine.rootContext().setContextProperty("logs", logs)
engine.rootContext().setContextProperty("inputs", inputs)
engine.rootContext().setContextProperty('wifi', core_modules['wifi'])
engine.rootContext().setContextProperty('git', core_modules['git'])
engine.rootContext().setContextProperty('httpserver', core_modules['httpserver'])
engine.rootContext().setContextProperty("appearance", core_modules['appearance'])
engine.rootContext().setContextProperty("mqttclient", core_modules['mqttclient'])

engine.rootContext().setContextProperty("modules", modules)

qt_check_loop = 'THREAD_STATS' not in sys.argv

setup_interrupt_handling(qt_check_loop)
if not qt_check_loop:
    t = threading.Thread(target=check_loop, name='check_loop', args=(1000,), daemon=True)
    t.start()


engine.load("qrc:/qml/main.qml")
#engine.load("qml/main.qml")

if not engine.rootObjects():
    sys.exit(-1)

if 'THREAD_STATS' in sys.argv:
    from helper.threadinfo import start_own_thread
    t = start_own_thread(5)

sys.exit(app.exec_())
