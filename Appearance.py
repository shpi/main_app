import os
from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
from enum import Enum
import threading


class Appearance(QObject):


    def __init__(self, inputs,
                     settings: QSettings = None):

        super(Appearance, self).__init__()

        self.inputs = inputs.entries
        self.backlightlevel = 0
        self._blackfilter = 0
        self.settings = settings
        self._min_backlight = int(settings.value("appearance/min" , 20))
        self._max_backlight = int(settings.value("appearance/max", 100))
        self._min_backlight_night = int(settings.value("appearance/min_night" , 20))
        self._max_backlight_night = int(settings.value("appearance/max_night", 100))
        self._night_mode = int(settings.value("appearance/night_mode" , 0))
        self._night_mode_start = settings.value("appearance/night_mode_start" , '00:00')
        self._night_mode_end =  settings.value("appearance/night_mode_end" , '00:00')
        self._jump_timer = int(settings.value("appearance/jump_timer", 20))
        self.jump_state = 0
        self._dim_timer = int(settings.value("appearance/dim_timer", 100))
        self._off_timer = int(settings.value("appearance/off_timer", 300))
        self.lastuserinput = time.time()
        self.state = 'ACTIVE' # Enum('ACTIVE','SLEEP','OFF')

        self.possible_devs = dict()
        self.possible_devs['list'] = list()

        for key in self.inputs.keys():
            if key.startswith('dev/') and key.find('/',4) == -1:
                self.possible_devs['list'].append(key)
                try:
                 self.possible_devs[key] = int(settings.value("appearance/" + key, 1))
                except:
                 self.possible_devs[key] = 1
                if self.possible_devs[key] == 1:
                    inputs.entries[key]['interrupts'].append((self.interrupt))



    @Property(int,constant=True)
    def dim_timer(self):
        return int(self._dim_timer)

    @dim_timer.setter
    def set_dim_timer(self, seconds):
        self._dim_timer = int(seconds)
        self.settings.setValue("appearance/dim_timer", seconds)


    @Property(str,constant=True)
    def night_mode_start(self):
        return (self._night_mode_start)

    @night_mode_start.setter
    def set_night_mode_start(self, time):
        self._night_mode_start = time
        self.settings.setValue("appearance/night_mode_start", time)
        print(self._night_mode_start)


    @Property(str,constant=True)
    def night_mode_end(self):
        return (self._night_mode_end)

    @night_mode_end.setter
    def set_night_mode_end(self, time):
        self._night_mode_end = time
        self.settings.setValue("appearance/night_mode_end", time)




    @Property(int,constant=True)
    def jump_timer(self):
        return int(self._jump_timer)

    @jump_timer.setter
    def set_jump_timer(self, seconds):
        self._jump_timer = int(seconds)
        self.settings.setValue("appearance/jump_timer", seconds)

    @Signal
    def nightmodeChanged(self):
        pass


    @Property(int,notify=nightmodeChanged)
    def night_mode(self):
            return int(self._night_mode)

    @night_mode.setter
    def set_night_mode(self, value):
            self._night_mode = int(value)
            self.settings.setValue("appearance/night_mode", value)
            self.nightmodeChanged.emit()



    @Property(int,constant=True)
    def off_timer(self):
        return int(self._off_timer)

    @off_timer.setter
    def set_off_timer(self, seconds):
        self._off_timer = int(seconds)
        self.settings.setValue("appearance/off_timer", seconds)



    @Signal
    def rangeChanged(self):
        pass

    @Property(int,notify=rangeChanged)
    def minbacklight(self):
        return int(self._min_backlight)

    @minbacklight.setter
    def set_min_backlight(self, min):
        self._min_backlight = int(min)
        self.settings.setValue("appearance/min", self._min_backlight)
        self.rangeChanged.emit()

    @Property(int,notify=rangeChanged)
    def maxbacklight(self):
        return int(self._max_backlight)

    @maxbacklight.setter
    def set_max_backlight(self, max):
        self._max_backlight = int(max)
        self.rangeChanged.emit()
        self.settings.setValue("appearance/max", self._max_backlight)
        self.set_backlight(self._max_backlight)
        self.rangeChanged.emit()


    def update(self):

        if self.state in ('SLEEP') and self._off_timer > 0 and (self.lastuserinput + self._off_timer < time.time()):
            self.set_backlight(0)
            self.state = 'OFF'

        elif self.state in ('ACTIVE') and self.lastuserinput + self._dim_timer < time.time():
             self.set_backlight(self._min_backlight)
             self.state = 'SLEEP'

        elif self.state in ('SLEEP','OFF') and self._dim_timer > 0 and self.lastuserinput + self._dim_timer > time.time():
            self.set_backlight(self._max_backlight)
            self.state = 'ACTIVE'

        if self.jump_state == 0 and self._jump_timer + self.lastuserinput < time.time():
            self.jump_state = 1
            self.jumpHome.emit()


    @Signal
    def jumpHome(self):
        pass



    def set_backlight(self,value):

        setthread = threading.Thread(target=self._set_backlight,args=(value,))
        setthread.start()


    def _set_backlight(self, value):
       value = int(value)
       if value != self.backlightlevel:
        if value  < 1:
            self.inputs['backlight/brightness']['set'](0)

        elif value < 30:
            self.inputs['backlight/brightness']['set'](1)
            self._blackfilter = ((100 - (value * 3.3)) /100)
            self.blackChanged.emit()

        elif value <= 100:
                self.inputs['backlight/brightness']['set'](int(self.mapFromTo(value,30,100,1,100)))
                self._blackfilter = 0
                self.blackChanged.emit()

        self.backlightlevel = (value)


    def mapFromTo(self,x,a,b,c,d):
        y=(x-a)/(b-a)*(d-c)+c
        return y


    def interrupt(self, key, value):
            self.lastuserinput = time.time()
            self.jump_state = 0

            if self.state in ('OFF','SLEEP'):
                self.state = 'ACTIVE'
                self.set_backlight(self._max_backlight)


    @Signal
    def blackChanged(self):
        pass

    @Slot(str,int)
    def setDeviceTrack(self,path,value):
        value = int(value)
        if value != self.possible_devs[path]:
         self.possible_devs[path] = value
         self.settings.setValue("appearance/" + path, value)

         if self.possible_devs[path] == 1:
            self.inputs[path]['interrupts'].append(self.interrupt)

         else:
            i = 0
            for interrupt in self.inputs[path]['interrupts']:
                if interrupt == self.interrupt:
                    self.inputs[path]['interrupts'].pop(i)
                i += 1



    @Property(float, notify=blackChanged)
    def blackfilter(self):
          return self._blackfilter


    @Property("QVariantMap", constant=True)
    def devices(self) -> dict:
         return dict(self.possible_devs)

