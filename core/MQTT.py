# -*- coding: utf-8 -*-

import logging
import sys
import time
import paho.mqtt.client as mqtt

from PySide2.QtCore import QSettings, QObject, Signal

from core.DataTypes import Convert, DataType
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix
from functools import partial


class MQTTClient(QObject):
    def __init__(self, inputs, settings: QSettings):
        super().__init__()

        self.settings = settings
        self._port = int(settings.value("mqtt/port", 1883))
        self._host = str(settings.value("mqtt/host", 'broker.hivemq.com'))
        self._path = str(settings.value("mqtt/path", 'shpi'))
        self._enabled = int(settings.value("mqtt/enabled", 1))

        self.properties = dict()
        self.properties['general_shutter_call'] = EntityProperty(parent=self,
                                                       category='core',
                                                       entity='mqtt',
                                                       name='general_shutter_call',
                                                       description='disk usage',
                                                       set=partial(self.publish,self._path + "/general_shutter_call"),
                                                       type=DataType.PERCENT_INT,
                                                       interval=0)

        def on_connect(client, userdata, flags, rc):
            

            client.subscribe(
            [
                (self._path+"/general_shutter_call", 1), 
            ]
            )

        def on_message( client, userdata, msg):

            if msg.topic == self._path + "/general_shutter_call":
               self.properties['general_shutter_call'].value = int(msg.payload.decode("utf-8"))
               print("GENERAL SHUTTER CALL " + str(self.properties['general_shutter_call'].value))
            #client.username_pw_set(config.MQTT_USER, config.MQTT_PW)


        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message

        if self._enabled:
            self.start_mqtt()

    def start_mqtt(self):
            logging.info("Starting MQTT Client ...")
            try:
                self.client.connect(self._host, self._port, 60)
                self.client.loop_start()
            except:
                logging.error("MQTT Client connection error.")
                self._enabled = 0
                pass



    def stop_mqtt(self):
        try:
          self.client.disconnect()
          self.client.loop_stop()
        except:
          pass

    def publish(self,path, value):
     try:
        result, mid = self.client.publish(path, value)

        if result == mqtt.MQTT_ERR_SUCCESS:
                        logging.info("Message {} queued successfully.".format(mid))
        else:
                        logging.error("Failed to publish message. Error: {}".format(result))
     except Exception as e:
                    logging.error("EXCEPTION RAISED: {}".format(e))

    @Signal
    def settings_changed(self):
        pass


    def get_inputs(self) -> list:
        return list(self.properties.values())



    # @Property(int, notify=settings_changed)
    def port(self):
        return int(self._port)

    @Pre_5_15_2_fix(int, port, notify=settings_changed)
    def port(self, value):
        self._port = int(value)
        self.settings.setValue("mqtt/port", value)

        if self._enabled:
            self.stop_mqtt()
            self.start_mqtt()


    # @Property(int, notify=settings_changed)
    def enabled(self):
        return int(self._enabled)

    @Pre_5_15_2_fix(int, enabled, notify=settings_changed)
    def enabled(self, value):
        self._enabled = int(value)
        self.settings.setValue("mqtt/enabled", value)
        if self._enabled == 1:
            self.start_mqtt()
        else:
            self.stop_mqtt()




   # @Property(str, notify=api_keyChanged)
    def host(self):
        return self._host

    # @host.setter
    @Pre_5_15_2_fix(str, host, notify=settings_changed)
    def host(self, key):
        self._host = key
        self.settings.setValue('mqtt/host', key)
        if self._enabled:
            self.stop_mqtt()
            self.start_mqtt()



   # @Property(str, notify=api_keyChanged)
    def path(self):
        return self._path

    # @host.setter
    @Pre_5_15_2_fix(str, path, notify=settings_changed)
    def path(self, key):
        self._path = key
        self.settings.setValue('mqtt/path', key)
        
        if self._enabled:
            self.stop_mqtt()
            self.start_mqtt()


