# -*- coding: utf-8 -*-
import json
import functools
import logging
import sys
import threading
import time
import urllib.parse as urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from PySide2.QtCore import QSettings, QObject, Signal

from core.DataTypes import Convert
from core.Toolbox import Pre_5_15_2_fix


class ServerHandler(BaseHTTPRequestHandler):
    inputs = None

    def do_GET(self):
        start_time = time.time()
        try:
            success = True
            if "?" in self.path:
                query = dict(urlparse.parse_qsl(self.path.split("?")[1], True))
            else:
                success = False


            if query.get('debug') == 'true':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                debug_message = self.format_debug_message()
                self.wfile.write(bytes(debug_message, "utf8"))
                self.connection.close()
                return

            if success and ('key' in query) and (query['key'] in self.inputs) and self.inputs[query['key']].exposed:

                if 'set' in query:
                    if self.inputs[query['key']].set is not None:
                        logging.debug(f'SET: {query["key"]} : {query["set"]}')
                        self.inputs[query['key']].value = float(query['set'])
                        self.inputs[query['key']].set(float(query['set']))

                value = self.inputs[query['key']]
                self.send_response(200)
                self.send_header('Content-type', 'text')
                self.end_headers()
                message = '{'
                # message += '"description":"' + str(value.description) + '",'
                # message += '"type":"' + Convert.type_to_str(value.type) + '",'
                message += '"last_update":' + str(value.last_update) + ','
                # if 'set' in value: message += '"set": true,'
                message += '"interval":' + str(value.interval) + ','
                message += '"value":"' + str(value.value) + '"}'

                # print(json.loads(message))

                self.wfile.write(bytes(message, "utf8"))
                self.connection.close()

            else:
                success = False

            if not success:
                self.send_response(200)
                self.send_header('Content-type', 'text')
                self.end_headers()
                message = '{'
                # exposed = list(filter(lambda x: self.inputs[x]['exposed'], self.inputs.keys()))

                for key, value in self.inputs.items():
                    if value.exposed:

                        message += '"' + key + '":{'
                        message += '"description":"' + str(value.description) + '",'
                        message += '"type":"' + Convert.type_to_str(value.type) + '",'
                        message += '"lastupdate":' + str(value.last_update) + ','
                        if value.set is not None:
                            message += '"set": true,'
                        message += '"interval":' + str(value.interval) + ','
                        message += '"value":"' + str(value.value) + '"'

                        # print('<td>' + str(value.get('available', '')) + '</td>')
                        # print('<td>' + str(value.get('min', '')) + '</td>')
                        # print('<td>' + str(value.get('max', '')) + '</td>')
                        # print('<td>' + str(value.get('step', '')) + '</td>')
                        message += '},'

                if message[-1] == ',':
                    message = message[:-1]
                message += '}'

                # print(json.loads(message))

                self.wfile.write(bytes(message, "utf8"))

                # self.wfile.write(bytes(json.dumps(exposed), "utf8"))

                self.connection.close()
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line {line_number}')
            self.send_response(400)
            self.connection.close()

        logging.debug("request finished in:  %s seconds" %
                      (time.time() - start_time))
        # return

    def format_debug_message(self):
     debug_dict = {}
     for key, value in self.inputs.items():
        entry = {}
        attributes = ['description', 'type', 'last_update', 'interval', 'value', 'set']
        for attr in attributes:
            if hasattr(value, attr):
                attr_value = getattr(value, attr)
                if attr == 'type':
                    attr_value = Convert.type_to_str(attr_value)
                elif isinstance(attr_value, functools.partial):  # Handle functools.partial objects
                    func_name = attr_value.func.__name__
                    attr_value = f"partial function: {func_name}"
                elif callable(attr_value):  # Handle other callable attributes like functions and methods
                    attr_value = getattr(attr_value, '__qualname__', getattr(attr_value, '__name__', 'callable'))
                entry[attr] = attr_value
        debug_dict[key] = entry

     return json.dumps(debug_dict, indent=4)

    def format_debug_message2(self):
    # Format the debug message with the contents of the inputs dictionary
     debug_message = '{'
     for key, value in self.inputs.items():
        debug_message += f'"{key}": {{'
        attributes = ['description', 'type', 'last_update', 'interval', 'value', 'set']  # List all possible attributes
        for attr in attributes:
            if hasattr(value, attr):
                attr_value = getattr(value, attr)
                if attr == 'type':  # Special handling for type attribute
                    attr_value = Convert.type_to_str(attr_value)
                if isinstance(attr_value, str):
                    debug_message += f'"{attr}": "{attr_value}",'
                else:
                    debug_message += f'"{attr}": {attr_value},'
        if debug_message.endswith(','):
            debug_message = debug_message[:-1]  # Remove the last comma
        debug_message += '},'
     if debug_message.endswith(','):
        debug_message = debug_message[:-1]  # Remove the last comma
     debug_message += '}'
     return debug_message




    def log_message(self, format, *args):
        logging.info("%s - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

    def do_POST(self):
        self.do_GET()

    def end_headers(self):
        try:
            super().end_headers()
        except BrokenPipeError as e:
            self.connection.close()
            logging.error('httpserver error: {}'.format(e))


class HTTPServer(QObject):
    def __init__(self, inputs, settings: QSettings):
        super().__init__()

        self.settings = settings
        self._port = int(settings.value("httpserver/port", 9000))

        ServerHandler.inputs = inputs.entries
        self.server = ThreadingHTTPServer(("0.0.0.0", self._port), ServerHandler)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

        # server.shutdown()
        # server_thread.join()

    @Signal
    def port_changed(self):
        pass

    def get_inputs(self):
        return []

    # @Property(int, notify=dim_timer_changed)
    def port(self):
        return int(self._dim_timer)

    @Pre_5_15_2_fix(int, port, notify=port_changed)
    def port(self, value):
        self._port = int(value)
        self.settings.setValue("httpserver/port", value)
