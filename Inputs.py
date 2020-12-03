# This Python file uses the following encoding: utf-8
import time
from PySide2.QtCore import Qt, QModelIndex,QSortFilterProxyModel
from PySide2.QtCore import QAbstractListModel, Property, Signal, Slot, QObject
from DataTypes import Convert
from DataTypes import DataType

class InputListModel(QAbstractListModel):
    PathRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001
    DescriptionRole = Qt.UserRole + 1002
    TypeRole = Qt.UserRole + 1003
    IntervalRole = Qt.UserRole + 1004
    ExposedRole = Qt.UserRole + 1005
    OutputRole = Qt.UserRole + 1006

    def __init__(self, dictionary, parent=None):
        super(InputListModel, self).__init__(parent)
        self.entries = dictionary
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
        roles[InputListModel.IntervalRole] = b"invertval"
        roles[InputListModel.ExposedRole] = b"exposed"
        roles[InputListModel.OutputRole] = b"output"
        return roles


class InputsDict(QObject):

    def __init__(self, parent: QObject = None):
        super(InputsDict, self).__init__(parent)
        self.entries = dict()
        self.completelist = InputListModel(self.entries)

        self.outputs = QSortFilterProxyModel()
        self.outputs.setSourceModel(self.completelist)
        self.outputs.setFilterRole(self.completelist.OutputRole)
        self.outputs.setFilterFixedString('1')

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

    @Property(QObject, notify=dataChanged, constant=False)
    def inputList(self):
        self.completelist.filter = None
        return self.completelist


    @Property(QObject, notify=dataChanged, constant=False)
    def outputList(self):
        return self.outputs

    @Property(QObject, notify=dataChanged, constant=False)
    def typeList(self):
        return self.proxy

    @Property(QObject, notify=dataChanged, constant=False)
    def searchList(self):
        return self.search

    @Slot(str)
    def set_typeList(self, type):
        self.proxy.setFilterFixedString(type)

    @Slot(str)
    def set_searchList(self, type):
        self.search.setFilterFixedString(type)

    @Property("QVariantMap", notify=dataChanged)
    def data(self) -> dict:
        return self.entries

    def add(self, newinputs=dict()):
        for key in list(newinputs):
            if 'lastupdate' not in newinputs[key]:
                newinputs[key]['lastupdate'] = 0
            if 'value' not in newinputs[key]:
                newinputs[key]['value'] = 0
            if 'interval' not in newinputs[key] and 'call' in newinputs[key]:
                newinputs[key]['interval'] = 5


            # following lines are inserted to make it possible to update values from another class
            # without removing dict memory adress of introducing class. for example:
            # adding [interrupts] in InputsDevs from another class

            if key in self.entries:

                for subkey in list(newinputs[key]):# like lastupdate
                    if subkey in self.entries[key]:

                        if type(self.entries[key][subkey]) is list:
                            self.entries[key][subkey].append(newinputs[key][subkey])
                            print(f'{key} {subkey} {newinputs[key][subkey]}')
                        else:
                            self.entries[key][subkey] = newinputs[key][subkey]
                    else:
                        self.entries[key][subkey] = newinputs[key][subkey]
                del newinputs[key]


        self.entries.update(newinputs)
        self.completelist.updateKeys()
        self.update(0)
        self.dataChanged.emit()



# interval -1 =  update through class
# interval  0 =  one time
# interval > 0 =  call function

    def update(self, lastupdate):
        acttime = time.time()
        for key, value in self.entries.items():

            if (value['lastupdate'] > lastupdate):
                    self.completelist.updateListView(key)


            elif ((value['interval'] > 0) and (value['lastupdate'] +
                                             value['interval'] < acttime)):

                temp = self.entries[key]['call']()

                if (temp != self.entries[key]['value']):
                    self.entries[key]['value'] = temp
                    self.completelist.updateListView(key)
                self.entries[key]['lastupdate'] = acttime



        self.dataChanged.emit()

    @Slot(str,str)
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



