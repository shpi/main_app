import sys
import os
import socket
import fcntl
import struct
import shutil
import re
import glob
import time
import threading
from typing import List, Dict
from subprocess import Popen, PIPE, DEVNULL
from core.DataTypes import DataType
from core.Toolbox import netmaskbytes_to_prefixlen, ipbytes_to_ipstr, IPEndpoint, lookup_oui

_re_ifname = re.compile(r'\s*(\S+):')
_re_ifname_w_stats = re.compile(r'\s*(\S+):' + (r'\s+(\d+)' * 16))  # 16 stat columns

# "Host: 192.168.51.31 (DVS-605-Series-0D-27-D6.fritz.box)"
_re_scanreport = re.compile(r'Host: (\S+) \((.*)\)')

# "192.168.51.5     0x1         0x2         9c:1c:12:ca:de:27     *        enp4s0"
_re_arp = re.compile(r'(\S+).*(\S{2}:\S{2}:\S{2}:\S{2}:\S{2}:\S{2})')


SIOCGIFNETMASK = 0x891b
SIOCGIFHWADDR = 0x8927
SIOCGIFADDR = 0x8915


class InterfaceInfo:
    def __init__(self, interface: str):
        self._name = interface
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, bytes(self._name, encoding="ascii"))
        self._endpoints = []
        self._scanthread = threading.Thread(target=self._scan_thread_func)

    @property
    def endpoints(self) -> List[IPEndpoint]:
        return self._endpoints

    @property
    def name(self):
        return self._name

    @property
    def mask(self) -> bytes:
        raw = fcntl.ioctl(self._sock.fileno(), SIOCGIFNETMASK, struct.pack("16s16x", bytes(self._name, encoding="ascii")))
        subnet_bytes = raw[20:24]
        return subnet_bytes

    @property
    def mask_human(self) -> str:
        return ipbytes_to_ipstr(self.mask)

    @property
    def mask_prefix_length(self) -> int:
        return netmaskbytes_to_prefixlen(self.mask)

    @property
    def ip(self) -> bytes:
        raw = fcntl.ioctl(self._sock.fileno(), SIOCGIFADDR, struct.pack('256s', bytes(self._name, encoding="ascii")))
        ip_bytes = raw[20:24]
        return ip_bytes

    @property
    def ip_human(self) -> str:
        return ipbytes_to_ipstr(self.ip)

    @property
    def mac_address(self) -> bytes:
        ifreq = struct.pack('16sH14s', bytes(self._name, encoding="ascii"), socket.AF_UNIX, b'\x00'*14)
        raw = fcntl.ioctl(self._sock.fileno(), SIOCGIFHWADDR, ifreq)

        mac_bytes = raw[18:24]
        return mac_bytes

    @property
    def mac_address_human(self) -> str:
        return ":".join(['%02X' % byte for byte in self.mac_address])

    def cidr(self) -> str:
        return f"{self.ip_human}/{self.mask_prefix_length}"

    def endpoint(self) -> IPEndpoint:
        return IPEndpoint(self.ip_human, socket.gethostname(), self.mac_address_human, lookup_oui(self.mac_address), self._name)

    def scan(self):
        if self._scanthread.is_alive():
            return

        self._scanthread.start()

    def _scan_thread_func(self):
        ip_list: Dict[str, List[str, str, str]] = {}

        p = Popen(['nmap', '-sn', self.cidr(), '--unprivileged', '-oG', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE, encoding="utf8")
        stdout_data = p.communicate()[0]

        for line in stdout_data.splitlines(False):
            m = _re_scanreport.match(line)
            if m:
                ip_list[m.group(1)] = [m.group(2), "", ""]

        with open("/proc/net/arp") as arps:
            for arp in arps:
                m = _re_arp.match(arp)
                if m:
                    ip = m.group(1)
                    if ip in ip_list:
                        mac = m.group(2)
                        sublist = ip_list[ip]
                        sublist[1] = mac
                        sublist[2] = lookup_oui(mac)

        self._endpoints.clear()
        for ip, data in ip_list.items():
            self._endpoints.append(IPEndpoint(ip, *data, self._name))

    def __del__(self):
        try:
            self._sock.close()
        except Exception:
            pass


class SystemInfo:
    _keys = 'read_bps', 'write_bps', 'read_abs', 'write_abs'

    def __init__(self, parent=None):
        super().__init__()
        self.module_inputs = dict()
        self.last_diskstat = 0
        self.interval = 60
        self.update(init=True)

        self.network_devices: Dict[str, InterfaceInfo] = \
            {ifname: InterfaceInfo(ifname) for ifname in SystemInfo.get_net_devs()}

        for netdev in self.network_devices.values():
            netdev.scan()

    def update(self, stat_path='/proc/diskstats', init=False):
        if not os.path.isfile(stat_path):
            logging.error(stat_path + ' does not exists.')
            return

        acttime = time.time()
        quotient = acttime - self.last_diskstat
        self.last_diskstat = acttime

        with open(stat_path) as stat_file:
            for line in stat_file:
                line = line.split()
                if not line:
                    continue

                if line[2].startswith('loop') or line[2].startswith('ram'):
                    # only physical devices
                    continue

                if init:
                    self.module_inputs[f'system/disk_{line[2]}/read_bps'] = {'value': 0,
                                                                         'interval': -1,
                                                                         'type': DataType.INT,
                                                                         'description': 'read bytes per second'}

                    self.module_inputs[f'system/disk_{line[2]}/write_bps'] = {'value': 0,
                                                                          'interval': -1,
                                                                          'type': DataType.INT,
                                                                          'description': 'write bytes per second'}
                    self.module_inputs[f'system/disk_{line[2]}/read_abs'] = {'value': 0,
                                                                         'interval': -1,
                                                                         'type': DataType.INT,
                                                                         'description': 'read bytes absolute'}
                    self.module_inputs[f'system/disk_{line[2]}/write_abs'] = {'value': 0,
                                                                          'interval': -1,
                                                                          'type': DataType.INT,
                                                                          'description': 'write bytes absolute'}

                self.module_inputs[f'system/disk_{line[2]}/read_bps']['value'] = (int(line[3]) -
                                                                              self.module_inputs[f'system/disk_{line[2]}/read_abs']['value']) // quotient

                self.module_inputs[f'system/disk_{line[2]}/write_bps']['value'] = (int(line[7]) -
                                                                               self.module_inputs[f'system/disk_{line[2]}/write_abs']['value']) // quotient

                self.module_inputs[f'system/disk_{line[2]}/read_abs']['value'] = int(line[3])
                self.module_inputs[f'system/disk_{line[2]}/write_abs']['value'] = int(line[7])

                for key in self._keys:
                    self.module_inputs[f'system/disk_{line[2]}/{key}']['lastupdate'] = acttime



    def get_discstats(self):
        return self.module_inputs

    def get_inputs(self) -> dict:
        inputs = self.module_inputs

        inputs['system/is64bit'] = {"description": "64bit system?",
                                    # "rights":0o444,
                                    "type": DataType.BOOL,
                                    "interval": 0,
                                    "value": self.is64bit(),
                                    "call": self.is64bit}

        inputs['system/cpu_freq'] = {"description": "actual CPU clock",
                                     # "rights": 0o444,
                                     "type": DataType.INT,
                                     "interval": 60,
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
                                   "type": DataType.INT,
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
            return ipbytes_to_ipstr(fcntl.ioctl(
                s.fileno(), SIOCGIFADDR,
                struct.pack('256s', bytes(ifname[:15], 'ascii'))
            )[20:24])
        except OSError as e:
            logging.error(str(e))
            return -1

    @staticmethod
    def get_cpu_freq():
        """
        This function seems to be very slow, use with care
        """
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
        return os.getloadavg()[0] / os.cpu_count() * 100

    @staticmethod
    def ram_usage():
        # total        used        free      shared  buff/cache   available
        # for future /proc/meminfo
        return (os.popen('free').readlines()[1].split())[1:]

    @staticmethod
    def disk_usage():
        # total used free
        # /proc/module_inputs for io rates
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
    def get_net_devs(stat_path='/proc/net/dev', with_lo=False):
        netdevs = []
        if not os.path.isfile(stat_path):
            return

        with open(stat_path) as net_file:
            # ['name',
            # 'received', 'packets', 'errs', 'drop', 'fifo', 'frame', 'compressed', 'multicast',
            # 'transmit, 'packets', 'errs', 'drop', 'fifo', 'colls', 'carrier', 'compressed']
            """
            Inter-|   Receive                                                |  Transmit
             face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
                lo:   84522     961    0    0    0     0     0         0    84522     961    0    0    0     0       0          0
            enp4s0: 402485511 4188225    0    0    0     0    0      1891 232774205 4096081    0    0    0     0       0          0
            wlp5s0u4u2u2:  605332    8593    0    0    0     0    0   0    94686     462    0    0    0     0       0          0
            """
            for line in net_file:
                # match = _re_ifname_w_stats.match(line)
                match = _re_ifname.match(line)

                if match:
                    # print(match.groups())
                    ifname = match.group(1)
                    if with_lo or ifname != "lo":
                        netdevs.append(ifname)
        return netdevs


