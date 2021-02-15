#!/usr/bin/env python3
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
from subprocess import Popen, PIPE
from core.DataTypes import DataType
from core.Toolbox import netmaskbytes_to_prefixlen, ipbytes_to_ipstr, IPEndpoint, lookup_oui
import logging
from core.Property import EntityProperty

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
        # self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, bytes(self._name, encoding="ascii"))
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
        raw = fcntl.ioctl(self._sock.fileno(), SIOCGIFNETMASK,
                          struct.pack("16s16x", bytes(self._name, encoding="ascii")))
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
       try:
        raw = fcntl.ioctl(self._sock.fileno(), SIOCGIFADDR, struct.pack('256s', bytes(self._name, encoding="ascii")))
        ip_bytes = raw[20:24]
        return ip_bytes
       except Exception as e:
           logging.error(str(e))
           return None

    @property
    def ip_human(self) -> str:
        return ipbytes_to_ipstr(self.ip)

    @property
    def mac_address(self) -> bytes:
        ifreq = struct.pack('16sH14s', bytes(self._name, encoding="ascii"), socket.AF_UNIX, b'\x00' * 14)
        raw = fcntl.ioctl(self._sock.fileno(), SIOCGIFHWADDR, ifreq)

        mac_bytes = raw[18:24]
        return mac_bytes

    @property
    def mac_address_human(self) -> str:
        return ":".join(['%02X' % byte for byte in self.mac_address])

    def cidr(self) -> str:
        return f"{self.ip_human}/{self.mask_prefix_length}"

    def endpoint(self) -> IPEndpoint:
        return IPEndpoint(self.ip_human, socket.gethostname(), self.mac_address_human, lookup_oui(self.mac_address),
                          self._name)

    def scan(self):
        if self._scanthread.is_alive():
            return

        self._scanthread.start()

    def _scan_thread_func(self):
        ip_list: Dict[str, List[str, str, str]] = {}

        p = Popen(['nmap', '-sn', self.cidr(), '--unprivileged', '-oG', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE,
                  encoding="utf8")
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
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line: {line_number}')

            pass


class Network(QObject):

    version = "1.0"
    required_packages = None
    allow_instances = False
    allow_maininstance = True
    description = "Network Module"

    def __init__(self, settings):


        self.network_devices: Dict[str, InterfaceInfo] = {ifname: InterfaceInfo(ifname) for ifname in SystemInfo.get_net_devs()}

        for netdev in self.network_devices.values():
            netdev.scan()


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



    @Slot()
    def start_scan_hosts(self):
        for netdev in self.wifi_devices:
                threading.Thread(target=self.scan_hosts, args=(netdev,)).start()



    def get_inputs(self) -> dict:
        return self.module_inputs


    @Signal
    def hostsChanged(self):
        pass


    def scan_hosts(self, device):
      try:

        p = Popen(['nmap', '-sn', str(SystemInfo.get_ip4_address(device))+'/24'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        #'sudo', '-S',
        #stdout_data = p.communicate(input=b'password')[0].split(b'\n')
        stdout_data = p.communicate()[0].split(b'\n')

        found_hosts =  list(self._network_hosts.keys())

        for key in found_hosts:

            if 'dev' in self._network_hosts[key]: # because helper list in dictionary for qml
                if self._network_hosts[key]['dev'] == device:
                    del self._network_hosts[key]

        for line in stdout_data:
            output = re.search(b'Nmap scan report for ([^ ]*) \(([^\)]*)\)', line)
            if output:
                    ip = output.group(2).decode()
                    self._network_hosts[ip] = {'ip':ip, 'hostname':output.group(1).decode(), 'dev' : device}
            else:
                output = re.search(b'Nmap scan report for ([^\n]*)', line)
                if output:
                    ip = output.group(1).decode()
                    self._network_hosts[ip] = {'ip': ip, 'dev' : device}
            output = re.search(b'Host is up \(([^ ]*) latency\)', line)
            if output:
                self._network_hosts[ip]['latency'] = output.group(1).decode()
            output = re.search(b'MAC Address: ([^ ]*) \(([^\)]*)\)', line)
            if output:
                self._network_hosts[ip]['mac'] = output.group(1).decode()
                self._network_hosts[ip]['manufacturer'] = output.group(2).decode()
        self.hostsChanged.emit()
      except Exception as e:
          logging.error(str(e))


    @Property('QVariantMap', notify=hostsChanged)
    def network_hosts(self):
        if 'list' in self._network_hosts:
            del self._network_hosts['list']
        self._network_hosts['list'] = list(self._network_hosts.keys())
        return (self._network_hosts)

    @Signal
    def devicesChanged(self):
        pass

    @Property('QVariantList', notify=devicesChanged)
    def devices(self):
        return self.wifi_devices


    @Signal
    def networksChanged(self):
        pass

    @Property(QObject, notify=networksChanged)
    def networks(self):
        return self._networks

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


