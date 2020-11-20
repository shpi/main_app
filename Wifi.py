#!/usr/bin/env python3

import os
import time
from subprocess import check_output,call, Popen, PIPE, DEVNULL
from PySide2.QtCore import QSettings, Qt, QModelIndex, QAbstractListModel, Property, Signal, Slot, QObject, QUrl, QUrlQuery


class WifiNetworkModel(QAbstractListModel):
    BSSIDRole = Qt.UserRole + 1000
    SSIDRole = Qt.UserRole + 1001
    SignalRole = Qt.UserRole + 1002
    FlagsRole = Qt.UserRole + 1003
    FrequencyRole = Qt.UserRole + 1004

    def __init__(self, entries=[], active='', parent=None):
        super(WifiNetworkModel, self).__init__(parent)
        self._entries = entries

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self._entries[index.row()]
            if role == WifiNetworkModel.BSSIDRole:
                return item["bssid"]
            elif role == WifiNetworkModel.SSIDRole:
                return item["ssid"]
            elif role == WifiNetworkModel.SignalRole:
                return Wifi.dbmtoperc[int(item["signal"])]
            elif role == WifiNetworkModel.FlagsRole:
                return item["flags"]
            elif role == WifiNetworkModel.FrequencyRole:
                return item["frequency"]

    def roleNames(self):

        roles = {WifiNetworkModel.BSSIDRole: b"bssid",
                 WifiNetworkModel.SSIDRole: b"ssid",
                 WifiNetworkModel.FlagsRole: b"flags",
                 WifiNetworkModel.SignalRole: b"signal",
                 WifiNetworkModel.FrequencyRole: b"frequency"}

        return roles

    def appendRow(self, n):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._entries.append(n)
        self.endInsertRows()


class Wifi(QObject):

    def __init__(self, parent: QObject = None):

        super(Wifi, self).__init__(parent)
        self.inputs = dict()
        self._networks = WifiNetworkModel()
        self.found_devices = []
        self.read_signal()
        self.scan_wifi('wlan1')

    def update(self):
        self.read_signal()

    def get_inputs(self) -> dict:
        return self.inputs

    @Signal
    def networksChanged(self):
           pass

    @Property(QObject, notify=networksChanged)
    def networks(self):
           return self._networks

    @Slot(str)
    def scan_wifi(self, device=''):
        networks = []
        retry = 5
        while retry > 0:
            try:
             if b'OK' in check_output(["wpa_cli","-i", device, "scan"], stderr=DEVNULL):
                retry = 0
                print('ok in wpa_cli scan')
                record_details = Popen(["wpa_cli","-i", device, "scan_results"], stdout=PIPE).communicate()[0].decode()
                record_details = record_details.strip().split('\n')
                record_details.pop(0)

                for record in record_details:
                    record = record.split('\t')
                    networks.append( {'bssid':record[0], 'frequency':record[1], 'signal': record[2].rstrip('.'), 'flags': record[3], 'ssid': record[4]})

                self._networks = WifiNetworkModel(networks)

                self.networksChanged.emit()
             else: time.sleep(1)
            except:
                retry -=1
                print('missing rights for wpa_cli')

    @Slot(str,str,str,str,str)
    def write_settings(self,device='',flags='',bssid='',ssid='',passwd=''):

        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
            f.write('country=US\n')
            f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
            f.write('update_config=1\n')
            f.write('network={\n')
            f.write('ssid="' + ssid + '"\n')
            if bssid != '':    f.write('bssid="' + bssid + '"\n')
            if 'ssid' == '':  f.write('scan_ssid=1\n')

            if   'WPA2' in flags:    f.write('psk="' + passwd + '"\n')
            elif 'WEP' in flags:
                                   f.write('wep_tx_keyidx=0\n')
                                   f.write('wep_key0="' +   passwd + '"\n')
                                   f.write('key_mgmt=NONE\n')
            elif 'WPA' in flags:
                                   f.write('psk="' + peripherals.eg_object.usertext + '"\n')
                                   f.write('pairwise=CCMP\n')
                                   f.write('group=TKIP\n')
            else:                  f.write('key_mgmt=NONE\n')

            f.write('}')
            call(['wpa_cli','-i', device, 'reconfigure'])
            call(['dhclient', device])
            # systemctl restart dhcpcd


    def read_signal(self):
        for device in self.found_devices:  # reset values before checking
            self.inputs[f'wifi/{device}/link']['value'] = 0
            self.inputs[f'wifi/{device}/link']['status'] = 0
            self.inputs[f'wifi/{device}/link']['level'] = 0
            self.inputs[f'wifi/{device}/link']['noise'] = 0

        if os.path.isfile('/proc/net/wireless'):
            with open('/proc/net/wireless', 'r') as rf:
                line = rf.readline()
                while line:
                    line = (rf.readline().rstrip().split())
                    if line and line[0].startswith('wlan'):
                        device = line[0].rstrip(":")
                        if device not in self.found_devices:
                            self.found_devices.append(device)
                        if f'wifi/{device}/link' not in self.inputs:
                            self.inputs[f'wifi/{device}/link'] = {'description': f'link quality of device {line[0].rstrip(":")}', 
                                                                               'interval': -1, 'lastupdate':0}
                        self.inputs[f'wifi/{device}/link']['value'] = self.dbmtoperc[int(line[3].rstrip('.'))]
                        self.inputs[f'wifi/{device}/link']['status'] = line[1]
                        self.inputs[f'wifi/{device}/link']['quality'] = line[2]
                        self.inputs[f'wifi/{device}/link']['noise'] = line[4]
                        self.inputs[f'wifi/{device}/link']['lastupdate'] = time.time()

            rf.close()


    dbmtoperc =         {-1: 100,  -26: 98, -51: 78, -76: 38,
                         -2: 100,  -27: 97, -52: 76, -77: 36,
                         -3: 100,  -28: 97, -53: 75, -78: 34,
                         -4: 100,  -29: 96, -54: 74, -79: 32,
                         -5: 100,  -30: 96, -55: 73, -80: 30,
                         -6: 100,  -31: 95, -56: 71, -81: 28,
                         -7: 100,  -32: 95, -57: 70, -82: 26,
                         -8: 100,  -33: 94, -58: 69, -83: 24,
                         -9: 100,  -34: 93, -59: 67, -84: 22,
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
                         -21: 99,  -46: 83, -71: 48, -96: 1,
                         -22: 99,  -47: 82, -72: 46, -97: 1,
                         -23: 99,  -48: 81, -73: 44, -98: 1,
                         -24: 98,  -49: 80, -74: 42, -99: 1,
                         -25: 98,  -50: 79, -75: 40, -100: 1}


def main():
    """Module's main method."""

    wifi = Wifi()
    print(wifi.scan_wifi('wlan1'))


if __name__ == "__main__":
    main()
