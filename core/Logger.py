# -*- coding: utf-8 -*-

import logging
from PySide2 import QtCore
from PySide2.QtCore import Qt, QModelIndex, QAbstractListModel, Slot
from os import environ


class LogModel(QAbstractListModel):
    def __init__(self, items=None):
        # QAbstractListModel.__init__(self)
        super().__init__()

        if items is None:
            self._items = []
        else:
            self._items = items

        self.roles = {
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
        self._items.remove(self._items[row])
        self.endRemoveRows()

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            return self._items[index.row()].get(self.roles[role], '')

        return ''

    def roleNames(self):
        return self.roles


class QtWarningHandler(logging.Handler):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.setLevel(logging.WARNING)

    def emit(self, record):
        self.format(record)
        self.model.appendRow({b'levelno': record.levelno,
                              b'msg': f'{record.module} - {record.funcName}: {record.msg}',
                              b'levelname': record.levelname,
                              b'asctime': record.asctime})


log_model = LogModel()
qt_warning_handler = QtWarningHandler(log_model)


logging.basicConfig(
    level=logging.DEBUG if environ.get("DEBUG") not in (None, "0") else logging.WARNING,
    format='%(asctime)s.%(msecs)03d %(module)s - %(funcName)s: %(message)s',
    datefmt='%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("debug.log"),
        qt_warning_handler
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
