# -*- coding: utf-8 -*-

from PySide2.QtCore import QSettings, QObject, Signal, Slot, Property
import time
import os
import threading
from datetime import datetime
from core.DataTypes import DataType
from core.Toolbox import Pre_5_15_2_fix
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
#import urlparse
import urllib.parse as urlparse


class ServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        try:
            if "?" in self.path:
                start_time = time.time()
                message = 'SHPI'
                self.send_response(200)

                print('http request from: ' + self.client_address[0])

                print(dict(urlparse.parse_qsl(self.path.split("?")[1], True)))

                self.send_header('Content-type', 'text')
                self.end_headers()

                self.wfile.write(bytes(message, "utf8"))
                self.connection.close()

                print("request finished in:  %s seconds" %
                              (time.time() - start_time))

            else:
                self.send_response(202)
                message = ''

                for key in self.inputs:
                    message += ', ' + key
                self.wfile.write(bytes(message, "utf8"))

                self.connection.close()
        except Exception as e:
            print(e)
            self.send_response(400)
            self.connection.close()

        return

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

        self.inputs = inputs.entries
        self.settings = settings
        self._port = int(settings.value("httpserver/port", 9000))

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

