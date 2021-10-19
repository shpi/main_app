import logging
import threading
import time

from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot

from core.DataTypes import DataType
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix


class ShutterModes:
    STOP = 0
    UP = 1
    DOWN = 2
    SLEEP = 3
    __valid_range = STOP, SLEEP  # lowest and highest

    @classmethod
    def is_valid(cls, number) -> bool:
        min_, max_ = cls.__valid_range
        return min_ <= number <= max_


class Shutter(QObject):

    def __init__(self, name, inputs,
                 settings: QSettings = None):

        super(Shutter, self).__init__()
        self.name = name
        self.path = 'shutter/' + name
        self.settings = settings
        self.inputs = inputs.entries
        self._up_time = float(settings.value('shutter/' + self.name + "/up_time", 3000)) / 100
        self._down_time = float(settings.value('shutter/' + self.name + "/down_time", 3000)) / 100

        self.time_start = 0
        self._residue_time = 0

        # boolean mode with two binary outputs
        self._relay_up = settings.value('shutter/' + self.name + "/relay_up", '')
        self._relay_down = settings.value('shutter/' + self.name + "/relay_down", '')

        self.userinput = 0

        self._module = EntityProperty(parent=self,
                                      category='module/logic',
                                      entity='shutter',
                                      name=name,
                                      value='NOT_INITIALIZED',
                                      description='Shutter Module for two binary outputs',
                                      type=DataType.MODULE,
                                      interval=-1)

        self._actual_position = EntityProperty(parent=self,
                                               category='logic/shutter',
                                               entity=name,
                                               name='actual_position',
                                               description='actual position',
                                               type=DataType.PERCENT_FLOAT,
                                               interval=-1)

        self._desired_position = EntityProperty(parent=self,
                                                category='logic/shutter',
                                                entity=name,
                                                name='desired_position',
                                                description='desired position',
                                                type=DataType.PERCENT_INT,
                                                set=self.set_desired_position,
                                                interval=-1)

        self.movethread = threading.Thread(target=self.move)
        self._state = ShutterModes.STOP

    def get_inputs(self) -> list:
        return [self._module, self._actual_position, self._desired_position]

    def set_up(self, value):

        if self._relay_up in self.inputs:
            if self.inputs[self._relay_up].type == DataType.BOOL:
                if self.inputs[self._relay_up].is_output:
                    try:
                        self.inputs[self._relay_up].set(bool(value))
                        status = 'OK'
                    except Exception as e:
                        status = 'ERROR'
                        logging.error('Error UP control:' + self._relay_up + ' error: ' + str(e))
                else:
                    status = 'ERROR'
                    logging.error('Error UP control:' + self._relay_up + ' set missing.')
            else:
                status = 'ERROR'
                logging.error('Error DataType UP control:' + self._relay_up + ' not BOOLEAN')
        else:
            status = 'ERROR'
            logging.error('Error UP control ' + self._relay_up + ' not in Inputs.')

        self._module.value = status

    def set_down(self, value):

        if self._relay_down in self.inputs:
            if self.inputs[self._relay_down].type == DataType.BOOL:
                if self.inputs[self._relay_down].is_output:
                    try:
                        self.inputs[self._relay_down].set(bool(value))
                        status = 'OK'
                    except Exception as e:
                        status = 'ERROR'
                        logging.error('Error down control:' + self._relay_down + ' error: ' + str(e))
                else:
                    status = 'ERROR'
                    logging.error('Error down control:' + self._relay_down + ' set missing.')
            else:
                status = 'ERROR'
                logging.error('Error DataType down control:' + self._relay_down + ' not BOOLEAN')
        else:
            status = 'ERROR'
            logging.error('Error down control ' + self._relay_down + ' not in Inputs.')

        self._module.value = status

    @Slot(int)
    def set_state(self, value):

        if value == ShutterModes.UP:

            self.set_down(0)
            time.sleep(0.01)
            self.set_up(1)
            self._state = ShutterModes.UP


        elif value == ShutterModes.DOWN:
            self.set_down(1)
            time.sleep(0.01)
            self.set_up(0)
            self._state = ShutterModes.DOWN


        elif value == ShutterModes.SLEEP:
            self._state = ShutterModes.SLEEP
            time.sleep(0.01)
            self.set_down(0)
            self.set_up(0)
            self._state = ShutterModes.STOP


        elif value == ShutterModes.STOP:
            self.set_down(0)
            self.set_up(0)
            self._state = ShutterModes.STOP

    def start_move(self):
        if not self.movethread.is_alive():
            self.movethread = threading.Thread(target=self.move)
            self.movethread.start()

    @Signal
    def configChanged(self):
        pass

    @Signal
    def stateChanged(self):
        pass

    @Signal
    def positionChanged(self):
        pass

    @Property(str, notify=stateChanged)
    def state(self):
        return self._state

    def desired_position(self):
        return (self._desired_position.value)

    @Pre_5_15_2_fix(int, desired_position, notify=positionChanged)
    def desired_position(self, value):
        self._desired_position.value = int(value)
        self.positionChanged.emit()

    @Slot(int)
    # @desired_position.setter
    # @Pre_5_15_2_fix(str, desired_position, notify=positionChanged)
    def set_desired_position(self, value):  # we need special name here for SET field in dict ??
        self.userinput = 1
        self._desired_position.value = int(value)
        self._residue_time = 0

        if self._actual_position.value is None:
            if value > 50:
                self._actual_position.value = 0
                self._desired_position.value = 100
            else:
                self._actual_position.value = 100
                self._desired_position.value = 0

        self.positionChanged.emit()
        self.start_move()

    # @Property(float,notify=positionChanged)
    def actual_position(self):
        if self._actual_position.value is None:
            return -1
        return (self._actual_position.value)

    # @actual_position.setter
    @Pre_5_15_2_fix(int, actual_position, notify=positionChanged)
    def actual_position(self, value):
        self._actual_position.value = int(value)
        self.positionChanged.emit()

        # self.settings.setValue('shutter/' + self.name + "/actual_position", value)

    @Signal
    def relayChanged(self):
        pass

    # @Property(str,notify=relayChanged)
    def relay_up(self):
        return str(self._relay_up)

    # @actual_position.setter
    @Pre_5_15_2_fix(str, relay_up, notify=relayChanged)
    def relay_up(self, value):
        self._relay_up = str(value)
        self.settings.setValue('shutter/' + self.name + "/relay_up", value)

    # @Property(str,notify=relayChanged)
    def relay_down(self):
        return str(self._relay_down)

    # @actual_position.setter
    @Pre_5_15_2_fix(str, relay_down, notify=relayChanged)
    def relay_down(self, value):
        self._relay_down = str(value)
        self.settings.setValue('shutter/' + self.name + "/relay_down", value)

    # @Property(float,notify=configChanged)
    def down_time(self):
        return (self._down_time * 100)

    # @down_time.setter
    @Pre_5_15_2_fix(int, down_time, notify=configChanged)
    def down_time(self, value):

        self._down_time = float(value / 100)
        self.settings.setValue('shutter/' + self.name + "/down_time", value)
        self.configChanged.emit()

    # @Property(float,notify=configChanged)
    def up_time(self):
        return (self._up_time * 100)

    # @up_time.setter
    @Pre_5_15_2_fix(int, up_time, notify=configChanged)
    def up_time(self, value):
        self._up_time = float(value / 100)
        self.settings.setValue('shutter/' + self.name + "/up_time", value)
        self.configChanged.emit()

    @Property(float, notify=positionChanged)
    def residue_time(self):
        return float(self._residue_time)

    def move(self):
        if self._actual_position.value is None:
            logging.error('Please calibrate Shutter Instance')
        else:
            was_in_loop = False

            while (self._actual_position.value < self._desired_position.value) or (
                    self._actual_position.value > self._desired_position.value):

                was_in_loop = True

                if self._actual_position.value < self._desired_position.value:

                    # need to move down, to close
                    if self.userinput == 1 and self._state != ShutterModes.UP:
                        self.set_state(ShutterModes.UP)
                        self.userinput = 0
                        self.time_start = time.time()
                        self.start_position = self._actual_position.value
                    time.sleep(0.01)
                    self._actual_position.value = self.start_position + \
                                                  ((100 / self._down_time) * (time.time() - self.time_start))
                    self.positionChanged.emit()
                    self._residue_time = (
                                                 self._desired_position.value - self._actual_position.value) * (
                                                 self._down_time / 100)
                    if self._residue_time < 0:  # detected overshoot, so stopping
                        self._residue_time = 0
                        if self.userinput == 0:  # ignore overshoots and allow direction change only on new input
                            self._actual_position.value = self._desired_position.value
                            self.positionChanged.emit()


                elif self._actual_position.value > self._desired_position.value:

                    # need to move up, to open
                    if self.userinput == 1 and self._state != ShutterModes.DOWN:
                        self.set_state(ShutterModes.DOWN)
                        self.userinput = 0
                        self.time_start = time.time()
                        self.start_position = self._actual_position.value
                    time.sleep(0.01)
                    self._actual_position.value = self.start_position - \
                                                  (100 / self._up_time) * (time.time() - self.time_start)
                    self.positionChanged.emit()
                    self._residue_time = (
                                                 self._actual_position.value - self._desired_position.value) * (
                                                 self._up_time / 100)
                    if self._residue_time < 0:
                        self._residue_time = 0
                        if self.userinput == 0:
                            self._actual_position.value = self._desired_position.value
                            self.positionChanged.emit()

            self._residue_time = 0

            if was_in_loop and self._desired_position.value == 100 or self._desired_position.value == 0:
                self._actual_position.value = self._desired_position.value
                self.set_state(ShutterModes.SLEEP)
            else:
                self.set_state(ShutterModes.STOP)
