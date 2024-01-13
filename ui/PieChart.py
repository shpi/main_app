from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot

from core.Toolbox import Pre_5_15_2_fix


class PieChart(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super().__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name
        self._values = {}
        self._value_path = settings.value('piechart/' + self.name + "/value_path", [])

        if isinstance(self._value_path, str):
            self._value_path = [self._value_path]
        elif self._value_path is None:
            self._value_path = []

        for value_path in self._value_path:
            self._values[value_path] = self.inputs.entries[value_path].value
            self.inputs.register_event(value_path, self.ui_event)

    def get_inputs(self):
        return []

    @Signal
    def position_pathChanged(self):
        pass

    @Signal
    def valuesChanged(self):
        pass

    @Property('QVariantList', notify=valuesChanged)
    def colors(self):
        return ['red', 'green', 'yellow', 'blue', 'orange', 'brown']

    @Property(float, notify=valuesChanged)
    def sum(self):
        return sum(self._values.values())

    @Slot(int, result=float)
    def angle(self, i):
        a = 0
        summe = sum(self._values.values())
        angleq = 360 / summe
        actangle = 0
        for value in self._values.values():
            if a >= i:
                return actangle
            actangle += angleq * float(value)
            a += 1

    @Property('QVariantList', notify=valuesChanged)
    def values(self):
        return list(self._values.values())

    @Property('QVariantList', notify=position_pathChanged)
    def names(self):
        return [self.inputs.entries[path].name for path in self._values.keys()]

    def value_path(self):
        return self._value_path

    # @value_path.setter
    @Pre_5_15_2_fix('QVariantList', value_path, notify=position_pathChanged)
    def value_path(self, key):
        self._value_path = key
        self.settings.setValue('piechart/' + self.name + "/value_path", key)

    def ui_event(self, path, value):
        self._values[path] = value
        self.valuesChanged.emit()

    @Slot(str)
    def add_path(self, value):

        if value not in self._values:
         self._values[value] = self.inputs.entries[value].value

        self._value_path.append(value)
        self.settings.setValue('piechart/' + self.name + "/value_path", self._value_path)
        self.inputs.register_event(value, self.ui_event)
        self.valuesChanged.emit()
        self.position_pathChanged.emit()

    @Slot(str)
    def remove_path(self, value):

        if value in self._value_path:
            self._value_path.remove(value)
            if value in self._values:
             del self._values[value]
            self.inputs.unregister_event(value, self.ui_event)
            self.settings.setValue('piechart/' + self.name + "/value_path", self._value_path)
            self.valuesChanged.emit()
            self.position_pathChanged.emit()
