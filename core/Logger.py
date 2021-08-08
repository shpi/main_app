# -*- coding: utf-8 -*-

import logging
import sys
import traceback
from typing import Any, Union

from PySide2 import QtCore
from PySide2.QtCore import Qt, QModelIndex, QAbstractListModel, Slot


def get_logging_level() -> int:
    if "DEBUG" in sys.argv:
        return logging.DEBUG

    if "INFO" in sys.argv:
        return logging.INFO

    if "WARNING" in sys.argv:
        return logging.WARNING

    if "ERROR" in sys.argv:
        return logging.INFO

    if "CRITICAL" in sys.argv:
        return logging.CRITICAL

    # Default
    return logging.INFO


class LogModel(QAbstractListModel):
    roles = {
        # 257: b"threadName",
        # 258: b"name",
        # 259: b"thread",
        # 260: b"created",
        # 261: b"process",
        # 262: b"processName",
        # 263: b"args",
        # 264: b"module",
        # 265: b"filename",
        Qt.UserRole + 266: b"levelno",
        # 267: b"exc_text",
        # 268: b"pathname",
        # 269: b"lineno",
        Qt.UserRole + 270: b"msg",
        # 271: b"exc_info",
        # 272: b"funcName",
        # 273: b"relativeCreated",
        Qt.UserRole + 274: b"levelname",
        # 275: b"msecs",
        Qt.UserRole + 276: b"asctime"
    }

    def __init__(self):
        super().__init__()
        self._items = []

    def rowCount(self, parent=None) -> int:
        # if parent.isValid():
        #    return 0
        return len(self._items)

    def appendRow(self, item):
        row = len(self._items)

        self.beginInsertRows(QModelIndex(), row, row)
        self._items.append(item)  # .__dict__)
        self.endInsertRows()

        # while len(self._items) > 10:
        #    self.removeRows(0)

    @Slot(int)
    def removeRows(self, row, parent=None):
        self.beginRemoveRows(parent, row, row)
        del self._items[row]
        self.endRemoveRows()

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            return self._items[index.row()].get(self.roles[role], '')

        return ''

    def roleNames(self):
        return self.roles

    def unload(self):
        self._items.clear()
        self.deleteLater()

    # def __del__(self):
    #    print("deleted LogModel")


class QtLoggingHandler(logging.Handler):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model  # qtinstance
        self.setLevel(get_logging_level())

        self._msg_formatter = logging.Formatter(fmt='%(message)s')
        self.setFormatter(self._msg_formatter)

    def emit(self, record):
        formatted_msg = self.format(record)

        self.model.appendRow(
            {
                b'levelno': record.levelno,
                b'msg': f'{record.module} - {record.funcName}: {formatted_msg}',
                b'levelname': record.levelname,
                b'asctime': record.asctime
            }
        )

    def unload(self):
        # print("Unloading QtLoggingHandler")
        self.emit = lambda x: None
        self.model = None

    def close(self):
        # print("closing handler")
        super().close()
        self.unload()

    # def __del__(self):
    #    print("deleted QtLoggingHandler")


log_model = LogModel()
qtlogginghandler = QtLoggingHandler(log_model)

logging.basicConfig(
    level=get_logging_level(),
    format='%(asctime)s.%(msecs)03d %(levelname)s @%(threadName)s [%(module)s:%(funcName)s()]: %(message)s',
    datefmt='%d.%m. %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        qtlogginghandler,
        # logging.FileHandler("debug.log"),
    ]
)

qml_logger = logging.getLogger("QML")
_message_mapping = {
    QtCore.QtInfoMsg: qml_logger.info,
    QtCore.QtWarningMsg: qml_logger.warning,
    QtCore.QtCriticalMsg: qml_logger.critical,
    QtCore.QtFatalMsg: qml_logger.error,
}


def qt_message_handler(mode, context, message):
    _message_mapping.get(mode, qml_logger.debug)("%s (%d, %s)", message, context.line, context.file)


force_stacktrace = 'STACKTRACE' in sys.argv


class LogCall:
    """
    Runs a function and writes exceptions to the given logger.

    Usage:

    import logging
    from core.Logger import LogCall
    logger = logging.getLogger(__name__)
    logcall = LogCall(logger)

    logcall(func, errmsg="Something went wrong: %s")
    """
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def __call__(self,
                 func,
                 *args,
                 errmsg="Exception during calling function: %s",
                 stack_trace=False,
                 catch_exceptions=(Exception,),
                 **kwargs) -> Union[Any, BaseException]:

        try:
            ret = func(*args, **kwargs)
            return ret
        except catch_exceptions as e:
            msg = ('\n'.join(line.strip() for line in traceback.format_stack()[:-1])).replace('%', '%%') + '\n' + \
                  'While calling: %s'
            self._logger.error(msg + '\n' + errmsg, repr(func), repr(e), exc_info=True)
            return e
