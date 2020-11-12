import sys
import platform
import os
import socket
import fcntl
import struct
import shutil
import re
import glob
import time

#cat /proc/net/wireless
#iwconfig wlan0
#iw dev wlan0 link
#iw dev wlan0 station dump -v

class SystemInfo():

    diskstats = dict()
    last_diskstat = 0


    @classmethod
    def update_diskstats(self,stat_path = '/proc/diskstats'):
        if os.path.isfile(stat_path):
         acttime = (time.time())
         quotient = acttime - SystemInfo.last_diskstat
         SystemInfo.last_diskstat = acttime

         with open(stat_path) as stat_file:
           while True:
            line = stat_file.readline().split()
            if line:
                if not line[2].startswith('loop'): # only physical devices
                 try:
                    SystemInfo.diskstats['system/disk_' + line[2] + '/read_bps']['value'] = (int(line[3]) -
                          SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs']['value']) // quotient


                    SystemInfo.diskstats['system/disk_' + line[2] + '/write_bps']['value'] = (int(line[7]) -
                           SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs']['value']) // quotient

                 except: #KeyError or Divsion Zero possible
                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_bps'] =  dict()
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_bps'] = dict()
                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs'] =  dict() 
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs'] = dict()

                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_bps']['value'] =  0
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_bps']['value'] = 0
                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs']['value'] =  0
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs']['value'] = 0

                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_bps']['interval'] =  -1
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_bps']['interval'] = -1
                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs']['interval'] =  -1
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs']['interval'] = -1

                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_bps']['type'] =  'int'
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_bps']['type'] = 'int'
                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs']['type'] =  'int'
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs']['type'] = 'int'

                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_bps']['description'] =  'read bytes per second'
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_bps']['description'] = 'write bytes per second'
                     SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs']['description'] =  'absolute read bytes'
                     SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs']['description'] = 'absolute written bytes'

                 SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs']['value'] = int(line[3])
                 SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs']['value'] = int(line[7])
                 SystemInfo.diskstats['system/disk_' + line[2] + '/write_abs']['lastupdate'] = acttime
                 SystemInfo.diskstats['system/disk_' + line[2] + '/read_abs']['lastupdate'] = acttime
                 SystemInfo.diskstats['system/disk_' + line[2] + '/write_bps']['lastupdate'] = acttime
                 SystemInfo.diskstats['system/disk_' + line[2] + '/read_bps']['lastupdate'] = acttime

            else:
                break


    @staticmethod
    def update():
        if SystemInfo.last_diskstat + 10 < time.time():
            SystemInfo.update_diskstats()


    @staticmethod
    def get_discstats():
        return SystemInfo.diskstats


    @staticmethod
    def get_inputs() -> dict:

        SystemInfo.update_diskstats() #init disk dict

        systeminputs  = SystemInfo.diskstats

        systeminputs['system/is64bit'] = dict({"description" : "64bit system?",
                                                #"rights" : 0o444,
                                                "type" : "bool",
                                                "interval" : 0,
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
                                                "interval" : 0,
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



