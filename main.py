#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import sys
from os import environ
from pathlib import Path
from logging import getLogger

from PySide2.QtCore import qInstallMessageHandler
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtQml import QQmlApplicationEngine

from interfaces.MainApp import MainAppBase
from core.Appearance import Appearance
from core.Git import Git
from core.HTTPServer import HTTPServer
from core.Logger import qt_message_handler, log_model
from core.Module import Module, ThreadModule
from core.ModuleManager import ModuleManager

# Qt resources
import files

logger = getLogger(__name__)

if environ.get("QMLDEBUG") not in (None, "0"):
    from PySide2.QtQml import QQmlDebuggingEnabler
    debug = QQmlDebuggingEnabler()


QFontDatabase.addApplicationFont("qrc:/fonts/dejavu-custom.ttf")
qInstallMessageHandler(qt_message_handler)


class MainApp(MainAppBase):
    def __init__(self):
        MainAppBase.__init__(self, sys.argv)

        self.APP_PATH = Path(sys.argv[0]).parent.resolve()
        signal.signal(signal.SIGINT, self.interrupt_handler)

        self.setApplicationName("Main")
        self.setOrganizationName("SHPI GmbH")
        self.setOrganizationDomain("shpi.de")
        self.setFont(QFont('Dejavu', 11))
        self.aboutToQuit.connect(self._unload)

        self.modulemanager = ModuleManager(self)

        self.engine = QQmlApplicationEngine()
        root_context = self.engine.rootContext()
        root_context.setContextProperty("applicationDirPath", str(self.APP_PATH))
        root_context.setContextProperty("logs", log_model)

        # root_context.setContextProperty("inputs", Module.inputs)
        root_context.setContextProperty('wifi', core_modules['wifi'])
        root_context.setContextProperty('git', core_modules['git'])
        root_context.setContextProperty("appearance", core_modules['appearance'])
        # root_context.setContextProperty("modules", modules)

        self.engine.load("qrc:/qml/main.qml")
        if not self.engine.rootObjects():
            sys.exit(-1)

    def _unload(self):
        Module.unload_modules()
        del self.engine

    def interrupt_handler(self, signum, frame):  # signum, frame
        """Handle KeyboardInterrupt: quit application."""
        self.quit()
        self.exit()
        sys.exit(0)


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

core_modules['httpserver'] = ThreadModule(HTTPServer)
# core_modules['demo'] = ThreadModule(DemoThreadModule, "EasyThread")
# core_modules['demo2'] = ThreadModule(EndlessThreadModule, "EndlessThread")

core_modules['mlx90615'] = ThreadModule(MLX90615)
core_modules['alsamixer'] = AlsaMixer(Module.inputs)


core_modules['appearance'] = Appearance()
Module.inputs.add(core_modules['appearance'].get_inputs())

if __name__ == '__main__':
    # Create main app
    app = MainApp()
    exec_returncode = app.exec_()
    # main app exited.

    if exec_returncode:
        logger.warning(f"Exiting mainapp with code: {exec_returncode}")

    sys.exit(exec_returncode)
