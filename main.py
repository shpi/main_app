#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import sys
import time
from os import environ
from pathlib import Path

from PySide2.QtCore import qInstallMessageHandler
from PySide2.QtCore import QTimer
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWidgets import QApplication

from core.Appearance import Appearance
from core.Git import Git
from core.HTTPServer import HTTPServer
from core.Logger import qml_log, log_model

from interfaces.Module import ModuleBase, ThreadModuleBase
from core.Module import Module, ThreadModule
from core.ModuleManager import ModuleManager

from core.MLX90615 import MLX90615
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

# Nuitka stuff
import files

APP_PATH = Path(__file__).parent

if environ.get("QMLDEBUG") not in (None, "0"):
    from PySide2.QtQml import QQmlDebuggingEnablers
    debug = QQmlDebuggingEnabler()


def _interrupt_handler(signum, frame):  # signum, frame
    """Handle KeyboardInterrupt: quit application."""
    app.quit()
    app.exit()
    sys.exit(0)


def setup_interrupt_handling():
    """Setup handling of KeyboardInterrupt (Ctrl-C) for PyQt."""
    signal.signal(signal.SIGINT, _interrupt_handler)
    safe_timer(1000, check_loop)  # not below 1000, because timeschedule in input class works with integers


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


# inputs = InputsDict()

core_modules = dict()

core_modules['systeminfo'] = SystemInfo()
core_modules['cpu'] = CPU()
core_modules['iio'] = IIO()
core_modules['leds'] = Led()
core_modules['hwmon'] = HWMon()
core_modules['git'] = Git(APP_PATH)
core_modules['disk'] = DiskStats()
core_modules['inputdevs'] = InputDevs()
core_modules['backlight'] = Backlight()
core_modules['wifi'] = Wifi()

httpserver = core_modules['httpserver'] = ThreadModule(HTTPServer)
httpserver.start()  # Temporary handling until modulemanager works


core_modules['mlx90615'] = MLX90615(Module._inputs)
core_modules['alsamixer'] = AlsaMixer(Module._inputs)


for core_module in core_modules:
    Module._inputs.add(core_modules[core_module].get_inputs())

core_modules['appearance'] = Appearance(Module._inputs)
Module._inputs.add(core_modules['appearance'].get_inputs())

modules = ModuleManager(Module._inputs)


app = QApplication(sys.argv)

QFontDatabase.addApplicationFont("./fonts/dejavu-custom.ttf")

qInstallMessageHandler(qml_log)

app.aboutToQuit.connect(ThreadModule.kill_threadmodules)

app.setApplicationName("Main")
app.setOrganizationName("SHPI GmbH")
app.setOrganizationDomain("shpi.de")

app.setFont(QFont('Dejavu', 11))

engine = QQmlApplicationEngine()
root_context = engine.rootContext()
root_context.setContextProperty("applicationDirPath", str(APP_PATH))
root_context.setContextProperty("logs", log_model)
root_context.setContextProperty("inputs", inputs)
root_context.setContextProperty('wifi', core_modules['wifi'])
root_context.setContextProperty('git', core_modules['git'])
root_context.setContextProperty("appearance", core_modules['appearance'])
root_context.setContextProperty("modules", modules)

setup_interrupt_handling()

engine.load("qrc:/qml/main.qml")

if not engine.rootObjects():
    sys.exit(-1)


exec_returncode = app.exec_()

print(f"Exiting mainapp with code: {exec_returncode}")
sys.exit(exec_returncode)
