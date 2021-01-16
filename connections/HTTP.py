# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property
import time
import os
import threading
import socket
from datetime import datetime
from core.DataTypes import DataType
from core.Toolbox import Pre_5_15_2_fix
from core.Inputs import InputListModel
from functools import partial
import urllib.request
import json
from core.DataTypes import Convert
from urllib.error import HTTPError, URLError


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

                if 'set' in self.http_inputs[key] and self.http_inputs[key]['set']:
                    self.selected_inputs["http/" + self.name + "/" + key]["set"] = partial(self.set_value, key)


        return self.selected_inputs


    @Signal
    def dataChanged(self):
        pass

    @Property(QObject, notify=dataChanged)
    def inputList(self):

        return self.inputlist



    @Slot()
    def update_vars(self):
        self.http_inputs = dict()
        try:
            url = 'https://' if self._ssl else 'http://'
            url += self._ip + ':' + str(self._port) + '/'

            try:
                response = urllib.request.urlopen(url, timeout=5)

            except HTTPError as error:
                    print('Data not retrieved because %s\nURL: %s', error, url)

            except URLError as error:
                    if isinstance(error.reason, socket.timeout):
                        print('socket timed out - URL %s', url)
                    else:
                        print('some other error happened')


            else:

                data = response.read().decode('utf-8')
                data =  json.loads(data)
                for key in data:

                    data[key]["type"] = Convert.str_to_type(data[key]['type'])
                    if data[key]['interval'] == -1: data[key]['interval']  = 60
                    # -1 means updated through class on remote device, so we need to define standard interval for network vars

                self.http_inputs = data

                #TODO check for correctness of dict


        except Exception as ex:
            print(ex)

        self.inputlist = InputListModel(self.http_inputs)
        self.vars_changed.emit()
        self.dataChanged.emit()





    def set_value(self, path, value):
       try:
           url = 'https://' if self._ssl else 'http://'
           params = {'key': path, 'set': str(value)}
           url += self._ip + ':' + str(self._port) + '/?' + urllib.parse.urlencode(params)

           try:
               response = urllib.request.urlopen(url, timeout=5)

           except HTTPError as error:
                   print('Data not retrieved because %s\nURL: %s', error, url)
                   return None
           except URLError as error:
                   if isinstance(error.reason, socket.timeout):
                       print('socket timed out - URL %s', url)
                   else:
                       print('some other error happened')
                   return None

           else:

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

           try:
               response = urllib.request.urlopen(url, timeout=5)

           except HTTPError as error:
                   print('Data not retrieved because %s\nURL: %s', error, url)
                   return None
           except URLError as error:
                   if isinstance(error.reason, socket.timeout):
                       print('socket timed out - URL %s', url)
                   else:
                       print('some other error happened')
                   return None

           else:
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


    @Slot(str)
    def delete_var(self, path):

            if "http/" + self.name + "/" + path in self.selected_inputs:
                del self.selected_inputs["http/" + self.name + "/" + path]
            if "http/" + self.name + "/" + path in self.inputs.entries:
                    del self.inputs.entries["http/" + self.name + "/" + path]
            if path in self._vars:
                self._vars.remove(path)

            self.settings.setValue("http/" + self.name + "/vars", self._vars)

            self.vars_changed.emit()
            self.dataChanged.emit()


    def delete_inputs(self):
        for key in self.selected_inputs:
            del self.inputs.entries[key]



    @Slot(str)
    def add_var(self, key):

        if key in self.http_inputs:
            self.selected_inputs["http/" + self.name + "/" + key] = self.http_inputs[key]
            self.selected_inputs["http/" + self.name + "/" + key]["call"] = partial(self.get_value, key)

            if 'set' in self.http_inputs[key] and self.http_inputs[key]['set']:
                self.selected_inputs["http/" + self.name + "/" + key]["set"] = partial(self.set_value, key)
            self._vars.append(key)
            self.inputs.add(self.get_inputs())
            self.settings.setValue("http/" + self.name + "/vars", self._vars)

            self.vars_changed.emit()
            self.dataChanged.emit()



    # @Property(str, notify=ip_changed)
    def ip(self):
        return str(self._ip)

    @Pre_5_15_2_fix(str, ip, notify=ip_changed)
    def ip(self, ip):
        self._ip = str(ip)
        self.settings.setValue("http/" + self.name + "/ip", ip)
        self.ip_changed.emit()


    @Signal
    def port_changed(self):
        pass

    # @Property(int, notify=port_changed)
    def port(self):
        return int(self._port)

    @Pre_5_15_2_fix(int, port, notify=port_changed)
    def port(self, port):
        self._port = int(port)
        self.settings.setValue("http/" + self.name + "/port", port)


    # @Property('QVariantList', notify=vars_changed)
    def vars(self):
        return (self._vars)

    @Pre_5_15_2_fix('QVariantList', vars, notify=vars_changed)
    def vars(self, varlist):
        self._vars = varlist
        self.settings.setValue("http/" + self.name + "/vars", varlist)




