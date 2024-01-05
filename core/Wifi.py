#!/usr/bin/env python3
import logging
import os
import sys
import threading
import time
from subprocess import check_output, Popen, PIPE, DEVNULL

from PySide2.QtCore import QSettings, Qt, QModelIndex, QAbstractListModel, Property, Signal, Slot, QObject

from core.DataTypes import DataType
from core.Property import EntityProperty


class WifiNetworkModel(QAbstractListModel):
    BSSIDRole = Qt.UserRole + 1000
    SSIDRole = Qt.UserRole + 1001
    SignalRole = Qt.UserRole + 1002
    FlagsRole = Qt.UserRole + 1003
    FrequencyRole = Qt.UserRole + 1004
    PasswordRole = Qt.UserRole + 1005

    def __init__(self, entries=[], settings: QSettings = None, active='', parent=None):
        super(WifiNetworkModel, self).__init__(parent)
        self._entries = entries
        self.settings = settings

    def rowCount(self, parent=None):
        # if parent.isValid():
        #    return 0
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self._entries[index.row()]
            if role == WifiNetworkModel.BSSIDRole:
                return item[b"bssid"]
            elif role == WifiNetworkModel.SSIDRole:
                return item[b"ssid"]
            elif role == WifiNetworkModel.SignalRole:
                return Wifi.dbmtoperc[int(item[b"signal"])]
            elif role == WifiNetworkModel.FlagsRole:
                if 'WPA2' in item[b'flags']:
                    return 'WPA2'
                elif 'WPA' in item[b'flags']:
                    return 'WPA'
                elif 'WEP' in item[b'flags']:
                    return 'WEP'
                else:
                    return 'OPEN'
            elif role == WifiNetworkModel.PasswordRole:
                return self.settings.value("wifi/password/" + item[b"bssid"], "")

            elif role == WifiNetworkModel.FrequencyRole:
                if int(item[b"frequency"]) in Wifi.freqtochn:
                    return Wifi.freqtochn[int(item[b"frequency"])]
                else:
                    return item[b"frequency"]

    def roleNames(self):

        roles = {WifiNetworkModel.BSSIDRole: b"bssid",
                 WifiNetworkModel.SSIDRole: b"ssid",
                 WifiNetworkModel.FlagsRole: b"flags",
                 WifiNetworkModel.SignalRole: b"signal",
                 WifiNetworkModel.PasswordRole: b"password",
                 WifiNetworkModel.FrequencyRole: b"frequency"}

        return roles

    def appendRow(self, n):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._entries.append(n)
        self.endInsertRows()


class Wifi(QObject):
    version = "1.0"
    required_packages = None
    allow_instances = False
    allow_maininstance = True
    description = "Wifi Module for managing WPA supplicant"

    def __init__(self, settings):

        super(Wifi, self).__init__()
        self.settings = settings
        self.changing_wpa = True
        self.properties = dict()
        self.wifi_devices = Wifi.get_wifi_devs()

        self._networks = WifiNetworkModel([], self.settings)
        self._wpa_state = ''
        self._wpa_bssid = ''
        self._wpa_ssid = ''
        self._wpa_ip = ''
        self._wpa_type = ''
        self.wpa_device = None

        self.properties['module'] = EntityProperty(
                                                   category='module',
                                                   name='wifi',
                                                   value='NOT_INITIALIZED',
                                                   description='WIFI WPA supplicant module',
                                                   type=DataType.MODULE,
                                                   call=self.read_signal,
                                                   interval=30)

        self.read_signal()

        if len(self.wifi_devices):
            self.wpa_device = self.wifi_devices[0]  # initial value
            self.wpa_status(self.wpa_device)

    @staticmethod
    def get_wifi_devs(stat_path='/proc/net/dev'):
        wifidevs = []
        if not os.path.isfile(stat_path):
            return wifidevs

        with open(stat_path) as net_file:
            for line in net_file:
                a = line.find(':')
                if a > -1:
                    netdev = line[:a].strip()
                    if netdev.startswith('wlan'):
                        wifidevs.append(netdev)
        return wifidevs

    def get_inputs(self) -> list:
        return self.properties.values()

    @Signal
    def networksChanged(self):
        # for updating list after wifi scan
        pass

    @Signal
    def wifi_devicesChanged(self):
        # for updating device list before scan
        pass

    @Signal
    def wpa_statusChanged(self):
        # for wpa status of selected device
        pass

    @Signal
    def signalsChanged(self):
        # signal for frequently signal read of all devices
        pass

    @Property('QVariantList', notify=wifi_devicesChanged)
    def devices(self):
        return self.wifi_devices

    @Slot()
    @Slot(str)
    def scan_wifi(self, device='wlan0'):
        self.wifi_devices = Wifi.get_wifi_devs()
        self.wifi_devicesChanged.emit()

        if len(self.wifi_devices) > 0 and device in self.wifi_devices:  # and device.startswith('wlan'):
            scanthread = threading.Thread(target=self._scan_wifi, args=(device,))
            scanthread.start()

    def _scan_wifi(self, device):
        networks = []
        retry = 3
        while retry > 0:
            try:
                if b'OK' in check_output(["wpa_cli", "-i", device, "scan"], stderr=DEVNULL):
                    retry = 0
                    record_details = Popen(["wpa_cli", "-i", device, "scan_results"], stdout=PIPE).communicate()[
                        0].decode()
                    record_details = record_details.strip().split('\n')
                    record_details.pop(0)

                    for record in record_details:
                        record = record.split('\t')
                        if len(record) < 5:
                            record.append('')
                        networks.append({b'device': device, b'bssid': record[0],
                                         b'frequency': record[1], b'signal': record[2].rstrip('.'),
                                         b'flags': record[3], b'ssid': record[4]})

                else:
                    time.sleep(0.2)
                    retry -= 1
            except Exception as e:
                retry -= 1
                exception_type, exception_object, exception_traceback = sys.exc_info()
                line_number = exception_traceback.tb_lineno
                logging.error(f'{e} in line {line_number}')
        self._networks = WifiNetworkModel(networks, self.settings)
        self.networksChanged.emit()

    @Slot(str)
    def wpa_status(self, device):
        if not self.changing_wpa:
            self.wpa_state = 'WPA reinit'

        try:
            output = check_output(
                ['wpa_cli', '-i', device, 'status']).split(b'\n')

            for line in output:
                if line.startswith(b'wpa_state='):
                    self._wpa_state = line[10:].rstrip().decode()
                if line.startswith(b'bssid='):
                    self._wpa_bssid = line[6:].rstrip().decode()
                if line.startswith(b'ssid='):
                    self._wpa_ssid = line[5:].rstrip().decode()
                if line.startswith(b'ip_address='):
                    self._wpa_ip = line[11:].rstrip().decode()
                if line.startswith(b'key_mgmt='):
                    self._wpa_type = line[9:].rstrip().decode()

                self.wpa_device = device

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'{e} in line {line_number}')
            self._wpa_state = 'ERROR'

        self.wpa_statusChanged.emit()

    @Property(str, notify=wpa_statusChanged)
    def wpa_state(self):
        return self._wpa_state

    @Property(str, notify=wpa_statusChanged)
    def wpa_bssid(self):
        return self._wpa_bssid

    @Property(str, notify=wpa_statusChanged)
    def wpa_ssid(self):
        return self._wpa_ssid

    @Property(str, notify=wpa_statusChanged)
    def wpa_ip(self):
        return self._wpa_ip

    @Property(str, notify=wpa_statusChanged)
    def wpa_type(self):
        return self._wpa_type

    @Property(QObject, notify=networksChanged)
    def networks(self):
        return self._networks

    @Property(int, notify=signalsChanged)
    def signal(self):
        if self.wpa_device in self.properties:
            return self.properties[self.wpa_device].value
        else:
            return 0

    @Slot(str, str, str, str, str, bool)
    def write_settings(self, device='', flags='', bssid='', ssid='', passwd='', fixbssid=False):
        scanthread = threading.Thread(target=self._write_settings, args=(device, flags, bssid, ssid, passwd, fixbssid))
        scanthread.start()

    # Thread
    def _write_settings(self, device='', flags='', bssid='', ssid='', passwd='', fixbssid=False):
        try:
            self.changing_wpa = False

            self.settings.setValue("wifi/password/" + bssid, passwd)
            with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:

                f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
                f.write('update_config=1\n')
                f.write('country=US\n')
                f.write('network={\n')
                f.write('ssid="' + ssid + '"\n')
                if fixbssid:
                    f.write('bssid=' + bssid + '\n')
                if 'ssid' == '':
                    f.write('scan_ssid=1\n')

                if 'WPA2' in flags:
                    f.write('psk="' + passwd + '"\n')
                elif 'WEP' in flags:
                    f.write('wep_tx_keyidx=0\n')
                    f.write('wep_key0="' + passwd + '"\n')
                    f.write('key_mgmt=NONE\n')
                elif 'WPA' in flags:
                    f.write('psk="' + passwd + '"\n')
                    f.write('pairwise=CCMP\n')
                    f.write('group=TKIP\n')
                else:
                    f.write('key_mgmt=NONE\n')

                f.write('}')

            Popen(['wpa_cli', '-i', device, 'reconfigure'], shell=False, stdin=None, stdout=None, stderr=None)
            # logging.error(check_output(['systemctl', 'restart', 'dhcpcd.service'], encoding='UTF-8'))
            self.changing_wpa = True
            self.wpa_status(device)

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'{e} in line {line_number}')

    def read_signal(self):
        if self.wpa_device is not None:
         self.wpa_status(self.wpa_device)
        if os.path.isfile('/proc/net/wireless'):
            with open('/proc/net/wireless', 'r') as rf:
                line = rf.readline()
                while line:
                    line = (rf.readline().rstrip().split())
                    if line and line[0].startswith('wlan'):
                        device = line[0].rstrip(":")
                        if device not in self.wifi_devices:
                            self.wifi_devices.append(device)
                        if f'{device}' not in self.properties:
                            self.properties[f'{device}'] = EntityProperty(
                                                                          category='system',
                                                                          name= 'wifi_' + device,
                                                                          value=0,
                                                                          description='WIFI signal in %',
                                                                          type=DataType.PERCENT_INT,
                                                                          interval=-1)

                        # {'description': f'link quality of device {line[0].rstrip(":")}'}
                        self.properties[f'{device}'].value = self.dbmtoperc[int(line[3].rstrip('.'))]
                        # self.properties[f'{device}']['status'] = line[1]
                        # self.properties[f'{device}']['quality'] = line[2]
                        # self.properties[f'{device}']['noise'] = line[4]

            self.signalsChanged.emit()
            return 'OK'
        return 'ERROR'

    dbmtoperc = {-1: 100, -26: 98, -51: 78, -76: 38,
                 -2: 100, -27: 97, -52: 76, -77: 36,
                 -3: 100, -28: 97, -53: 75, -78: 34,
                 -4: 100, -29: 96, -54: 74, -79: 32,
                 -5: 100, -30: 96, -55: 73, -80: 30,
                 -6: 100, -31: 95, -56: 71, -81: 28,
                 -7: 100, -32: 95, -57: 70, -82: 26,
                 -8: 100, -33: 94, -58: 69, -83: 24,
                 -9: 100, -34: 93, -59: 67, -84: 22,
                 -10: 100, -35: 93, -60: 66, -85: 20,
                 -11: 100, -36: 92, -61: 64, -86: 17,
                 -12: 100, -37: 91, -62: 63, -87: 15,
                 -13: 100, -38: 90, -63: 61, -88: 13,
                 -14: 100, -39: 90, -64: 60, -89: 10,
                 -15: 100, -40: 89, -65: 58, -90: 8,
                 -16: 100, -41: 88, -66: 56, -91: 6,
                 -17: 100, -42: 87, -67: 55, -92: 3,
                 -18: 100, -43: 86, -68: 53, -93: 1,
                 -19: 100, -44: 85, -69: 51, -94: 1,
                 -20: 100, -45: 84, -70: 50, -95: 1,
                 -21: 99, -46: 83, -71: 48, -96: 1,
                 -22: 99, -47: 82, -72: 46, -97: 1,
                 -23: 99, -48: 81, -73: 44, -98: 1,
                 -24: 98, -49: 80, -74: 42, -99: 1,
                 -25: 98, -50: 79, -75: 40, -100: 1}

    freqtochn = {2412: '2.4GHz 1', 2417: '2.4GHz 2',
                 2422: '2.4GHz 3', 2427: '2.4GHz 4',
                 2432: '2.4GHz 5', 2437: '2.4GHz 6',
                 2442: '2.4GHz 7', 2447: '2.4GHz 8',
                 2452: '2.4GHz 9', 2457: '2.4GHz 10',
                 2462: '2.4GHz 11', 2467: '2.4GHz 12',
                 2472: '2.4GHz 13', 2484: '2.4GHz 14',
                 5035: '5GHz 7', 5040: '5GHz 8',
                 5045: '5GHz 9', 5055: '5GHz 11',
                 5060: '5GHz 12', 5080: '5GHz 16',
                 5160: '5GHz 32', 5170: '5GHz 34',
                 5180: '5GHz 36', 5190: '5GHz 38',
                 5200: '5GHz 40', 5210: '5GHz 42',
                 5220: '5GHz 44', 5230: '5GHz 46',
                 5240: '5GHz 48', 5250: '5GHz 50',
                 5260: '5GHz 52', 5270: '5GHz 54',
                 5280: '5GHz 56', 5290: '5GHz 58',
                 5300: '5GHz 60', 5310: '5GHz 62',
                 5320: '5GHz 64', 5340: '5GHz 68',
                 5480: '5GHz 96', 5500: '5GHz 100',
                 5510: '5GHz 102', 5520: '5GHz 104',
                 5530: '5GHz 106', 5540: '5GHz 108',
                 5550: '5GHz 110', 5560: '5GHz 112',
                 5570: '5GHz 114', 5580: '5GHz 116',
                 5590: '5GHz 118', 5600: '5GHz 120',
                 5610: '5GHz 122', 5620: '5GHz 124',
                 5630: '5GHz 126', 5640: '5GHz 128',
                 5660: '5GHz 132', 5670: '5GHz 134',
                 5680: '5GHz 136', 5690: '5GHz 138',
                 5700: '5GHz 140', 5710: '5GHz 142',
                 5720: '5GHz 144', 5745: '5GHz 149',
                 5755: '5GHz 151', 5765: '5GHz 153',
                 5775: '5GHz 155', 5785: '5GHz 157',
                 5795: '5GHz 159', 5805: '5GHz 161',
                 5825: '5GHz 165', 5845: '5GHz 169',
                 5865: '5GHz 173', 4915: '5GHz 183',
                 4920: '5GHz 184', 4925: '5GHz 185',
                 4935: '5GHz 187', 4940: '5GHz 188',
                 4945: '5GHz 189', 4960: '5GHz 192',
                 4980: '5GHz 196'}
