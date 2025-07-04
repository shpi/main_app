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

        self.properties['module'] = EntityProperty(
                                                   category='module',
                                                   value='NOT_INITIALIZED',
                                                   name='disk',
                                                   description='disk stats module',
                                                   type=DataType.MODULE,
                                                   call=self.update,
                                                   interval=600)

        self.properties['module'].last_update = time.time() - DiskStats.get_uptime()

        self.update(init=True)

    def update(self, init=False):

        oldtime = self.properties['module'].last_update
        self.properties['module'].value = 'OK'
        quotient =  max(1, (self.properties['module'].last_update - oldtime))

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
                        self.properties[f'{line[2]}/{key}'] = EntityProperty(
                                                                             category='disk/' + line[2],
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

