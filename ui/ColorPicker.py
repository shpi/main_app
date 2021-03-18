import logging
from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
from core.Toolbox import Pre_5_15_2_fix


class ColorPicker(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super().__init__()
        self.settings = settings
        self.inputs = inputs
        self.name = name

        self._red = 0
        self._green = 0
        self._blue = 0

        self._red_path = settings.value('colorpicker/' + self.name + "/red_path", '')
        self._green_path = settings.value('colorpicker/' + self.name + "/green_path", '')
        self._blue_path = settings.value('colorpicker/' + self.name + "/blue_path", '')


    def delete_inputs(self):
        pass

    @Signal
    def pathChanged(self):
        pass

    @Signal
    def valuesChanged(self):
        pass


    def red_path(self):
        return self._red_path

    # @value_path.setter
    @Pre_5_15_2_fix(str, red_path, notify=pathChanged)
    def red_path(self, key):
        self._red_path = key
        self.settings.setValue('colorpicker/' + self.name + "/red_path", key)

    def green_path(self):
        return self._green_path

    # @value_path.setter
    @Pre_5_15_2_fix(str, green_path, notify=pathChanged)
    def green_path(self, key):
        self._green_path = key
        self.settings.setValue('colorpicker/' + self.name + "/green_path", key)

    def blue_path(self):
        return self._blue_path

    # @value_path.setter
    @Pre_5_15_2_fix(str, blue_path, notify=pathChanged)
    def blue_path(self, key):
        self._blue_path = key
        self.settings.setValue('colorpicker/' + self.name + "/blue_path", key)

    @Slot(int,int,int)
    def set(self, red, green, blue):
       try:
        self.inputs.entries[self._red_path].set(red)
        self._red = red
       except Exception as e:
           logging.error(str(e))

       try:
        self.inputs.entries[self._green_path].set(green)
        self._green = green
       except Exception as e:
           logging.error(str(e))

       try:
        self.inputs.entries[self._blue_path].set(blue)
        self._blue = blue
       except Exception as e:
           logging.error(str(e))


    @Property(int, notify=valuesChanged)
    def red(self):
        return int(self._red)

    @Property(int, notify=valuesChanged)
    def green(self):
        return int(self._green)

    @Property(int, notify=valuesChanged)
    def blue(self):
        return int(self._blue)

    def ui_event(self, path, value):
        if path == self._red_path:
            if value != self._red:
                self._red = value
                self.valuesChanged.emit()
        elif path == self._green_path:
            if value != self._green:
                self._green = value
                self.valuesChanged.emit()
        elif path == self._blue_path:
            if self._blue != value:
                self._blue = value
                self.valuesChanged.emit()



