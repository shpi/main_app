# -*- coding: utf-8 -*-

from PySide2.QtCore import QModelIndex, QSortFilterProxyModel
from PySide2.QtCore import QAbstractListModel, Property, Signal, Slot, QObject
from core.DataTypes import Convert
from core.DataTypes import DataType
from core.CircularBuffer import CircularBuffer
from PySide2.QtGui import QPolygonF
from PySide2.QtCore import QPointF
from PySide2.QtCore import QDateTime, Qt
import shiboken2
import ctypes
import logging
import numpy as np
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
    AvailableRole = Qt.UserRole + 1008
    MinRole = Qt.UserRole + 1009
    MaxRole = Qt.UserRole + 1010
    StepRole = Qt.UserRole + 1011

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
                    return str(item.value)
                elif role == InputListModel.OutputRole:
                    return item.is_output
                elif role == InputListModel.TypeRole:
                    return Convert.type_to_str(item.type)
                elif role == InputListModel.DescriptionRole:
                    return item.description
                elif role == InputListModel.IntervalRole:
                    return item.interval
                elif role == InputListModel.ExposedRole:
                    return item.exposed
                elif role == InputListModel.LoggingRole:
                    return item.logging
                elif role == InputListModel.AvailableRole:
                    return item.available
                elif role == InputListModel.MinRole:

                    return item.min
                elif role == InputListModel.MaxRole:
                    return item.max
                elif role == InputListModel.StepRole:
                    return item.step

                else:
                    return 'unknown role'
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                line_number = exception_traceback.tb_lineno
                logging.error(f'{self._keys[index.row()]} error {exception_type}: {e} in line {line_number}')

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
        roles[InputListModel.AvailableRole] = b"available"
        roles[InputListModel.MinRole] = b"min"
        roles[InputListModel.MaxRole] = b"max"
        roles[InputListModel.StepRole] = b"step"
        return roles


class InputsDict(QObject):
    def __init__(self, settings):
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
    # def data(self) -> dict:
    #    return self.entries

    # data = Property('QVariantMap', data, constant=True)

    def register_timerschedule(self, key, interval):
        interval = int(interval)
        if interval not in self.timerschedule:
            self.timerschedule[interval] = list()

        self.timerschedule[interval].append(key)

    def delete_timerschedule(self, key, interval):
        if int(interval) in self.timerschedule:
            if key in self.timerschedule[interval]:
                self.timerschedule[interval].remove(key)

    def add(self, newinputs=None):

        for newproperty in newinputs:

            # newinputs[key].logging = bool(int(self.settings.value(key + "/logging", 0)))

            if newproperty.logging:
                self.buffer[newproperty.path] = CircularBuffer(10000)

            if newproperty.interval > 0:
                self.register_timerschedule(newproperty.path, newproperty.interval)

            self.entries[newproperty.path] = newproperty

            if newproperty.events is not None:
                newproperty.events.append(self.update_remote)

            # following lines are inserted to make it possible to update values from another class
            # without removing dict memory adress of introducing class. for example:
            # adding [interrupts] in InputsDevs from another class
            """
            if key in self.entries:
                for subkey in list(newinputs[key]):  # like lastupdate
                    if subkey in self.entries[key]:

                        if type(self.entries[key][subkey]) is list:
                            self.entries[key][subkey].append(
                                newinputs[key][subkey])
                            logging.debug(f'{key} {subkey} {newinputs[key][subkey]}')
                        else:
                            self.entries[key][subkey] = newinputs[key][subkey]
                    else:
                        self.entries[key][subkey] = newinputs[key][subkey]
                del newinputs[key]  # ??
            """

        self.completelist.updateKeys()
        self.dataChanged.emit()

    @Slot(str, result='QVariantList')
    @Slot(str, 'long long', float, result='QVariantList')
    def get_points(self, key, start=None, divider=1):

        # logging.debug(key + ':' + str(divider) + ':' + str(start))
        """
        lo = 0
        hi = len(self.buffer[key])

        if start is not None:

            start = start / 1000            

            while lo < hi:
                    mid = (lo+hi)//2
                    if start < self.buffer[key][mid][0]: hi = mid
                    else: lo = mid+1


            # logging.debug([QPointF((v[0]*1000), v[1]/divider) for v in self.buffer[key][i:]])
            return [QPointF((v[0]*1000), v[1]/divider) for v in self.buffer[key][lo:(lo+1000)]]
            # return p = [QPointF(*v) for v in filter(lambda x: x[0] > start, self.buffer[key])]

        else:"""
        # logging.debug([QPointF((v[0]*1000), v[1]/divider) for v in self.buffer[key]])
        return [QPointF((v[0] * 1000), v[1] / divider) for v in self.buffer[key][:1000]]

    @Slot(str, int, int, int, result='QVariantMap')
    def get_calc_points(self, key, width=800, height=480, divider=1, start=None):

        startx = self.buffer[key].min_time()
        endx = self.buffer[key].max_time()

        scalex = 1

        if (startx != endx):
            scalex = width / ((endx - startx).total_seconds() * 1000)

        max = self.buffer[key].max_data()
        min = self.buffer[key].min_data()

        scaley = 1

        if (min != max):
            scaley = height / (abs(min - max))

        size = self.buffer[key].length()
        polyline = QPolygonF(size)
        buffer = (ctypes.c_double * 2 * size).from_address(shiboken2.getCppPointer(polyline.data())[0])
        memory = np.frombuffer(buffer, np.float)
        memory[: (size - 1) * 2 + 1: 2] = (self.buffer[key].time(size) - np.datetime64(startx, 'ms')).astype(
            float) * scalex
        memory[1: (size - 1) * 2 + 2: 2] = (self.buffer[key].data(size) - min) * scaley

        # [ QPoint(     int(   (v[0] - startx) * scalex), height - int(v[1]/divider * scaley))     for v in self.buffer[key]]s
        return {'startDate': QDateTime(startx), 'endDate': QDateTime(endx), 'polyline': polyline, 'count': size,
                'minValue': float(min / divider), 'maxValue': float(max / divider)}

    @Slot(str, int)
    def set_interval(self, key, value):
        logging.debug('set_interval ' + key + ' ' + str(value))
        try:
            self.delete_timerschedule(key, self.entries[key].interval)
            self.entries[key].interval = int(value)
            self.register_timerschedule(key, int(value))
            self.settings.setValue(key + "/interval", value)
        except KeyError:
            logging.debug(key + ' not in Inputdictionary')

    @Slot(str, bool)
    def set_logging(self, key, value):
        logging.info('set_logging ' + key + ' ' + str(value))
        try:
            self.entries[key].logging = bool(value)
            self.settings.setValue(key + "/logging", int(value))
            if value and key not in self.buffer:
                self.buffer[key] = CircularBuffer(10000)
        except KeyError:
            logging.debug(key + ' not in Inputdictionary')

    @Slot(str, bool)
    def set_exposed(self, key, value):
        logging.debug('set_exposed ' + key + ' ' + str(value))
        try:
            self.entries[key].exposed = bool(value)

            self.settings.setValue(key + "/exposed", int(value))

        except KeyError:
            logging.debug(key + ' not in Inputdictionary')

    def update_remote(self, key):  # doing eventing here

        try:
            self.completelist.updateListView(key)
            if self.entries[key].logging > 0:
                self.buffer[key].append(float(self.entries[key].value), self.entries[key].last_update)

        except KeyError as e:
            logging.error(key + ' does not exists yet, you can ignore this message, if it onlys happens during startup')

    def register_event(self, key, eventfunction):
        try:
            logging.info(key + ' : ' + str(eventfunction))
            self.entries[key].events.append(eventfunction)
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line {line_number}')

    def unregister_event(self, key, eventfunction):
        try:
            logging.info(key + ' : ' + str(eventfunction))
            if eventfunction in self.entries[key].events:
                self.entries[key].events.remove(eventfunction)
        except Exception as e:
            logging.error(str(e))

    def update(self, lastupdate):

        for timeinterval in self.timerschedule:
            if lastupdate % timeinterval == 0:
                for key in self.timerschedule[timeinterval]:
                    try:
                        self.entries[key].update()
                    except Exception as e:
                        exception_type, exception_object, exception_traceback = sys.exc_info()
                        print(exception_type)
                        line_number = exception_traceback.tb_lineno
                        logging.error(f'{e}, removed ' + key + ' from timer_schedule, in line: {line_number}')
                        self.timerschedule[timeinterval].remove(key)

    @Slot(str, str)
    def set(self, key, value):
        logging.debug('set:' + key + ':' + value)
        if key in self.entries and self.entries[key].is_output:
            if self.entries[key].type == DataType.PERCENT_INT:
                self.entries[key].set(float(value))
            elif self.entries[key].type == DataType.INT:
                self.entries[key].set(int(value))
            elif self.entries[key].type == DataType.BOOL:
                self.entries[key].set(int(value))
            elif self.entries[key].type == DataType.ENUM:
                self.entries[key].set(int(value))
