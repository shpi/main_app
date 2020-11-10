# This Python file uses the following encoding: utf-8
import time
from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtCore import QAbstractListModel, Property, Signal, QObject


class InputListModel(QAbstractListModel):
    PathRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001
    DescriptionRole = Qt.UserRole + 1002
    TypeRole = Qt.UserRole + 1003
    IntervalRole = Qt.UserRole + 1004
    ExposedRole = Qt.UserRole + 1005

    def __init__(self, parent=None):
        super(InputListModel, self).__init__(parent)
        self.entries = dict()
        self._keys = list()

    def updateKeys(self):
        self._keys = list(self.entries.keys())

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.entries)

    def updateListView(self, key):
        keyindex = self.index(self._keys.index(key))
        self.dataChanged.emit(keyindex, keyindex, [self.ValueRole])

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self.entries[self._keys[index.row()]]
            if role == InputListModel.PathRole:
                return self._keys[index.row()]
            elif role == InputListModel.ValueRole:

                if item["interval"] == 0:
                    return item['call']()
                else:
                    return item["value"]

            elif role == InputListModel.TypeRole:
                return item["type"]
            elif role == InputListModel.DescriptionRole:
                return item["description"]
            elif role == InputListModel.IntervalRole:
                return item["interval"]
            elif role == InputListModel.ExposedRole:
                return item["exposed"]

    def roleNames(self):
        roles = dict()
        roles[InputListModel.PathRole] = b"path"
        roles[InputListModel.ValueRole] = b"value"
        roles[InputListModel.DescriptionRole] = b"description"
        roles[InputListModel.TypeRole] = b"type"
        roles[InputListModel.IntervalRole] = b"invertval"
        roles[InputListModel.ExposedRole] = b"exposed"
        return roles


class InputsDict(QObject):

    def __init__(self, api_key: str = "", parent: QObject = None):
        super(InputsDict, self).__init__(parent)
        self._data = InputListModel()

    @Signal
    def dataChanged(self):
        pass

    @Property(QObject, notify=dataChanged, constant=False)
    def inputList(self):
        return self._data

    @Property("QVariantMap", notify=dataChanged)
    def data(self) -> dict:
        return self._data.entries

    def add(self, newinputs=dict()):
        for key, value in newinputs.items():
            newinputs[key]['lastupdate'] = 0
            newinputs[key]['value'] = 0
            if 'interval' not in value:
                newinputs[key]['interval'] = 5

        self._data.entries.update(newinputs)
        self._data.updateKeys()
        self.update()
        self.dataChanged.emit()

    def update(self):
        for key, value in self._data.entries.items():
            if ('call' in self._data.entries[key] and
               (value['lastupdate'] + value['interval'] < time.time())):

                temp = self._data.entries[key]['call']()
                if (temp != self._data.entries[key]['value']):
                    self._data.entries[key]['value'] = temp
                    self._data.updateListView(key)
                    self._data.entries[key]['lastupdate'] = time.time()
                elif value['lastupdate'] > (time.time() - 2):
                    self._data.updateListView(key)
        self.dataChanged.emit()
