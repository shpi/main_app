# -*- coding: utf-8 -*-

import logging
import sys
import time
import paho.mqtt.client as mqtt
import ssl


from PySide2.QtCore import QSettings, QObject, Signal

from core.DataTypes import Convert, DataType
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix
from functools import partial


class MQTTClient(QObject):
    inputs = None

    def __init__(self, settings: QSettings):
        super().__init__()

        self.settings = settings
        self._port = int(settings.value("mqtt/port", 1883))
        self._host = str(settings.value("mqtt/host", 'broker.hivemq.com'))
        self._path = str(settings.value("mqtt/path", 'shpi'))
        self._tls_enabled = int(settings.value("mqtt/tls_enabled", '0'))
        self._user = str(settings.value("mqtt/user", ''))
        self._password = str(settings.value("mqtt/password", ''))
        self.is_connected = False


        self._enabled = int(settings.value("mqtt/enabled", '0'))
        self._available_properties = {}  # Dictionary to store properties with their paths


        self.properties = dict()
        self.properties['general_shutter_call'] = EntityProperty(
                                                       category='mqtt',
                                                       name='general_shutter_call',
                                                       description='General Call for shutter instances',
                                                       set=partial(self.publish,self._path + "/general_shutter_call"),
                                                       type=DataType.PERCENT_INT,
                                                       interval=0)


        self.client = mqtt.Client()


        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect


        if self._enabled:
            self.start_mqtt()




    def on_connect(self, client, userdata, flags, rc):

            logging.error("subscribing to channels")

            client.subscribe([
            (self._path+"/general_shutter_call", 1),
            (self._path + "/#", 1),  # Replace with your actual main topic
            ])



            if rc == 0:
                self.is_connected = True
                logging.error("Connected to MQTT Broker")
            else:
                logging.error(f"Failed to connect to MQTT Broker: Error code {rc}")



    def on_disconnect(self, client, userdata, rc):
            # Update connection status when disconnected
            self.is_connected = False
            logging.error("Disconnected from MQTT Broker")



    def on_message(self, client, userdata, msg):

            if msg.topic == self._path + "/general_shutter_call":
               self.properties['general_shutter_call'].value = int(msg.payload.decode("utf-8"))
               logging.info("GENERAL SHUTTER CALL " + str(self.properties['general_shutter_call'].value))
            #client.username_pw_set(config.MQTT_USER, config.MQTT_PW)
            else:
                self.update_properties(msg.topic, msg.payload)




    def update_properties(self, topic, payload):
        # Store the raw payload using the topic path as the key
           if topic not in self._available_properties:
               self.properties_changed.emit()
               logging.error('NEW MQTT TOPIC: ' + str(topic))

           self._available_properties[topic] = payload.decode('utf-8')  # Decoding assuming payload is a string






    def start_mqtt(self):
            logging.error("Starting MQTT Client ...")
            try:
             if self._tls_enabled > 0:
                    #openssl s_client -host mqtt.broker.hostname.com -port 8883 -showcerts
                    self.client.tls_set() #tls_version=ssl.PROTOCOL_TLSv1_2)
                    self.client.tls_insecure_set(True)
             if self._user != '':
                self.client.username_pw_set(username=self._user, password=self._password)
             self.client.connect(self._host, self._port, 60)
             self.client.loop_start()
            except:
                logging.error("MQTT Client connection error.")
                self._enabled = 0
                pass


    def stop_mqtt(self):
        logging.error('stop mqtt client...')
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

    @Signal
    def properties_changed(self):
        pass


    def get_inputs(self) -> list:
        return list(self.properties.values())



    def available_properties(self):
        return self._available_properties


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


   # @Property(str, notify=settings_changed)
    def user(self):
        return self._user

    # @host.setter
    @Pre_5_15_2_fix(str, user, notify=settings_changed)
    def user(self, key):
        self._user = key
        self.settings.setValue('mqtt/user', key)
        
        if self._enabled:
            self.stop_mqtt()
            self.start_mqtt()

   # @Property(str, notify=settings_changed)
    def password(self):
        return self._password

    # @host.setter
    @Pre_5_15_2_fix(str, password, notify=settings_changed)
    def password(self, key):
        self._password = key
        self.settings.setValue('mqtt/password', key)
        
        if self._enabled:
            self.stop_mqtt()
            self.start_mqtt()


   # @Property(int, notify=settings_changed)
    def tls_enabled(self):
        return self._tls_enabled

    # @host.setter
    @Pre_5_15_2_fix(int, tls_enabled, notify=settings_changed)
    def tls_enabled(self, key):
        self._tls_enabled = key
        self.settings.setValue('mqtt/tls_enabled', key)
        
        if self._enabled:
            self.stop_mqtt()
            self.start_mqtt()
