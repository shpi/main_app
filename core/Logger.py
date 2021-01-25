import logging
from PySide2.QtCore import Qt, QModelIndex, QAbstractListModel, Property, Signal, Slot, QObject




class LogModel(QAbstractListModel):


    def __init__(self, items = []):
        super(LogModel, self).__init__()

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



    def appendRow(self, item):
        self.beginInsertRows(QModelIndex(),
                             self.rowCount(),
                             self.rowCount())
        self._items.append(item) #.__dict__)
        self.endInsertRows()

        #if len(self._items) > 100:
        #    self.removeRows(0)





    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._items)

    @Slot(int)
    def removeRows(self, row, parent=QModelIndex()):
         self.beginRemoveRows(parent, row, row)
         self._items.remove(self._items[row])
         self.endRemoveRows()


    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():

            item = self._items[index.row()]

            if role in self.roles:
                return item.get(self.roles[role], '')

        return ''

    def roleNames(self):
        return self.roles


class MessageHandler(logging.Handler):


    def __init__(self, model, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.model = model

    def emit(self, record):

        self.model.appendRow({b'levelno': record.levelno,
                            b'msg': record.msg,
                            b'levelname': record.levelname,
                            b'asctime': record.asctime})



