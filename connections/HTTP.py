# -*- coding: utf-8 -*-

import json
import logging
import socket
import sys
import urllib.request
from functools import partial
from urllib.error import HTTPError, URLError

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property

from core.DataTypes import Convert
from core.DataTypes import DataType
from core.Inputs import InputListModelDict
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix


class HTTP(QObject):
    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()

        self.path = 'http/' + name
        self.name = name
        self.inputs = inputs
        self.settings = settings
        self._ip = str(settings.value(self.path + "/ip", '127.0.0.1'))
        self._port = int(settings.value(self.path + "/port", '9000'))
        self._vars = (settings.value(self.path + "/vars", []))

        if isinstance(self._vars, str):
            self._vars = [self._vars]

        self._ssl = False
        self.module_inputs = dict()
        self.properties = dict()

        self.properties['module'] = EntityProperty(parent=self,
                                                   category='module',
                                                   entity='connections',
                                                   name=self.name,
                                                   value='NOT_INITIALIZED',
                                                   call=self.update_vars,
                                                   description='HTTP Module for ' + self.name + '(' + self._ip + ')',
                                                   type=DataType.MODULE,
                                                   interval=60)

        for sproperty in self._vars:
            self.properties[sproperty] = EntityProperty(parent=self,
                                                        category='connections/http',
                                                        entity=self.name,
                                                        name=sproperty,
                                                        value=None,
                                                        description='place holder after init, module not initialized',
                                                        type=DataType.UNDEFINED,
                                                        interval=-1)

    def get_inputs(self) -> list:
        return list(self.properties.values())

    @Signal
    def dataChanged(self):
        pass

    @Property(QObject, notify=dataChanged)
    def inputList(self):
        return self.inputlist

    @Slot()
    def update_vars(self):
        self.module_inputs = dict()
        status = 'OK'

        try:
            url = 'https://' if self._ssl else 'http://'
            url += self._ip + ':' + str(self._port) + '/'

            try:
                response = urllib.request.urlopen(url, timeout=1)

            except HTTPError as error:
                status = 'ERROR'
                logging.error('Data not retrieved because %s\nURL: %s', error, url)

            except URLError as error:
                status = 'ERROR'
                if isinstance(error.reason, socket.timeout):
                    logging.error('socket timed out - URL %s', url)
                else:
                    logging.error('unknown error happened')
            except Exception as e:
                status = 'ERROR'
                logging.error(str(e))

            if status != 'ERROR':
                data = response.read().decode('utf-8')
                data = json.loads(data)
                for key in data:

                    data[key]['type'] = Convert.str_to_type(data[key].get('type', 'undefined'))

                    if data[key]['interval'] == -1:
                        data[key]['interval'] = 60
                    # -1 means updated through class on remote device,
                    # so we need to define standard interval for network vars

                    if key in self.properties:
                        self.properties[key].type = data[key]['type']
                        self.properties[key].interval = data[key].get('interval', 60)
                        self.properties[key].value = data[key].get('value', 0)
                        self.properties[key].description = data[key].get('description', None)
                        self.properties[key].call = partial(self.get_value, key)
                        if 'set' in data[key]:
                            self.properties[key].set = partial(self.set_value, key)

                self.module_inputs = data

                status = 'OK'

                # TODO check for correctness of dict

        except Exception as ex:
            status = 'NOT_INITIALIZED'
            logging.error('damns:' + str(ex))

        self.properties[
            'module'].value = status  # we need to update it here, because we have no interval update function
        self.inputlist = InputListModelDict(self.module_inputs)
        self.vars_changed.emit()
        self.dataChanged.emit()

    def set_value(self, path, value):
        status = 'OK'
        try:
            url = 'https://' if self._ssl else 'http://'
            params = {'key': path, 'set': str(value)}
            url += self._ip + ':' + str(self._port) + '/?' + urllib.parse.urlencode(params)

            try:
                response = urllib.request.urlopen(url, timeout=1)

            except HTTPError as error:
                status = 'ERROR'
                self.properties['module'].value = status
                logging.debug('Data not retrieved because %s\nURL: %s', error, url)
                return None
            except URLError as error:
                status = 'ERROR'
                if isinstance(error.reason, socket.timeout):
                    logging.debug('socket timed out - URL %s', url)
                else:
                    logging.debug('some other error happened')
                self.properties['module'].value = status
                return None

            else:

                data = response.read().decode('utf-8')
                data = json.loads(data)

                # TODO check for correctness of dict
                self.properties['module'].value = status
                return data['value']

        except Exception as ex:
            status = 'ERROR'
            logging.debug(str(ex))
            self.properties['module'].value = status
            return None

    def get_value(self, path):
        try:
            url = 'https://' if self._ssl else 'http://'
            params = {'key': path}
            url += self._ip + ':' + str(self._port) + '/?' + urllib.parse.urlencode(params)

            try:
                response = urllib.request.urlopen(url, timeout=1)

            except HTTPError as error:
                logging.error('Data not retrieved because %s\nURL: %s', error, url)
                return None
            except URLError as error:
                if isinstance(error.reason, socket.timeout):
                    self.properties['module'].value = 'ERROR'
                    logging.error('socket timed out - URL %s', url)
                else:
                    self.properties['module'].value = 'ERROR'
                    logging.error('some other error happened')
                return None

            else:
                data = response.read().decode('utf-8')
                data = json.loads(data)
                # TODO check for correctness of dict

                self.properties['module'].value = 'OK'
                return data['value']

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line {line_number}')

            self.properties['module'].value = 'ERROR'

            return None

    @Signal
    def vars_changed(self):
        pass

    @Signal
    def ip_changed(self):
        pass

    @Slot(str)
    def delete_var(self, path):
        if path != '':
            if path in self.properties:
                del self.properties[path]
            if 'connections/http' + self.properties[path].name + "/" + path in self.inputs.entries:
                del self.inputs.entries['connections/http' + self.properties[path].name + "/" + path]
                # todo: remove from timer_schedule
            if path in self._vars:
                self._vars.remove(path)

        self.settings.setValue("http/" + self.name + "/vars", self._vars)

        self.vars_changed.emit()
        self.dataChanged.emit()

    def delete_inputs(self):
        for key in self.properties:
            if key in self.inputs.entries:
                del self.inputs.entries[key]

    @Slot(str)
    def add_var(self, key):
        if key in self.module_inputs:
            self.properties[key] = EntityProperty(parent=self,
                                                  category='connections/http',
                                                  entity=self.name,
                                                  name=key,
                                                  call=partial(self.get_value, key),
                                                  set=partial(self.set_value, key) if 'set' in self.module_inputs[
                                                      key] else None,
                                                  type=Convert.str_to_type(self.module_inputs[key]['type']),
                                                  description=self.module_inputs[key]['description'],
                                                  interval=60)
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
        return self._vars

    @Pre_5_15_2_fix('QVariantList', vars, notify=vars_changed)
    def vars(self, varlist):
        self._vars = varlist
        self.settings.setValue("http/" + self.name + "/vars", varlist)
