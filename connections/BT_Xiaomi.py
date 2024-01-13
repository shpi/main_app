# -*- coding: utf-8 -*-

import logging
from functools import partial
import threading
import time
import subprocess
import sys
import os
import signal
import struct
import json

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property

from core.DataTypes import Convert
from core.DataTypes import DataType
from core.Inputs import InputListModelDict
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix

MI_FLORA_HANDLE_FIRMWARE_AND_BATTERY = "0x38"
MI_FLORA_HANDLE_MODE_CHANGE = "0x33"
MI_FLORA_HANDLE_DATA_READ = "0x35"
MJ_HT_V1_HANDLE_DATA_READ = "0x10"
MJ_HT_V1_HANDLE_BATTERY = "0x18"




class BT_Xiaomi(QObject):

    singleton = 1
    scanningChanged = Signal(bool)



    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()

        self.name = "INSTANCE"  # this class has max. one instance!
        self.inputs = inputs
        self.settings = settings

        try:
            self._sensors = json.loads(settings.value("/module/connections/bt_xiaomi/sensors", "{}"))

        except Exception as e:
            # Handle the case where the string is not a valid JSON
            logging.error(f"Error loading sensors settings {e}")
            self._sensors = {}


        #self.adapter = pygatt.GATTToolBackend()
        self._discovered_devices = {}
        self.timeout = 20
        self.process = None
        self._scanning = False

        self.properties = dict()

        self.properties['module'] = EntityProperty(
                                                   category='module',
                                                   name='bt_xiaomi',
                                                   value='NOT_INITIALIZED',
                                                   call=self.update,
                                                   description='BT Module for MJ_HT_V1 Sensors',
                                                   type=DataType.MODULE,
                                                   interval=120)

        self.init_sensors()
        self.scan_devices()

    def init_sensors(self):

        for sensor in self._sensors:
            self._discovered_devices[sensor] =  {'custom_name' : self._sensors[sensor]['custom_name'], 'rssi': '-999', 'selected': 1, 'type' : self._sensors[sensor]['type']}


            if self._sensors[sensor]['type'] == 'mj_ht_v1':

                self.properties[self._sensors[sensor]['custom_name'] + '_humidity'] = EntityProperty(
                                                        category='connections/mj_ht_v1',
                                                        name=self._sensors[sensor]['custom_name'] + '_humidity',
                                                        value=None,
                                                        description='Humidity',
                                                        type=DataType.HUMIDITY,
                                                        interval=-1)
                self.properties[self._sensors[sensor]['custom_name'] + '_temperature'] = EntityProperty(
                                                        category='connections/mj_ht_v1',
                                                        name=self._sensors[sensor]['custom_name'] + '_temperature',
                                                        value=None,
                                                        description='Temperature',
                                                        type=DataType.TEMPERATURE,
                                                        interval=-1)
                self.properties[self._sensors[sensor]['custom_name'] + '_battery'] = EntityProperty(
                                                        category='connections/mj_ht_v1',
                                                        name=self._sensors[sensor]['custom_name'] + '_battery',
                                                        value=None,
                                                        description='Battery Level',
                                                        type=DataType.PERCENT_INT,
                                                        interval=-1)

            elif self._sensors[sensor]['type'] == 'mi_flora':

                self.properties[self._sensors[sensor]['custom_name'] + '_moisture'] = EntityProperty(
                                                        category='connections/mi_flora',
                                                        name=self._sensors[sensor]['custom_name'] + '_moisture',
                                                        value=None,
                                                        description='Moisture',
                                                        type=DataType.HUMIDITY,
                                                        interval=-1)
                self.properties[self._sensors[sensor]['custom_name'] + '_temperature'] = EntityProperty(
                                                        category='connections/mi_flora',
                                                        name=self._sensors[sensor]['custom_name'] + '_temperature',
                                                        value=None,
                                                        description='Temperature',
                                                        type=DataType.TEMPERATURE,
                                                        interval=-1)
                self.properties[self._sensors[sensor]['custom_name'] + '_battery'] = EntityProperty(
                                                        category='connections/mi_flora',
                                                        name=self._sensors[sensor]['custom_name'] + '_battery',
                                                        value=None,
                                                        description='Battery Level',
                                                        type=DataType.PERCENT_INT,
                                                        interval=-1)
                self.properties[self._sensors[sensor]['custom_name'] + '_fertility'] = EntityProperty(
                                                        category='connections/mi_flora',
                                                        name=self._sensors[sensor]['custom_name'] + '_fertility',
                                                        value=None,
                                                        description='Fertility',
                                                        type=DataType.CONDUCTIVITY,
                                                        interval=-1)
                self.properties[self._sensors[sensor]['custom_name'] + '_light'] = EntityProperty(
                                                        category='connections/mi_flora',
                                                        name=self._sensors[sensor]['custom_name'] + '_light',
                                                        value=None,
                                                        description='Light',
                                                        type=DataType.ILLUMINATION,
                                                        interval=-1)


    def run_gatttool(self, handle, mac, command="", listen=False):
     """Runs gatttool command and returns the output."""
     try:
      if command and not listen:
        cmd = f"gatttool -b {mac} --char-write-req -a {handle} -n {command}"
        output = subprocess.check_output(cmd, shell=True, timeout=10)
        print(cmd)
        print(output)
        if output is not None:
         return (output)
      elif listen and listen:
        #gatttool -b 4C:65:A8:D0:81:70 --char-write-req --handle=0x10 -n 0100 --listen
        cmd = f"gatttool -b {mac} --char-write-req --handle={handle} -n {command} --listen"
        output = subprocess.check_output(cmd, shell=True, timeout=7)
        print(cmd)
        print(output)
        if output is not None:
         return (output)
      else:
       cmd = f"gatttool -b {mac} --char-read -a {handle}"
       output = subprocess.check_output(cmd, shell=True, timeout=10)
       print(cmd)
      print(output)
      if output is not None:
       return (output)

     except subprocess.TimeoutExpired as e:
            print(e.output)  # This will print the partial output received before the timeout
            if e.output is not None:
             return (e.output)
     return b""


    def parse_firmware_battery_data_mi_flora(self,data):
     """Parse the firmware and battery data."""
     try:
        bytes_data = bytes.fromhex(data.split("value/descriptor: ")[1].strip())
        battery, firmware = struct.unpack('<xB5s', bytes_data)
        firmware = firmware.partition(b'\0')[0]  # Remove trailing null bytes
        return battery, firmware.decode()
     except:
        return None, None

    def parse_sensor_data_mi_flora(self,data):
     """Parse the sensor data."""
     try:
      bytes_data = bytes.fromhex(data.split("value/descriptor: ")[1].strip())
      temperature, sunlight, moisture, fertility = struct.unpack('<hxIBHxxxxxx', bytes_data)
      temperature /= 10.0  # Convert to Celsius
      return temperature, sunlight, moisture, fertility
     except: 
      return 0, 0 ,0 , 0


    def parse_sensor_data_mj_ht_v1(self, sensor_data):
     # Split the sensor data by newlines
     lines = sensor_data.split('\n')

     for line in lines:
        if 'Notification handle' in line:
            parts = line.split(': ')
            if len(parts) > 1:
                value_part = parts[1]
                hex_part = ''.join(char for char in value_part if char in "0123456789abcdefABCDEF")

                try:
                    ascii_string = bytes.fromhex(hex_part).decode('utf-8').rstrip('\x00')
                    # Assuming the format is "T=xx.x H=yy.y"
                    parts = ascii_string.split()
                    if len(parts) >= 2:
                        temperature_str = parts[0][2:]  # After "T="
                        humidity_str = parts[1][2:]     # After "H="
                        return float(temperature_str), float(humidity_str.rstrip('\x00'))
                except ValueError as e:
                    print("Error converting hex to ASCII:", e)
      # Return a default value if no data is found or an error occurs
     return None, None



    def update_threaded(self):

        for sensor in self.sensors:

            if self.sensors[sensor]['type'] == 'mi_flora':

                    try:
                     firmware_battery_data = self.run_gatttool(MI_FLORA_HANDLE_FIRMWARE_AND_BATTERY, sensor).decode()
                     battery, firmware = self.parse_firmware_battery_data_mi_flora(firmware_battery_data)
                     self.properties[self._sensors[sensor]['custom_name'] + '_battery'].value = battery #in %

                     self.run_gatttool(MI_FLORA_HANDLE_MODE_CHANGE, sensor, "A01F")
                     sensor_data = self.run_gatttool(MI_FLORA_HANDLE_DATA_READ, sensor).decode()
                     temperature, sunlight, moisture, fertility = self.parse_sensor_data_mi_flora(sensor_data)
                     self.properties[self._sensors[sensor]['custom_name'] + '_moisture'].value = int(moisture) #in %
                     self.properties[self._sensors[sensor]['custom_name'] + '_temperature'].value = int(temperature * 1000) #in celsius 
                     self.properties[self._sensors[sensor]['custom_name'] + '_light'].value = int(sunlight) # in lux
                     self.properties[self._sensors[sensor]['custom_name'] + '_fertility'].value = int(fertility)  # in uS/cm

                    except subprocess.CalledProcessError as e:
                     logging.error(f"Failed to run gatttool: {e}")

            if self.sensors[sensor]['type'] == 'mj_ht_v1':
                try:

                     sensor_data = self.run_gatttool(MJ_HT_V1_HANDLE_DATA_READ, sensor, "0100", listen=True).decode()
                     temperature, humidity = self.parse_sensor_data_mj_ht_v1(sensor_data)
                     if humidity is not None:
                      self.properties[self._sensors[sensor]['custom_name'] + '_humidity'].value = int(humidity) #in %
                      self.properties[self._sensors[sensor]['custom_name'] + '_temperature'].value = int(temperature * 1000) #in celsius 

                     # Run gatttool command to get battery data
                     battery_data = self.run_gatttool(MJ_HT_V1_HANDLE_BATTERY, sensor).decode()
                     battery_hex = battery_data.split(": ")[1].strip()
                     # Converting the hex value to an integer
                     batt = int(battery_hex, 16)
                     self.properties[self._sensors[sensor]['custom_name'] + '_battery'].value = batt #in %


                except subprocess.CalledProcessError as e:
                     logging.error(f"Failed to run gatttool: {e}")



    def update(self):
        """Starts the update process in a separate thread."""
        update_thread = threading.Thread(target=self.update_threaded)
        update_thread.start()
        return 'OK'


    def get_inputs(self) -> list:
        return list(self.properties.values())

    @Property(dict)
    def sensors(self):
        return self._sensors



    @Property(bool, notify=scanningChanged)
    def scanning(self):
        return self._scanning

    @scanning.setter
    def scanning(self, value):
        if self._scanning != value:
            self._scanning = value
            self.scanningChanged.emit(self._scanning)

    @Slot()
    def scan_devices(self):
        logging.info('start bluetooth scanning..')
        self.stop_scan()  # Ensure no previous scan is running
        self.scanning = True
        #btmgmt -i hci0 power on
        cmd = ['/usr/bin/stdbuf', '-oL', '/usr/bin/btmgmt', '-i', 'hci0', 'find']
        self.process = subprocess.Popen(cmd,stdin=subprocess.PIPE ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)
        output_thread = threading.Thread(target=self.parse_output)
        output_thread.start()
        timer = threading.Timer(self.timeout, self.stop_scan)
        timer.start()



    def parse_output(self):
        device_info = {}
        for line in iter(self.process.stdout.readline, ''):
            if 'dev_found' in line:
                if device_info:  # If there is a previous device, save it
                    if device_info['address'] not in self._discovered_devices:
                        self._discovered_devices[device_info['address']] = device_info
                    else:
                       if device_info['name'] != None:
                           self._discovered_devices[device_info['address']]['name'] = device_info['name']
                       self._discovered_devices[device_info['address']]['rssi'] = device_info['rssi']
                    self._discovered_devices[device_info['address']]['type'] = self.detection_type(device_info)


                    self.devicesScanned.emit()
                parts = line.split(' ')
                address = parts[2]
                device_info = {
                    'address': address,
                    'type': parts[4] + ' ' + parts[5],
                    'rssi': parts[7],
                    'name': None,
                    'type': 'unknown', 
                    'selected' : 0,
                    'custom_name' : ""
                }
            elif 'name' in line and device_info:
                name = line.split('name', 1)[1].strip()
                device_info['name'] = name

        if device_info:  # Save the last device
                    if device_info['address'] not in self._discovered_devices:
                        self._discovered_devices[device_info['address']] = device_info
                        self._discovered_devices[device_info['address']]['type'] = self.detection_type(device_info)

                    else:
                       if device_info['name'] != None:
                           self._discovered_devices[device_info['address']]['name'] = device_info['name']
                       self._discovered_devices[device_info['address']]['rssi'] = device_info['rssi']


    def detection_type(self,device):

        if   device['address'].startswith('C4:7C:8D') and device['name'] == 'Flower care':
            return 'mi_flora'

        elif device['address'].startswith('C4:7C:8D') and device['name'] == 'Flower mate':
            return 'mi_flora'

        elif device['address'].startswith('4C:65:A8') and device['name'] == "MJ_HT_V1":
            return 'mj_ht_v1'

        return 'unknown'




    def stop_scan(self):
     self.scanning = False

     if self.process:
        logging.info("bluetooth scanning process was still active... killing.")
        # Attempt to terminate the process
        try:
            self.process.terminate()
            # Wait for a moment to see if the process terminates
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            # If the process is still running, forcefully kill it
            try:
                os.kill(self.process.pid, signal.SIGKILL)
            except OSError:
                pass  # Process could have already terminated
        except Exception as e:
            print(f"Error terminating process: {e}")

        # Make sure the subprocess resources are cleaned up
        if self.process:
            self.process.communicate()

        # Stop the find command for the Bluetooth interface
        try:
            subprocess.run(['btmgmt', '-i', 'hci0', 'stop-find'], input="", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logging.error(f"Error stopping Bluetooth find: {e}")

        self.process = None

    @Signal
    def devicesScanned(self):
        pass


    @Property(int)
    def singleton(self):
        return singleton

    @Property('QVariantMap', notify=devicesScanned)
    def discovered_devices(self):
        return self._discovered_devices

    @Slot(str, str)
    def add_sensor(self, mac, name):
        logging.info('add_sensor: ' + mac + ' ' + name)
        try:
            self._sensors[mac] = {}
            self._sensors[mac]['custom_name'] = name
            self._sensors[mac]['type'] =  self._discovered_devices[mac]['type']

            self._discovered_devices[mac]['custom_name'] = name
            self._discovered_devices[mac]['selected'] = 1

            try:
             self.settings.setValue("/module/connections/bt_xiaomi/sensors", json.dumps(self._sensors))
            except Exception as e:
             logging.error('JSON DUMP ERROR' + str(e))

            try:
                self.init_sensors()
                self.inputs.add(self.get_inputs())
            except Exception as e:
                logging.error(f'Adding new sensors to inputs dict error: {e}')

            self.devicesScanned.emit()

        except Exception as e:
            logging.error('ERROR' + str(e))

    @Slot(str)
    def delete_sensor(self, mac):
        logging.info('delete_sensor: ' + mac + ' ' + str(self._sensors[mac]['custom_name']))
        try:
            properties_to_delete = []
            for subproperty in self.properties.keys():
                if self.properties[subproperty].name.startswith(self._sensors[mac]['custom_name']):
                    if self.properties[subproperty].path in self.inputs.entries:
                        del self.inputs.entries[self.properties[subproperty].path]
                        properties_to_delete.append(subproperty)

            for property_key in properties_to_delete:
                del self.properties[property_key]


            del self._sensors[mac]
            self._discovered_devices[mac]['selected'] = 0
            self._discovered_devices[mac]['custom_name'] = ""
            try:
             self.settings.setValue("/module/connections/bt_xiaomi/sensors", json.dumps(self._sensors))
            except Exception as e:
             logging.error(str(e))

        except Exception as e:
            logging.error(str(e))
        self.devicesScanned.emit()







