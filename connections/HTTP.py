# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property
import logging
import socket
from core.Toolbox import Pre_5_15_2_fix
from core.Inputs import InputListModel
from functools import partial
import urllib.request
import json
from core.DataTypes import Convert
from urllib.error import HTTPError, URLError
from core.DataTypes import DataType


class HTTP(QObject):
    def __init__(self, name, inputs, settings: QSettings):
        super().__init__()

        self.path = 'http/' + name
        self.name = name
        self.inputs = inputs
        self.settings = settings
        self._ip = str(settings.value(self.path + "/ip", '127.0.0.1'))
        self._port = int(settings.value(self.path + "/port", '9000'))
        self._vars = list(settings.value(self.path + "/vars", []))
        self._ssl = False
        self.module_inputs = dict()
        self.selected_inputs = dict()

        self.selected_inputs['http/' + self.name] = {'description': 'HTTP Module ' + name + ' Status',
                                                     'value': 'NOT_INITIALIZED',
                                                     'type': DataType.MODULE,
                                                     'lastupdate': 0,
                                                     'interval': -1}
        self.update_vars()
        self.inputlist = InputListModel(self.module_inputs)

        # minimum fields: path, value, interval, type, lastupdate

    def get_inputs(self) -> dict:

        # keys = self.selected_inputs.keys()
        # for key in keys:
        #    if key[len("http/" + self.name + "/"):] not in self._vars:
        #        del self.selected_inputs[key]

        for key in self._vars:
            # data[key]['interval'] = int(settings.value(f"http/{name}/{key}/interval', data[key]['interval']))
            if key in self.module_inputs:
                self.selected_inputs["http/" + self.name + "/" + key] = self.module_inputs[key]
                self.selected_inputs["http/" + self.name + "/" + key]["call"] = partial(self.get_value, key)

                if 'set' in self.module_inputs[key] and self.module_inputs[key]['set']:
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
        self.module_inputs = dict()
        status = 'OK'

        try:
            url = 'https://' if self._ssl else 'http://'
            url += self._ip + ':' + str(self._port) + '/'

            try:
                response = urllib.request.urlopen(url, timeout=5)

            except HTTPError as error:
                status = 'ERROR'
                logging.debug('Data not retrieved because %s\nURL: %s', error, url)

            except URLError as error:
                status = 'ERROR'
                if isinstance(error.reason, socket.timeout):
                    logging.debug('socket timed out - URL %s', url)
                else:
                    logging.debug('unknown error happened')

            else:
                data = response.read().decode('utf-8')
                data = json.loads(data)
                for key in data:

                    data[key]["type"] = Convert.str_to_type(data[key]['type'])
                    if data[key]['interval'] == -1:
                        data[key]['interval'] = 60
                    # -1 means updated through class on remote device,
                    # so we need to define standard interval for network vars

                self.module_inputs = data

                # TODO check for correctness of dict

        except Exception as ex:
            status = 'ERROR'
            logging.debug(ex)

        self.selected_inputs['http/' + self.name][
            'value'] = status  # we need to update it here, because we have no interval update function
        self.inputlist = InputListModel(self.module_inputs)
        self.vars_changed.emit()
        self.dataChanged.emit()

    def set_value(self, path, value):
        status = 'OK'
        try:
            url = 'https://' if self._ssl else 'http://'
            params = {'key': path, 'set': str(value)}
            url += self._ip + ':' + str(self._port) + '/?' + urllib.parse.urlencode(params)

            try:
                response = urllib.request.urlopen(url, timeout=5)

            except HTTPError as error:
                status = 'ERROR'
                self.selected_inputs['http/' + self.name]['value'] = status
                logging.debug('Data not retrieved because %s\nURL: %s', error, url)
                return None
            except URLError as error:
                status = 'ERROR'
                if isinstance(error.reason, socket.timeout):
                    logging.debug('socket timed out - URL %s', url)
                else:
                    logging.debug('some other error happened')
                self.selected_inputs['http/' + self.name]['value'] = status
                return None

            else:

                data = response.read().decode('utf-8')
                data = json.loads(data)

                # TODO check for correctness of dict
                self.selected_inputs['http/' + self.name]['value'] = status
                return data['value']

        except Exception as ex:
            status = 'ERROR'
            logging.debug(str(ex))
            self.selected_inputs['http/' + self.name]['value'] = status
            return None

    def get_value(self, path):

        try:
            url = 'https://' if self._ssl else 'http://'
            params = {'key': path}
            url += self._ip + ':' + str(self._port) + '/?' + urllib.parse.urlencode(params)

            try:
                response = urllib.request.urlopen(url, timeout=5)

            except HTTPError as error:
                logging.error('Data not retrieved because %s\nURL: %s', error, url)
                return None
            except URLError as error:
                if isinstance(error.reason, socket.timeout):
                    self.selected_inputs['http/' + self.name]['value'] = 'ERROR'
                    logging.error('socket timed out - URL %s', url)
                else:
                    self.selected_inputs['http/' + self.name]['value'] = 'ERROR'
                    logging.error('some other error happened')
                return None

            else:
                data = response.read().decode('utf-8')
                data = json.loads(data)
                # TODO check for correctness of dict

                self.selected_inputs['http/' + self.name]['value'] = 'OK'
                return data['value']

        except Exception as ex:

            self.selected_inputs['http/' + self.name]['value'] = 'ERROR'
            logging.error(str(ex))
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
            if "http/" + self.name + "/" + path in self.selected_inputs:
                del self.selected_inputs["http/" + self.name + "/" + path]
            if "http/" + self.name + "/" + path in self.inputs.entries:
                del self.inputs.entries["http/" + self.name + "/" + path]
                # todo: remove from timer_schedule
            if path in self._vars:
                self._vars.remove(path)

        self.settings.setValue("http/" + self.name + "/vars", self._vars)

        self.vars_changed.emit()
        self.dataChanged.emit()

    def delete_inputs(self):
        for key in self.selected_inputs:
            if key in self.inputs.entries:
                del self.inputs.entries[key]

    @Slot(str)
    def add_var(self, key):

        if key in self.module_inputs:
            self.selected_inputs["http/" + self.name + "/" + key] = self.module_inputs[key]
            self.selected_inputs["http/" + self.name + "/" + key]["call"] = partial(self.get_value, key)

            if 'set' in self.module_inputs[key] and self.module_inputs[key]['set']:
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
        return self._vars

    @Pre_5_15_2_fix('QVariantList', vars, notify=vars_changed)
    def vars(self, varlist):
        self._vars = varlist
        self.settings.setValue("http/" + self.name + "/vars", varlist)
