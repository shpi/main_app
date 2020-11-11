import sys
import platform
import os
import socket
import fcntl
import struct
import shutil
import re
import glob

#cat /proc/net/wireless
#iwconfig wlan0
#iw dev wlan0 link
#iw dev wlan0 station dump -v

class SystemInfo():

    @staticmethod
    def get_inputs() -> dict:
        systeminputs = dict()
        systeminputs['system/is64bit'] = dict({"description" : "64bit system?",
                                                #"rights" : 0o444,
                                                "type" : "bool",
                                                "interval" : -1,
                                                "value" : SystemInfo.is64bit(),
                                                "call" : SystemInfo.is64bit})

        systeminputs['system/is64bit']['value'] = SystemInfo.is64bit()

        systeminputs['system/cpu_freq'] = dict({"description" : "actual CPU clock",
                                                #"rights" : 0o444,
                                                "type" : "list_int",
                                                "interval" : 10,
                                                "call" : SystemInfo.get_cpu_freq})

        systeminputs['system/cpu_usage'] = dict({"description" : "CPU usage %",
                                                #"rights" : 0o444,
                                                "type" : "percent",
                                                "interval" : 10,
                                                "call" : SystemInfo.cpu_usage})

        systeminputs['system/ram_usage'] = dict({"description" : "RAM usage",
                                                #"rights" : 0o444,
                                                "type" : "list_int",
                                                "interval" : 10,
                                                "call" : SystemInfo.ram_usage}) 

        systeminputs['system/disk_usage'] = dict({"description" : "disk usage",
                                                #"rights" : 0o444,
                                                "type" : "list_int",
                                                "interval" : 600,
                                                "call" : SystemInfo.disk_usage}) 

        systeminputs['system/cpu_seconds'] = dict({"description" : "cpu spend time in seconds",
                                                #"rights" : 0o444,
                                                "type" : "list_int",
                                                "interval" : 60,
                                                "call" : SystemInfo.get_cpu_seconds})


        systeminputs['system/uptime'] = dict({"description" : "uptime in seconds",
                                                #"rights" : 0o444,
                                                "type" : "int",
                                                "interval" : 60,
                                                "call" : SystemInfo.get_uptime}) 


        systeminputs['system/netdevs'] = dict({"description" : "available network devices",
                                                #"rights" : 0o444,
                                                "type" : "list_string",
                                                "interval" : -1,
                                                "value" : SystemInfo.get_net_devs(),
                                                "call" : SystemInfo.get_net_devs})


        return systeminputs

    @staticmethod
    def is64bit():
        return int(sys.maxsize > 2**32)  #is 64bits


    @staticmethod
    def get_ip4_address(ifname):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
               s.fileno(),0x8915,  # SIOCGIFADDR
               struct.pack('256s',  bytes(ifname[:15], 'utf-8'))
               )[20:24])
        except OSError:
            return -1

    @staticmethod
    def get_cpu_freq():
        cpus = []
        if os.path.isdir('/sys/devices/system/cpu/'):
            for cpu in glob.iglob('/sys/devices/system/cpu/cpu*',recursive = False):
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
        #total        used        free      shared  buff/cache   available
        # for future /proc/meminfo
        return (os.popen('free').readlines()[1].split())[1:]

    @staticmethod
    def disk_usage():
        #total used free
        # /proc/diskstats for io rates
        return list(shutil.disk_usage("/"))

    @staticmethod
    def get_cpu_seconds(stat_path='/proc/stat'):
        with open(stat_path) as stat_file:
            return next(stat_file).split()[1:]

    @staticmethod
    def get_uptime(stat_path='/proc/uptime'):
        with open(stat_path) as stat_file:
            return int(float(next(stat_file).split()[0]))

    @staticmethod
    def get_net_devs():
        with open('/proc/net/dev') as net_file:
            netdevs = []
            net_file.readline()
            net_file.readline()
            # ['face', 'received bytes', 'packets', 'errs', 'drop', 'fifo', 'frame', 'compressed', 'multicast',
            #          'transmit bytes', 'packets', 'errs', 'drop', 'fifo', 'colls', 'carrier', 'compressed']
            # print(re.split('\s+\||\s+|\|',net_file.readline().strip()))
            while True:
             line = net_file.readline()
             if line:
                 netdevs.append( re.split('\s+|:\s+',line.strip())[0] )
                 #print(netdevs[-1])
             else:
                 break
        return netdevs


