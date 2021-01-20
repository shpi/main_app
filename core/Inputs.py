# -*- coding: utf-8 -*-

import time
import threading
import logging
from PySide2.QtCore import Qt, QModelIndex, QSortFilterProxyModel
from PySide2.QtCore import QAbstractListModel, Property, Signal, Slot, QObject
from core.DataTypes import Convert
from core.DataTypes import DataType
from PySide2.QtCore import QPointF
import sys


class InputListModel(QAbstractListModel):
    PathRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001
    DescriptionRole = Qt.UserRole + 1002
    TypeRole = Qt.UserRole + 1003
    IntervalRole = Qt.UserRole + 1004
    ExposedRole = Qt.UserRole + 1005
    OutputRole = Qt.UserRole + 1006
    LoggingRole = Qt.UserRole + 1007

    def __init__(self, dictionary, parent=None):
        super(InputListModel, self).__init__(parent)
        self.entries = dictionary
        self._keys = list(self.entries.keys())

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
            try:
                if role == InputListModel.PathRole:
                    return self._keys[index.row()]
                elif role == InputListModel.ValueRole:
                    return item["value"]
                elif role == InputListModel.OutputRole:
                    return '1' if ('set' in item) else '0'
                elif role == InputListModel.TypeRole:
                    return Convert.type_to_str(item["type"])
                elif role == InputListModel.DescriptionRole:
                    return item["description"]
                elif role == InputListModel.IntervalRole:
                    return item["interval"]
                elif role == InputListModel.ExposedRole:
                    return item["exposed"]
                elif role == InputListModel.LoggingRole:
                    if 'logging' in item:
                        return item["logging"]
                    else:
                        return 0
                else:
                    return 'unknown role'
            except Exception as e:
                print(e)
                print(item)

    def roleNames(self):
        roles = dict()
        roles[InputListModel.PathRole] = b"path"
        roles[InputListModel.ValueRole] = b"value"
        roles[InputListModel.DescriptionRole] = b"description"
        roles[InputListModel.TypeRole] = b"type"
        roles[InputListModel.IntervalRole] = b"interval"
        roles[InputListModel.ExposedRole] = b"exposed"
        roles[InputListModel.OutputRole] = b"output"
        roles[InputListModel.LoggingRole] = b"logging"
        return roles


class InputsDict(QObject):
    def __init__(self, settings = None):
        super(InputsDict, self).__init__()
        self.settings = settings
        self.entries = dict()
        self.buffer = dict()

        self.timerschedule = dict()

        self.completelist = InputListModel(self.entries)

        self.outputs = QSortFilterProxyModel()
        self.outputs.setSourceModel(self.completelist)
        self.outputs.setFilterRole(self.completelist.OutputRole)
        self.outputs.setFilterFixedString('1')

        self.outputssearch = QSortFilterProxyModel()
        self.outputssearch.setSourceModel(self.outputs)
        self.outputssearch.setFilterRole(self.completelist.TypeRole)
        self.outputssearch.setFilterFixedString('')

        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.completelist)
        self.proxy.setFilterRole(self.completelist.TypeRole)
        self.proxy.setFilterFixedString('')

        self.search = QSortFilterProxyModel()
        self.search.setSourceModel(self.completelist)
        self.search.setFilterRole(self.completelist.PathRole)
        self.search.setFilterFixedString('')
        # proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)

    @Signal
    def dataChanged(self):
        pass

    @Property(QObject, notify=dataChanged)
    def inputList(self):
        self.completelist.filter = None
        return self.completelist

    @Property(QObject, notify=dataChanged)
    def outputList(self):
        return self.outputssearch

    @Property(QObject, notify=dataChanged)
    def typeList(self):
        return self.proxy

    @Property(QObject, notify=dataChanged)
    def searchList(self):
        return self.search

    @Slot(str)
    def set_typeList(self, type_):
        self.proxy.setFilterFixedString(type_)

    @Slot(str)
    def set_outputList(self, type_):
        self.outputssearch.setFilterFixedString(type_)

    @Slot(str, result=int)
    def getIndex(self, path):
        return self.completeList._keys.index(path)

    @Slot(str)
    def set_searchList(self, type_):
        self.search.setFilterFixedString(type_)

    # Workaround for https://bugreports.qt.io/browse/PYSIDE-1426
    # @Property('QVariantMap', constant=True)  # , notify=dataChanged)
    def data(self) -> dict:
        return self.entries
    data = Property('QVariantMap', data, constant=True)

    def register_timerschedule(self, key, interval):
        interval = int(interval)
        if interval not in self.timerschedule:
            self.timerschedule[interval] = list()

        self.timerschedule[interval].append(key)


    def delete_timerschedule(self,key, interval):
        if int(interval) in self.timerschedule:
            if key in self.timerschedule[interval]:
                self.timerschedule[interval].remove(key)


    def add(self, newinputs=None):
        if newinputs is None:
            newinputs = {}

        for key in list(newinputs):

            newinputs[key]['logging'] = bool(int(self.settings.value(key + "/logging", 0)))
            if newinputs[key]['logging']:
                self.buffer[key] = list()

            newinputs[key]['exposed'] = bool(int(self.settings.value(key + "/exposed", 0)))

            if 'lastupdate' not in newinputs[key]:
                newinputs[key]['lastupdate'] = 0
            if 'value' not in newinputs[key]:
                newinputs[key]['value'] = 0
            if 'call' in newinputs[key]:
                newinputs[key]['interval'] = int(self.settings.value(key + "/interval", newinputs[key].get('interval', 60)))

            if newinputs[key]['interval'] != 0:
                self.register_timerschedule(key, newinputs[key]['interval'])


            # following lines are inserted to make it possible to update values from another class
            # without removing dict memory adress of introducing class. for example:
            # adding [interrupts] in InputsDevs from another class

            if key in self.entries:
                for subkey in list(newinputs[key]):  # like lastupdate
                    if subkey in self.entries[key]:

                        if type(self.entries[key][subkey]) is list:
                            self.entries[key][subkey].append(
                                newinputs[key][subkey])
                            print(f'{key} {subkey} {newinputs[key][subkey]}')
                        else:
                            self.entries[key][subkey] = newinputs[key][subkey]
                    else:
                        self.entries[key][subkey] = newinputs[key][subkey]
                del newinputs[key] # ??

        self.entries.update(newinputs)
        self.completelist.updateKeys()
        self.dataChanged.emit()

        # 'available' -> for ENUM datatype, list of option for dropdown box
        # 'lastupdate' -> lastupdate
        # 'call' -> for get actual sensor value
        # 'step', 'min', 'max'  -> for integer slides
        # 'value' -> cached sensor value
        # 'thread' -> thread for input devices
        # 'type' -> datatype of sensor
        # 'description' -> description
        # 'set' -> outputs have set function
        # 'interrupts' -> for input devices, could be reworked to events for multipurpose
        # 'interval'  -> #  -1 =  update through class, 0 =  one time,  > 0 = update throug  call function

    @Slot(str, result='QVariantList')
    @Slot(str, 'long', result='QVariantList')
    def get_points(self, key, start = None):
        #print(len(self.buffer[key]))
        #print(sys.getsizeof(self.buffer[key]))
        if start is not None:

            i = 0
            for subpoint in self.buffer[key]:

                if subpoint[0] > start:
                    break
                else:
                    i += 1
            #return self.buffer[key][i:]
            return [QPointF(*v) for v in self.buffer[key][i:]]
            #return p = [QPointF(*v) for v in filter(lambda x: x[0] > start, self.buffer[key])]
        else:
            #return self.buffer[key]
            return [QPointF(*v) for v in self.buffer[key]]


    @Slot(str, int)
    def set_interval(self, key, value):
        logging.debug('set_interval ' + key + ' ' + str(value))
        try:
            self.delete_timerschedule(key, self.entries[key]['interval'])
            self.entries[key]['interval'] = int(value)
            self.register_timerschedule(key, int(value))
            self.settings.setValue(key + "/interval", value)
        except KeyError:
            logging.debug(key + ' not in Inputdictionary')


    @Slot(str, bool)
    def set_logging(self, key, value):
        logging.debug('set_logging ' + key + ' ' + str(value))
        try:
            self.entries[key]['logging'] = bool(value)
            self.settings.setValue(key + "/logging", int(value))
            if value and key not in self.buffer:
               self.buffer[key] = list()
        except KeyError:
            logging.debug(key + ' not in Inputdictionary')

    @Slot(str, bool)
    def set_exposed(self, key, value):
        logging.debug('set_exposed ' + key + ' ' + str(value))
        try:
            self.entries[key]['exposed'] = bool(value)

            self.settings.setValue(key + "/exposed", int(value))

        except KeyError:
            logging.debug(key + ' not in Inputdictionary')


    def update(self, lastupdate):

        for key in self.timerschedule[-1]:
            value = self.entries[key]
            if value['lastupdate'] > lastupdate:
                self.completelist.updateListView(key)
                if value['logging'] > 0:
                    self.buffer[key].append((value['lastupdate'], value['value']))

                    # just for now, to avoid overflows
                    if len(self.buffer[key]) > 30000:
                        self.buffer[key] = self.buffer[key][10000:]

        for timeinterval in self.timerschedule:

            if timeinterval != -1 and lastupdate % timeinterval == 0:

                for key in self.timerschedule[timeinterval]:

                    if (key.startswith('http')):
                        if 'updatethread' not in self.entries[key] or not self.entries[key]['updatethread'].is_alive():
                            self.entries[key]['updatethread'] = (threading.Thread(target=self.update_value, args=(key,)))
                            self.entries[key]['updatethread'].start()
                    else:
                        self.update_value(key)

        # self.dataChanged.emit() needs too many ressources

    def update_value(self, key, value=None):
        if value is None:
            value = self.entries[key]

        if 'call' in self.entries[key]:
            temp = self.entries[key]['call']()
            if temp != value['value']:
                self.entries[key]['value'] = temp
                self.completelist.updateListView(key)
            self.entries[key]['lastupdate'] = time.time()

            if self.entries[key]['logging'] > 0:
                self.buffer[key].append((self.entries[key]['lastupdate'], self.entries[key]['value']))

                # just for now, to avoid overflows
                if len(self.buffer[key]) > 30000:
                    self.buffer[key] = self.buffer[key][10000:]



    @Slot(str, str)
    def set(self, key, value):
        print('set:' + key + ':' + value)
        if key in self.entries and 'set' in self.entries[key]:
            if self.entries[key]['type'] == DataType.PERCENT_INT:
                self.entries[key]['set'](float(value))
            elif self.entries[key]['type'] == DataType.INT:
                self.entries[key]['set'](int(value))
            elif self.entries[key]['type'] == DataType.BOOL:
                self.entries[key]['set'](int(value))
            elif self.entries[key]['type'] == DataType.ENUM:
                self.entries[key]['set'](int(value))
