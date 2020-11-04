import glob, os
from functools import partial

class HWMon:

    def __init__(self,  parent=None):

        super(HWMon, self).__init__()
        self._hwmon = dict()

        for sensors in glob.iglob('/sys/class/hwmon/hwmon*',recursive = False):
            sensor = dict()

            if os.path.isfile(sensors + '/name'):
                with open(sensors + '/name','r') as rf:
                    sensor['name'] = (rf.read().rstrip())

            sensors = sensors.split('/')
            sensor['id'] = sensors[-1]

            for type in ('input','alarm','enable'):
                for filename in glob.iglob('/sys/class/hwmon/' + sensor['id'] + '/*_' + type):

                    channel = sensor.copy()

                    if (os.path.isfile(filename[0:-len(type)] + "label")):
                        with open(filename[0:-len(type)] + "label", 'r') as rf:
                            channel['description'] = (rf.read().rstrip())

                    channel['path'] = filename
                    channel['rights'] = oct(os.stat(filename).st_mode & 0o777)
                    filename = filename.split('/')
                    channel['channel'] = filename[-1]
                    self._hwmon[channel['name'] + '/' + filename[-1]] = channel



            for type in ('pwm','buzzer','relay'):
                for filename in glob.iglob('/sys/class/hwmon/' + sensors[-1] + '/' + type + '[0-9]'):
                    channel = sensor.copy()
                    if (os.path.isfile(filename + "_label")):

                        with open(filename + "_label", 'r') as rf:
                            channel['description'] = (rf.read().rstrip())

                    channel['path'] = filename
                    channel['rights'] = oct(os.stat(filename).st_mode & 0o777)
                    filename = filename.split('/')
                    channel['channel'] = filename[-1]
                    self._hwmon[channel['name'] + '/' + filename[-1]] = channel

        #print(self._hwmon)




    def register_inputs(self, globaldict):

        for key, value in self._hwmon.items():
            if (value['rights'] == '0o444'):
                globaldict['hwmon/' + value['name'] + '/' + value['channel']] = partial(self.read_hwmon, value['id'], value['channel'])



    def read_hwmon(self, id, channel):

           if os.path.isfile('/sys/class/hwmon/' + id + '/' + channel):
                with open('/sys/class/hwmon/' + id + '/' + channel, 'r') as rf:
                    return (rf.read().rstrip())
                rf.close()

           else:
               return False


    def register_outputs(self, globaldict):

        for key, value in self._hwmon.items():
            if (value['rights'] == '0o644'):
                globaldict['hwmon/' + value['name'] + '/' + value['channel']] =  partial(self.write_hwmon, value['id'], value['channel'])




    def write_hwmon(self, id, channel, value):
           value = str(value)
           print(id,channel,value)
           if os.path.isfile('/sys/class/hwmon/' + id + '/' + channel):
                with open('/sys/class/hwmon/' + id + '/' + channel, 'r+') as rf:
                    rf.write(value)
                    rf.seek(0)
                    if (value == rf.read().rstrip()): return True
                    else: return False

           else:
               return False



hwmon = HWMon()

outputs = dict()


hwmon.register_outputs(outputs)



print(outputs['hwmon/shpi/relay2'](1))







