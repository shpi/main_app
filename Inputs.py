# This Python file uses the following encoding: utf-8

from PySide2.QtCore  import QByteArray, Qt, QModelIndex,QAbstractListModel, Property, Signal, Slot, QObject
import typing
import logging
import os


class InputListModel(QAbstractListModel):
    PathRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001
    DescriptionRole = Qt.UserRole + 1002
    TypeRole = Qt.UserRole + 1003
    IntervalRole = Qt.UserRole + 1004
    ExposedRole = Qt.UserRole + 1005

    def __init__(self, entries=dict(), parent=None):
        super(InputListModel, self).__init__(parent)
        self._entries = entries
        self._keys = list()
        self.updateKeys()

    def updateKeys(self):
        self._keys = list(self._entries.keys())
        print(self._keys)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self._entries[self._keys[index.row()]]
            if role == InputListModel.PathRole:
                return self._keys[index.row()]
            elif role == InputListModel.ValueRole:
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

        def __init__(self, api_key: str ="", parent: QObject = None):
            super(InputsDict, self).__init__(parent)

            self._data = dict()
            self._list = InputListModel(self._data)

        @Signal
        def inputsChanged(self):
            pass

        @Property(QObject, notify=inputsChanged)
        def inputList(self):
            return self._list

        @Property("QVariantMap", notify=inputsChanged)
        def data(self) -> dict:
            return self._data

        def add(self, newinputs=dict()):
            self._data.update(newinputs)

            self._list.updateKeys()
            self.inputsChanged.emit()
            #print(self._data)



