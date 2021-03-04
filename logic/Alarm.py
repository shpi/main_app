import threading
import time

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot


class Shutter(QObject):

    def __init__(self, inputs,
                 settings: QSettings = None):

        super(Shutter, self).__init__()
        self.settings = settings
        self.inputs = inputs.entries
        self.up_time = int(settings.value("shutter/up_time", 3))
        self.down_time = int(settings.value("shutter/down_time", 3))
        self.time_start = 0
        self._residue_time = 0

        self._mode = settings.value("shutter/mode", 'boolean')

        # boolean mode with two binary outputs
        self._relay_up = settings.value("shutter/relay_up", '')
        self._relay_down = settings.value("shutter/relay_down", '')

        # percent_int mode
        self._percent_output = settings.value("shutter/percent_output", '')

        self.userinput = 0

        self._actual_position = int(
            settings.value("shutter/actual_position", 100))

        self._desired_position = self._actual_position
        self.movethread = threading.Thread(target=self.move)
        self._state = 'STOP'  # 'UP', 'DOWN'

    def set_state(self, value):

        if value == 'UP':
            print('relais down 0')
            time.sleep(0.1)
            print('relais up 1')
            self._state = 'UP'
            self.stateChanged.emit()

        elif value == 'DOWN':
            print('relais down 1')
            time.sleep(0.1)
            print('relais up 0')
            self._state = 'DOWN'
            self.stateChanged.emit()

        elif value == 'STOPSLEEP':
            self._state = 'STOPSLEEP'
            self.stateChanged.emit()
            time.sleep(1)
            print('relais down 0')
            print('relais up 0')
            self._state = 'STOP'
            self.stateChanged.emit()

        elif value == 'STOP':
            print('relais down 0')
            print('relais up 0')
            self._state = 'STOP'
            self.stateChanged.emit()

    def start_move(self):
        if not self.movethread.is_alive():
            self.movethread = threading.Thread(target=self.move)
            self.movethread.start()

    @Signal
    def stateChanged(self):
        pass

    @Signal
    def positionChanged(self):
        pass

    @Property(str, notify=stateChanged)
    def state(self):
        return self._state

    @Property(str, constant=True)
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, key):
        self._mode = key
        self.settings.setValue(self.path + "shutter/mode", key)

    @Property(int, notify=positionChanged)
    def desired_position(self):
        return int(self._desired_position)

    @Property(float, notify=positionChanged)
    def actual_position(self):
        return self._actual_position

    @actual_position.setter
    def actual_position(self, key):
        self._actual_position = int(key)
        self.settings.setValue("shutter/actual_position", int(key))
        self.positionChanged.emit()

    @Property(float, notify=positionChanged)
    def residue_time(self):
        return float(self._residue_time)

    @Slot(int)
    def set_position(self, value):
        self.userinput = 1
        self._desired_position = int(value)
        self._residue_time = 0
        self.positionChanged.emit()
        self.start_move()
