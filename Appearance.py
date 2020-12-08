from PySide2.QtCore import QSettings, QObject, Property, Signal, Slot
import time
import os
from enum import Enum
import threading
from datetime import datetime
from DataTypes import DataType


class Appearance(QObject):


    def __init__(self, inputs,
                     settings: QSettings = None):

        super(Appearance, self).__init__()

        self.inputs = inputs.entries
        self.backlightlevel = 0
        self._blackfilter = 0
        self.settings = settings
        self._background_night = int(settings.value("appearance/background_night" , 1))
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
        self._night = 0

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

    @Slot(str)
    def delete_file(self, path):
        if os.path.exists(path):
          os.remove(path)


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
    def background_Night_Changed(self):
        pass

    @Property(bool,notify=background_Night_Changed)
    def background_night(self):
        return bool(self._background_night)

    @background_night.setter
    def set_background_night(self, min):
        self._background_night = int(min)
        self.settings.setValue("appearance/background_night", self._background_night)
        self.background_Night_Changed.emit()


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
    def minbacklight_night(self):
        return int(self._min_backlight_night)

    @minbacklight_night.setter
    def set_min_backlight_night(self, min):
        self._min_backlight_night = int(min)
        self.settings.setValue("appearance/min_night", self._min_backlight_night)
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


    @Property(int,notify=rangeChanged)
    def maxbacklight_night(self):
        return int(self._max_backlight_night)

    @maxbacklight_night.setter
    def set_max_backlight_night(self, max):
       self._max_backlight_night = int(max)
       self.rangeChanged.emit()
       self.settings.setValue("appearance/max_night", self._max_backlight_night)
       self.set_backlight(self._max_backlight_night)
       self.rangeChanged.emit()

    @Signal
    def nightChanged(self):
           pass


    @Property(int,notify=nightChanged)
    def night(self):
               return int(self._night)




    def update(self):

        error = False
        night = self._night

        if self._night_mode > -1 and self._night_mode_start != self._night_mode_end:

            if self._night_mode == 0:
                start = self._night_mode_start
                end = self._night_mode_end

            elif self._night_mode == 1:
                if self._night_mode_start in self.inputs and self.inputs[self._night_mode_start]['type'] == DataType.TIME:
                    start = self.inputs[self._night_mode_start]['value']
                else:
                    error = True
                    print('Datatype doesnt match, Nightmode disabled')
                    self._night = 0

                if self._night_mode_end in self.inputs and self.inputs[self._night_mode_end]['type'] == DataType.TIME:
                    end = self.inputs[self._night_mode_end]['value']
                else:
                    error = True
                    print('Datatype doesnt match, Nightmode disabled')
                    self._night = 0

            if error == False:
                start = start.split(':')
                start = int(start[0]) * 60 + int(start[1])
                now = datetime.now().strftime("%H:%M").split(':')
                now = int(now[0]) * 60 + int(now[1])
                end = end.split(':')
                end = int(end[0]) * 60 + int(end[1])

                if start < end: # 18 - 23:00
                    if now > end or now < start:
                        self._night = 0
                    else:
                        self._night = 1

                else:  # end < start: # 18 - 3:00
                    if now > end and now < start:
                        self._night = 0
                    else:
                        self._night = 1

        else:
            self._night = 0

        if night != self._night:
                self.nightChanged.emit()


        if self.state in ('SLEEP') and self._off_timer > 0 and (self.lastuserinput + self._off_timer < time.time()):
            self.set_backlight(0)
            self.state = 'OFF'

        elif self.state in ('ACTIVE') and self.lastuserinput + self._dim_timer < time.time():
             if self._night:
                 self.set_backlight(self._min_backlight_night)
             else:
                 self.set_backlight(self._min_backlight)
             self.state = 'SLEEP'

        elif self.state in ('SLEEP','OFF') and self._dim_timer > 0 and self.lastuserinput + self._dim_timer > time.time():
            if self._night:
                self.set_backlight(self._max_backlight_night)
            else:
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
    def setDeviceTrack(self, path, value):
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

