# -*- coding: utf-8 -*-

import logging
import sys
import time
import urllib.parse as urlparse
from http.server import BaseHTTPRequestHandler

from PySide2.QtCore import Signal

from core.DataTypes import Convert
from core.Toolbox import Pre_5_15_2_fix, ThreadingHTTPServer
from core.Settings import settings
from interfaces.Module import ThreadModuleBase, ModuleCategories
from core.Module import Module


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
            exception_traceback = sys.exc_info()[2]
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line {line_number}')
            self.send_response(500)
            self.connection.close()

        logging.debug("request finished in:  %s seconds" %
                      (time.time() - start_time))
        # return

    def log_message(self, fmt, *args):
        logging.info("%s - [%s] %s", (self.address_string(), self.log_date_time_string(), fmt % args))

    def do_POST(self):
        self.do_GET()

    def end_headers(self):
        try:
            super().end_headers()
        except BrokenPipeError as e:
            self.connection.close()
            logging.error('httpserver error: {}'.format(e))


class HTTPServer(ThreadingHTTPServer, ThreadModuleBase):
    allow_maininstance = True
    allow_instances = False
    description = "HTTP Server"
    categories = (ModuleCategories._INTERNAL, )

    def __init__(self):
        # QObject.__init__(self)
        ThreadModuleBase.__init__(self)

        self._port = settings.int("httpserver/port", 9000)
        ThreadingHTTPServer.__init__(self, ('0.0.0.0', self._port), ServerHandler)

        ServerHandler.inputs = Module.inputs.entries

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
        settings.setint("httpserver/port", self._port)

    def stop(self):
        print("HTTPServer: Shutdown")
        self.shutdown()

    def load(self):
        pass

    def unload(self):
        self.server_close()

    def run(self) -> None:
        print("HTTPServer: Run")
        self.serve_forever()
        print("HTTPServer: End of run")
