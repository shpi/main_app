import logging
import os
import shutil
import time

from core.DataTypes import DataType
from core.Property import EntityProperty, StaticProperty


class DiskStats:
    _keys = 'read_bps', 'write_bps', 'read_abs', 'write_abs'
    _descs = 'read bytes per second', 'write bytes per second', 'read absolute', 'write absolute'

    stat_path = '/proc/diskstats'

    def __init__(self):

        if not os.path.isfile(DiskStats.stat_path):
            logging.error(DiskStats.stat_path + ' does not exists.')
            return

        self.properties = dict()  # we need a dict here, because we update all values with a single update function
        self.last_diskstat = 0

        self.properties['module'] = EntityProperty(parent=self,
                                                   category='module',
                                                   entity='core',
                                                   value='NOT_INITIALIZED',
                                                   name='disk',
                                                   description='disk stats module',
                                                   type=DataType.MODULE,
                                                   call=self.update,
                                                   interval=60)

        self.properties['module'].last_update = time.time() - DiskStats.get_uptime()

        self.properties['disk_usage'] = EntityProperty(parent=self,
                                                       category='core',
                                                       entity='disk',
                                                       name='disk_usage',
                                                       description='disk usage',
                                                       type=DataType.INT,
                                                       call=DiskStats.disk_used,
                                                       interval=600)

        self.properties['disk_total'] = StaticProperty(parent=self,
                                                       category='core',
                                                       entity='disk',
                                                       name='disk_size',
                                                       value=DiskStats.disk_total(),
                                                       description='disk total size',
                                                       type=DataType.INT)

        self.update(init=True)

    def update(self, init=False):

        oldtime = self.properties['module'].last_update
        self.properties['module'].value = 'OK'
        quotient = self.properties['module'].last_update - oldtime

        with open(DiskStats.stat_path) as stat_file:
            for line in stat_file:
                line = line.split()
                if not line:
                    continue

                if line[2].startswith('loop') or line[2].startswith('ram'):
                    # only physical devices
                    continue

                if init:

                    for key, desc in list(zip(DiskStats._keys, DiskStats._descs)):
                        self.properties[f'{line[2]}/{key}'] = EntityProperty(parent=self,
                                                                             category='disk',
                                                                             entity=line[2],
                                                                             value=0,
                                                                             name=key,
                                                                             description=desc,
                                                                             type=DataType.INT,
                                                                             interval=-1)

                self.properties[f'{line[2]}/read_bps'].value = (int(line[3]) - self.properties[
                    f'{line[2]}/read_abs'].value) // quotient
                self.properties[f'{line[2]}/write_bps'].value = (int(line[7]) - self.properties[
                    f'{line[2]}/write_abs'].value) // quotient
                self.properties[f'{line[2]}/read_abs'].value = int(line[3])
                self.properties[f'{line[2]}/write_abs'].value = int(line[7])

        return 'OK'

    def get_inputs(self) -> list:
        return self.properties.values()

    @staticmethod
    def disk_total():
        # total used free
        # /proc/properties for io rates
        return list(shutil.disk_usage("/"))[0]

    @staticmethod
    def disk_used():
        # total used free
        # /proc/properties for io rates
        return list(shutil.disk_usage("/"))[1]

    @staticmethod
    def get_uptime(stat_path='/proc/uptime'):
        if os.path.isfile(stat_path):
            with open(stat_path) as stat_file:
                return int(float(next(stat_file).split()[0]))
