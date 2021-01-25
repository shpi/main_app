import logging
from PySide2.QtCore import Qt, QModelIndex, QAbstractListModel, Property, Signal, Slot, QObject


class LogModel(QAbstractListModel):


    def __init__(self, parent=None):
        super(LogModel, self).__init__()
        self.items = []

        self.roles = {
            257: b"threadName",
            258: b"name",
            259: b"thread",
            260: b"created",
            261: b"process",
            262: b"processName",
            263: b"args",
            264: b"module",
            265: b"filename",
            266: b"levelno",
            267: b"exc_text",
            268: b"pathname",
            269: b"lineno",
            270: b"msg",
            271: b"exc_info",
            272: b"funcName",
            273: b"relativeCreated",
            274: b"levelname",
            275: b"msecs",
            276: b"asctime"
        }



    def addItem(self, item):
        self.beginInsertRows(QModelIndex(),
                             self.rowCount(),
                             self.rowCount())

        self.items.append(item.__dict__)
        self.endInsertRows()
        if len(self.items) > 100:
            self.removeRows(0)


    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.items)

    def removeRows(self, row, parent=QModelIndex()):
         self.beginRemoveRows(parent, row, row)
         self.items.remove(self.items[row])
         self.endRemoveRows()


    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():

            item = self.items[index.row()]

            if role in self.roles:
                return item.get(self.roles[role].decode(), '')

        return ''

    def roleNames(self):
        return self.roles


class MessageHandler(logging.Handler):

    def __init__(self, model, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.model = model

    def emit(self, record):
        self.model.addItem(record)



