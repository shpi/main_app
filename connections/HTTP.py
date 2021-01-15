# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property
import time
import os
import threading
from datetime import datetime
from core.DataTypes import DataType
from core.Toolbox import Pre_5_15_2_fix
from core.Inputs import InputListModel
from functools import partial
import urllib.request
import json
from core.DataTypes import Convert


class HTTP(QObject):
    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()

        self.name = name
        self.inputs = inputs
        self.settings = settings
        self._ip = str(settings.value("http/" + name + "/ip", '127.0.0.1'))
        self._port = int(settings.value("http/" + name + "/port", '9000'))
        self._vars = list(settings.value("http/" + name + "/vars", []))
        self._ssl = False
        self.http_inputs = dict()

        self.update_vars()
        self.selected_inputs = dict()

        self.inputlist = InputListModel(self.http_inputs)

        #minimum fields: path, value, interval, type, lastupdate

    def get_inputs(self) -> dict:

        for key in self.selected_inputs:
            if key[len("http/" + self.name + "/"):] not in self._vars:
                del self.selected_inputs[key]

        for key in self._vars:
            #data[key]['interval'] = int(settings.value("http/" + name + "/" + key + '/interval', data[key]['interval']))
            if key in self.http_inputs:
                self.selected_inputs["http/" + self.name + "/" + key] = self.http_inputs[key]
                self.selected_inputs["http/" + self.name + "/" + key]["call"] = partial(self.get_value, key)
                self.selected_inputs["http/" + self.name + "/" + key]["type"] = Convert.str_to_type(self.http_inputs[key]['type'])

                if 'set' in self.http_inputs[key] and self.http_inputs[key]['set']:
                    self.selected_inputs["http/" + self.name + "/" + key]["set"] = partial(self.set_value, key, value)


        return self.selected_inputs


    @Signal
    def dataChanged(self):
        pass

    @Property(QObject, notify=dataChanged)
    def inputList(self):

        return self.inputlist



    @Slot()
    def update_vars(self):
        try:
            url = 'https://' if self._ssl else 'http://'
            url += self._ip + ':' + str(self._port) + '/'
            response = urllib.request.urlopen(url)
            data = response.read().decode('utf-8')
            data =  json.loads(data)

            for key in data:
                data[key]["type"] = Convert.str_to_type(data[key]['type'])


            self.http_inputs = data


            #TODO check for correctness of dict

            self.vars_changed.emit()

        except Exception as ex:
            print(ex)
            return {}


    def set_value(self, path, value):
       try:
           url = 'https://' if self._ssl else 'http://'
           params = {'key': path, 'set': str(value)}
           url += self._ip + ':' + str(self._port) + '/?' + urllib.parse.urlencode(params)
           response = urllib.request.urlopen(url)
           data = response.read().decode('utf-8')
           data =  json.loads(data)

           #TODO check for correctness of dict

           return data['value']

       except Exception as ex:
           print(ex)
           return None



    def get_value(self, path):
       try:
           url = 'https://' if self._ssl else 'http://'
           params = {'key': path}
           url += self._ip + ':' + str(self._port) + '/?' + urllib.parse.urlencode(params)
           response = urllib.request.urlopen(url)
           data = response.read().decode('utf-8')
           data =  json.loads(data)

           #TODO check for correctness of dict

           return data['value']

       except Exception as ex:
           print(ex)
           return None



    @Signal
    def vars_changed(self):
        pass

    @Signal
    def ip_changed(self):
        pass

    # @Property(str, notify=ip_changed)
    def ip(self):
        return str(self._ip)

    @Pre_5_15_2_fix(str, ip, notify=ip_changed)
    def ip(self, ip):
        self._ip = str(ip)
        self.settings.setValue("http/" + self.name + "/ip", ip)


