# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property
import time
import os
import threading
from datetime import datetime
from core.DataTypes import DataType
from core.Toolbox import Pre_5_15_2_fix
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse as urlparse
import json
from core.DataTypes import Convert

class ServerHandler(BaseHTTPRequestHandler):

    inputs = None

    def do_GET(self):
        start_time = time.time()
        try:
            succ = True

            if "?" in self.path:
                query = dict(urlparse.parse_qsl(self.path.split("?")[1], True))
            else:
                succ = False

            if succ and ('key' in query) and (query['key'] in self.inputs) and self.inputs[query['key']].get('exposed', False):


                     if ('set' in query):
                         self.inputs[query['key']]['set'](query['set'])


                     value = self.inputs[query['key']]
                     self.send_response(200)
                     self.send_header('Content-type', 'text')
                     self.end_headers()
                     message = '{'
                     #message += '"description":"' + str(value.get('description', '')) + '",'
                     #message += '"type":"' + Convert.type_to_str(value["type"]) + '",'
                     message += '"lastupdate":' + str(value.get('lastupdate', '')) + ','
                     #if 'set' in value: message += '"set": true,'
                     message += '"interval":' + str(value.get('interval', '0')) + ','
                     message += '"value":"' + str(value.get('value', '')) + '"}'

                     #print(json.loads(message))

                     self.wfile.write(bytes(message, "utf8"))
                     self.connection.close()

            else:
                succ = False


            if not succ:
                self.send_response(200)
                self.send_header('Content-type', 'text')
                self.end_headers()
                message = '{'
                #exposed = list(filter(lambda x: self.inputs[x]['exposed'], self.inputs.keys()))

                for key, value in self.inputs.items():
                   if value['exposed'] == True:

                       message += '"' + key + '":{'
                       message += '"description":"' + str(value.get('description', '')) + '",'
                       message += '"type":"' + Convert.type_to_str(value["type"]) + '",'
                       message += '"lastupdate":' + str(value.get('lastupdate', '')) + ','
                       if 'set' in value: message += '"set": true,'
                       message += '"interval":' + str(value.get('interval', '0')) + ','
                       message += '"value":"' + str(value.get('value', '')) + '"'

                       #print('<td>' + str(value.get('available', '')) + '</td>')
                       #print('<td>' + str(value.get('min', '')) + '</td>')
                       #print('<td>' + str(value.get('max', '')) + '</td>')
                       #print('<td>' + str(value.get('step', '')) + '</td>')
                       message += '},'

                message = message[0:-1]
                message += '}'

                #print(json.loads(message))

                self.wfile.write(bytes(message, "utf8"))

                #self.wfile.write(bytes(json.dumps(exposed), "utf8"))

                self.connection.close()
        except Exception as e:
            print(e)
            self.send_response(400)
            self.connection.close()

        print("request finished in:  %s seconds" %
                          (time.time() - start_time))
        #return

    def log_request(self, code):

        pass

    def do_POST(self):
        self.do_GET()

    def end_headers(self):
        try:
            super().end_headers()
        except BrokenPipeError as e:
            self.connection.close()
            print('httpserver error: {}'.format(e))




class HTTPServer(QObject):
    def __init__(self, inputs, settings: QSettings):
        super().__init__()


        self.settings = settings
        self._port = int(settings.value("httpserver/port", 9000))

        ServerHandler.inputs = inputs.entries
        self.server = ThreadingHTTPServer(("0.0.0.0", self._port), ServerHandler)


        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

        #server.shutdown()
        #server_thread.join()



    @Signal
    def port_changed(self):
        pass

    # @Property(int, notify=dim_timer_changed)
    def port(self):
        return int(self._dim_timer)

    @Pre_5_15_2_fix(int, port, notify=port_changed)
    def port(self, value):
        self._port = int(value)
        self.settings.setValue("httpserver/port", value)
