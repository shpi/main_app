#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import sys
from os import environ
from pathlib import Path
from logging import getLogger
from typing import Dict, Optional, Any

from PySide2.QtCore import qInstallMessageHandler
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtQml import QQmlApplicationEngine

from interfaces.MainApp import MainAppBase
from core.Logger import qt_message_handler, log_model
from modules.ModuleManager import Modules

# Qt resources
import qtres

logger = getLogger(__name__)

if environ.get("QMLDEBUG") not in (None, "0"):
    from PySide2.QtQml import QQmlDebuggingEnabler
    debug = QQmlDebuggingEnabler()


class MainApp(MainAppBase):
    applicationDirPath = Path(sys.argv[0]).parent.resolve()

    _main_instance: Optional["MainApp"] = None

    def __init__(self):
        if self._main_instance is not None:
            raise ValueError('MainApp has already been instantiated.')

        self.__class__._main_instance = self

        MainAppBase.__init__(self, sys.argv)

        signal.signal(signal.SIGINT, self._interrupt_handler)
        self.aboutToQuit.connect(MainApp.unload)

        self.setApplicationName("Main")
        self.setOrganizationName("SHPI GmbH")
        self.setOrganizationDomain("shpi.de")
        self.setFont(QFont('Dejavu', 11))

        # Load "everything"

        self.engine = QQmlApplicationEngine()
        Modules.selfload(self)
        self.engine.load("qrc:/qml/main.qml")

        if not self.engine.rootObjects():
            sys.exit(-1)

    def qml_context_properties(self) -> Dict[str, Any]:
        return {
            'applicationDirPath': str(self.applicationDirPath),
            'logs': log_model,
        }

    @classmethod
    def unload(cls):
        print("unload")
        if cls._main_instance is None:
            return

        mapp = cls._main_instance
        print("deleteing engine")
        del mapp.engine
        print("deleteted engine")

        print("modules.shutdown()")
        mapp.modules.shutdown()

        print("del modules")
        del mapp.modules
        cls._main_instance = None

    def _interrupt_handler(self, signum, frame):  # signum, frame
        """Handle KeyboardInterrupt: quit application."""
        print("interrupt_handler called")
        self.quit()  # trigger quit slot
        self.exit()  # exit eventloop (app.exec)


if __name__ == '__main__':
    # Create main app
    app = MainApp()

    QFontDatabase.addApplicationFont("fonts/dejavu-custom.ttf")
    qInstallMessageHandler(qt_message_handler)

    # Run event loop
    print("Starting mainloop")
    exec_returncode = app.exec_()
    print("mainloop exited")
    # main app exited.

    app.unload()
    del app

    if exec_returncode:
        logger.warning('Exiting mainapp with code: %s', exec_returncode)

    sys.exit(exec_returncode)
