#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import sys
from os import environ
from pathlib import Path

from PySide2.QtCore import qInstallMessageHandler
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWidgets import QApplication

from core.Appearance import Appearance
from core.Git import Git
from core.HTTPServer import HTTPServer
from core.Logger import qml_log, log_model
from core.Toolbox import RepeatingTimer

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


check_loop_timer = RepeatingTimer(1000, Module.check_loop, autostart=False)


def setup_interrupt_handling():
    """Setup handling of KeyboardInterrupt (Ctrl-C) for PyQt."""
    signal.signal(signal.SIGINT, _interrupt_handler)
    check_loop_timer.start()
    # safe_timer(1000, Module.check_loop)  # not below 1000, because timeschedule in input class works with integers


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
httpserver.load()  # Temporary handling until modulemanager works


core_modules['mlx90615'] = MLX90615(Module.inputs)
core_modules['alsamixer'] = AlsaMixer(Module.inputs)


for mod_str, core_module in core_modules.items():
    if not isinstance(core_module, ThreadModule):
        Module.inputs.add(core_module.get_inputs())


core_modules['appearance'] = Appearance(Module.inputs)
Module.inputs.add(core_modules['appearance'].get_inputs())

modules = ModuleManager(Module.inputs)


app = QApplication(sys.argv)

QFontDatabase.addApplicationFont("./fonts/dejavu-custom.ttf")

qInstallMessageHandler(qml_log)

app.aboutToQuit.connect(Module.unload_modules)

app.setApplicationName("Main")
app.setOrganizationName("SHPI GmbH")
app.setOrganizationDomain("shpi.de")

app.setFont(QFont('Dejavu', 11))

engine = QQmlApplicationEngine()
root_context = engine.rootContext()
root_context.setContextProperty("applicationDirPath", str(APP_PATH))
root_context.setContextProperty("logs", log_model)
root_context.setContextProperty("inputs", Module.inputs)
root_context.setContextProperty('wifi', core_modules['wifi'])
root_context.setContextProperty('git', core_modules['git'])
root_context.setContextProperty("appearance", core_modules['appearance'])
root_context.setContextProperty("modules", modules)

setup_interrupt_handling()

engine.load("qrc:/qml/main.qml")

if not engine.rootObjects():
    sys.exit(-1)


exec_returncode = app.exec_()

check_loop_timer.stop()

print(f"Exiting mainapp with code: {exec_returncode}")
sys.exit(exec_returncode)
