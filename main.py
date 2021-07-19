#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import faulthandler
import logging
import os
import signal
import sys
import threading
from pathlib import Path
from logging import getLogger
from typing import Dict, Optional, Any

from PySide2.QtCore import qInstallMessageHandler
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtQml import QQmlApplicationEngine

from interfaces.MainApp import MainAppBase
from core.Logger import qt_message_handler, log_model, get_logging_level, LogCall
from interfaces.PropertySystem import properties_early_stop
from modules.ModuleManager import Modules

faulthandler.enable()

# Qt resources
import qtres

logger = getLogger(__name__)
logcall = LogCall(logger)


if get_logging_level() <= logging.DEBUG:
    from PySide2.QtQml import QQmlDebuggingEnabler
    debug = QQmlDebuggingEnabler()

SCRIPT_PATH = Path(sys.argv[0]).parent.resolve()

in_event_loop = None


class MainApp(MainAppBase):
    applicationDirPath = SCRIPT_PATH

    _main_instance: Optional["MainApp"] = None

    def __init__(self):
        if self._main_instance is not None:
            raise ValueError('MainApp has already been instantiated.')

        self.__class__._main_instance = self

        MainAppBase.__init__(self, sys.argv)

        signal.signal(signal.SIGINT, self._interrupt_handler)
        # self.aboutToQuit.connect(MainApp.unload)

        self.setApplicationName("Main")
        self.setOrganizationName("SHPI GmbH")
        self.setOrganizationDomain("shpi.de")
        self.setFont(QFont('Dejavu', 11))

        self.engine = QQmlApplicationEngine()
        # Load "everything"
        Modules.selfload(self)

        self.engine.load("qrc:/qml/main.qml")

        if not self.engine.rootObjects():
            self.unload()
            raise RuntimeError("QML failed")

    def qml_context_properties(self) -> Dict[str, Any]:
        return {
            'applicationDirPath': str(self.applicationDirPath),
            'logs': log_model,
        }

    @classmethod
    def unload(cls):
        if cls._main_instance is None:
            return

        logcall(properties_early_stop)

        mapp = cls._main_instance
        if hasattr(mapp, 'engine'):
            del mapp.engine
        else:
            logger.warning('Did not find the qml engine instance in MainApp.')

        Modules.shutdown()

        cls._main_instance = None

    def _interrupt_handler(self, signum, frame):  # signum, frame
        """Handle KeyboardInterrupt: quit application."""
        print("interrupt_handler called")
        if in_event_loop:
            self.quit()  # trigger quit slot
            self.exit()  # exit eventloop (app.exec)
        else:
            sys.exit(1)


if __name__ == '__main__':
    # Change working directory to location of main.py or executable
    os.chdir(SCRIPT_PATH)

    exec_returncode = 0

    # Create main app
    try:
        app = MainApp()

        QFontDatabase.addApplicationFont("fonts/dejavu-custom.ttf")
        qInstallMessageHandler(qt_message_handler)

        # Run event loop
        in_event_loop = True
        exec_returncode = app.exec_()
        in_event_loop = False

        # main app exited.
        logger.info("mainloop exited")

        app.unload()
        del app

        if exec_returncode:
            logger.warning('Exiting mainapp with code: %s', exec_returncode)

    except Exception as e:
        logger.critical('Could not load MainApp: %s', repr(e))

    for t in tuple(threading.enumerate()):
        if t is not threading.current_thread():
            logger.warning("Remaining Thread: %s", t.name)

    sys.exit(exec_returncode)
