import glob, os



class HWMon:

    def __init__(self,  parent=None):

        super(HWMon, self).__init__()

        self._hwmon = dict()
        self._outputs = dict()

        for sensors in glob.iglob('/sys/class/hwmon/hwmon*',recursive = False):
            sensor = dict()

            if os.path.isfile(sensors + '/name'):

                with open(sensors + '/name','r') as rf:
                    sensor['name'] = (rf.read().rstrip())

                rf.close()

            sensors = sensors.split('/')
            sensor['id'] = sensors[-1]

            for type in ('input','alarm','enable'):

                for filename in glob.iglob('/sys/class/hwmon/' + sensors[-1] + '/*_' + type):

                    channel = sensor.copy()

                    if (os.path.isfile(filename[0:-len(type)] + "label")):

                        with open(filename[0:-len(type)] + "label", 'r') as rf:
                            channel['description'] = (rf.read().rstrip())

                        rf.close()
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
                        rf.close()
                    channel['path'] = filename
                    channel['rights'] = oct(os.stat(filename).st_mode & 0o777)
                    filename = filename.split('/')
                    channel['channel'] = filename[-1]
                    self._hwmon[channel['name'] + '/' + filename[-1]] = channel

        #print(self._hwmon)
        for key, value in self._hwmon.items():
            if (value['rights'] == '0o644'):
                self._outputs['hwmon/' + value['name'] + '/' + value['channel']] = lambda x: (self.write(value['id'], value['channel'], x))




    def get_inputs(self):

        inputs = dict()

        for key, value in self._hwmon.items():
            if (value['rights'] == '0o444'):
                inputs['hwmon/' + value['name'] + '/' + value['channel']] = lambda: self.read(value['id'], value['channel'])

        return inputs


    def read(self, id, channel):

           if os.path.isfile('/sys/class/hwmon/' + id + '/' + channel):
                with open('/sys/class/hwmon/' + id + '/' + channel, 'r') as rf:
                    return (rf.read().rstrip())
                rf.close()

           else:
               return False


    def get_outputs(self):

        return self._outputs


    def write(self, id, channel, value):
           print(id,channel,value)
           if os.path.isfile('/sys/class/hwmon/' + id + '/' + channel):
                with open('/sys/class/hwmon/' + id + '/' + channel, 'r+') as rf:
                    rf.write(str(value))
                    rf.seek(0)
                    if value == rf.read().rstrip(): return True
                    else: return False
                rf.close()

           else:
               return False



hwmon = HWMon()

outputs = hwmon.get_outputs()


print(outputs['hwmon/shpi/relay2'](1))








