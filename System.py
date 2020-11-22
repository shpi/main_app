import sys
import os
import socket
import fcntl
import struct
import shutil
import re
import glob
import time
from DataTypes import DataType

# iw dev wlan0 link
# iw dev wlan0 station dump -v


class _SystemInfo:

    def __init__(self,  parent=None):
        super(_SystemInfo, self).__init__()
        self.diskstats = dict()
        self._keys = 'read_bps', 'write_bps', 'read_abs', 'write_abs'
        self.last_diskstat = 0
        self.update_diskstats(init=True)


    def update_diskstats(self, stat_path='/proc/diskstats', init=False):
        if os.path.isfile(stat_path):
            acttime = (time.time())
            quotient = acttime - self.last_diskstat
            self.last_diskstat = acttime

            with open(stat_path) as stat_file:
                while True:
                    line = stat_file.readline().split()
                    if line:

                        if not line[2].startswith('loop'):
                            # only physical devices

                            if init:
                                self.diskstats[f'system/disk_{line[2]}/read_bps'] =  {'value' : 0,
                                                                                           'interval': -1,
                                                                                           'type' : DataType.INT,
                                                                                           'description' : 'read bytes per second'}

                                self.diskstats[f'system/disk_{line[2]}/write_bps'] = {'value' : 0,
                                                                                           'interval': -1,
                                                                                           'type' : DataType.INT,
                                                                                           'description' : 'write bytes per second'}
                                self.diskstats[f'system/disk_{line[2]}/read_abs'] =  {'value' : 0,
                                                                                           'interval': -1,
                                                                                           'type' : DataType.INT,
                                                                                           'description' : 'read bytes absolute'}
                                self.diskstats[f'system/disk_{line[2]}/write_abs'] = {'value' : 0,
                                                                                           'interval': -1,
                                                                                           'type' : DataType.INT,
                                                                                           'description' : 'write bytes absolute'}

                            self.diskstats[f'system/disk_{line[2]}/read_bps']['value'] = (int(line[3]) -
                             self.diskstats[f'system/disk_{line[2]}/read_abs']['value']) // quotient

                            self.diskstats[f'system/disk_{line[2]}/write_bps']['value'] = (int(line[7]) -
                             self.diskstats[f'system/disk_{line[2]}/write_abs']['value']) // quotient

                            self.diskstats[f'system/disk_{line[2]}/read_abs']['value'] = int(line[3])
                            self.diskstats[f'system/disk_{line[2]}/write_abs']['value'] = int(line[7])

                            for key in self._keys:
                                self.diskstats[f'system/disk_{line[2]}/{key}']['lastupdate'] = acttime

                    else:
                        break

    def update(self):
        if self.last_diskstat + 10 < time.time():
            self.update_diskstats()

    def get_discstats(self):
        return self.diskstats

    def get_inputs(self) -> dict:

        inputs = self.diskstats

        inputs['system/is64bit'] = {"description": "64bit system?",
                                    # "rights":0o444,
                                    "type": DataType.BOOL,
                                    "interval": 0,
                                    "value": self.is64bit(),
                                    "call": self.is64bit}

        inputs['system/cpu_freq'] = {"description": "actual CPU clock",
                                     # "rights": 0o444,
                                     "type": DataType.INT,
                                     "interval": 10,
                                     "call": self.get_cpu_freq}

        inputs['system/cpu_usage'] = {"description": "CPU usage %",
                                      # "rights": 0o444,
                                      "type": DataType.PERCENT_FLOAT,
                                      "interval": 10,
                                      "call": self.cpu_usage}

        inputs['system/ram_usage'] = {"description": "RAM usage",
                                      # "rights": 0o444,
                                      "type": DataType.INT,
                                      "interval": 10,
                                      "call": self.ram_usage}

        inputs['system/disk_usage'] = {"description": "disk usage",
                                       # "rights": 0o444,
                                       "type": DataType.INT,
                                       "interval": 600,
                                       "call": self.disk_usage}

        inputs['system/cpu_seconds'] = {"description": "spend time in scnds",
                                        # "rights": 0o444,
                                        "type": DataType.INT,
                                        "interval": 60,
                                        "call": self.get_cpu_seconds}

        inputs['system/uptime'] = {"description": "uptime in seconds",
                                   # "rights": 0o444,
                                   "type": "int",
                                   "interval": 60,
                                   "call": self.get_uptime}

        inputs['system/netdevs'] = {"description": "available network devices",
                                    # "rights": 0o444,
                                    "type": DataType.STRING,
                                    "interval": 0,
                                    "value": self.get_net_devs(),
                                    "call": self.get_net_devs}

        return inputs

    @staticmethod
    def is64bit():
        return int(sys.maxsize > 2**32)  # is 64bits

    @staticmethod
    def get_ip4_address(ifname):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
               s.fileno(), 0x8915,  # SIOCGIFADDR
               struct.pack('256s', bytes(ifname[:15], 'utf-8'))
               )[20:24])
        except OSError:
            return -1

    @staticmethod
    def get_cpu_freq():
        cpus = []
        if os.path.isdir('/sys/devices/system/cpu/'):
            for cpu in glob.iglob('/sys/devices/system/cpu/cpu*'):
                if os.path.isfile(cpu + '/cpufreq/scaling_cur_freq'):
                    with open(cpu + '/cpufreq/scaling_cur_freq') as cpu_file:
                        cpus.append(int(next(cpu_file).rstrip()))
        return cpus

    @staticmethod
    def cpu_usage():
        # /proc/loadavg maybe better for processcount
        return (os.getloadavg()[0] / os.cpu_count() * 100)

    @staticmethod
    def ram_usage():
        # total        used        free      shared  buff/cache   available
        # for future /proc/meminfo
        return (os.popen('free').readlines()[1].split())[1:]

    @staticmethod
    def disk_usage():
        # total used free
        # /proc/diskstats for io rates
        return list(shutil.disk_usage("/"))

    @staticmethod
    def get_cpu_seconds(stat_path='/proc/stat'):
        if os.path.isfile(stat_path):
            with open(stat_path) as stat_file:
                return next(stat_file).split()[1:]

    @staticmethod
    def get_uptime(stat_path='/proc/uptime'):
        if os.path.isfile(stat_path):
            with open(stat_path) as stat_file:
                return int(float(next(stat_file).split()[0]))

    @staticmethod
    def get_net_devs(stat_path='/proc/net/dev'):
        netdevs = []
        if os.path.isfile(stat_path):
            with open(stat_path) as net_file:
                net_file.readline()
                net_file.readline()
                # ['name',
                # 'received', 'packets', 'errs', 'drop', 'fifo', 'frame', 'compressed', 'multicast',
                # 'transmit, 'packets', 'errs', 'drop', 'fifo', 'colls', 'carrier', 'compressed']
                # print(re.split('\s+\||\s+|\|',net_file.readline().strip()))
                while True:
                    line = net_file.readline()
                    if line:
                        netdevs.append(re.split(r'\s+|:\s+', line.strip())[0])
                        # print(netdevs[-1])
                    else:
                        break
        return netdevs


SystemInfo = _SystemInfo()
