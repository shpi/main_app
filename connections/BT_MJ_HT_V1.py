# -*- coding: utf-8 -*-

import logging
from functools import partial
import pygatt
import threading
import time


from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property

from core.DataTypes import Convert
from core.DataTypes import DataType
from core.Inputs import InputListModelDict
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix


class BT_MJ_HT_V1(QObject):

    singleton = 1

    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()

        self.name = "INSTANCE"  # this class has max. one instance!
        self.inputs = inputs
        self.settings = settings
        self._sensors = (settings.value("/module/connections/bt_mj_ht_v1/sensors", {}))
        self.adapter = pygatt.GATTToolBackend()
        self._discovered_devices = {}
        self.properties = dict()

        self.properties['module'] = EntityProperty(parent=self,
                                                   category='module',
                                                   entity='connections',
                                                   name='bt_mj_ht_v1',
                                                   value='NOT_INITIALIZED',
                                                   call=self.update,
                                                   description='BT Module for MJ_HT_V1 Sensors',
                                                   type=DataType.MODULE,
                                                   interval=60)

        for sensor in self._sensors:
            self.properties[self._sensors[sensor] + '_humidity'] = EntityProperty(parent=self,
                                                        category='connections',
                                                        entity='bt_mj_ht_v1',
                                                        name=self._sensors[sensor],
                                                        value=None,
                                                        description='Humidity',
                                                        type=DataType.HUMIDITY,
                                                        interval=-1)
            self.properties[self._sensors[sensor] + '_temperature'] = EntityProperty(parent=self,
                                                        category='connections',
                                                        entity='bt_mj_ht_v1',
                                                        name=self._sensors[sensor],
                                                        value=None,
                                                        description='Temperature',
                                                        type=DataType.TEMPERATURE,
                                                        interval=-1)
            self.properties[self._sensors[sensor] + '_battery'] = EntityProperty(parent=self,
                                                        category='connections',
                                                        entity='bt_mj_ht_v1',
                                                        name=self._sensors[sensor],
                                                        value=None,
                                                        description='Battery Level',
                                                        type=DataType.PERCENTAGE,
                                                        interval=-1)



    def update(self):
        pass


    def get_inputs(self) -> list:
        return list(self.properties.values())

    def _scan_devices(self, timeout=5):
        #print("Scanning for BLE devices...")
        try:
            self.adapter.start()
            self._discovered_devices = {}
            self._discovered_devices = self.adapter.scan(timeout=timeout)
            self.adapter.reset()
            for device in self.discovered_devices:
                logging.info(f"Found device: {device['address']} with name: {device['name']}")
        except Exception as e:
            logging.error(f"An error occurred during scanning: {e}")

        finally:
           self.adapter.stop()
           self.devicesScanned.emit()

    @Slot()
    def scan_devices(self):
        scan_thread = threading.Thread(target=self._scan_devices)
        scan_thread.start()


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
            self._sensors[mac] = name
            self.settings.setValue(key + "/sensors", self._sensors)
        except Exception as e:
            logging.error(str(e))

    @Slot(str)
    def delete_sensor(self, mac):
        logging.info('delete_sensor: ' + mac + ' ' + self._sensors[mac])
        try:
            del self._sensors[mac]
            self.settings.setValue(key + "/sensors", self._sensors)
        except Exception as e:
            logging.error(str(e))







