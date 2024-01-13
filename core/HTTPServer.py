# -*- coding: utf-8 -*-
import os
from PIL import Image
from io import BytesIO
import cgi
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



    def do_POST(self):
     logging.debug("POST request received")

     try:
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        logging.debug("Form parsed")

        if 'file' in form:
            file_item = form['file']
            if file_item.filename:
                logging.debug(f"Received file: {file_item.filename}")
                file_data = file_item.file.read()
                image = Image.open(BytesIO(file_data))

                # Konvertieren nach JPG, wenn PNG
                if file_item.filename.lower().endswith('.png'):
                    logging.debug("Converting PNG to JPG")
                    image = image.convert('RGB')
                    file_path = os.path.join('backgrounds', os.path.splitext(file_item.filename)[0] + '.jpg')
                else:
                    file_path = os.path.join('backgrounds', file_item.filename)

                # Zielgröße
                target_width, target_height = 800, 480

                # Bildseitenverhältnis beibehalten und sicherstellen, dass es die Zielgröße füllt
                image_ratio = image.width / image.height
                target_ratio = target_width / target_height

                if image_ratio > target_ratio:
                    # Bild ist breiter als Zielverhältnis
                    scale = target_height / image.height
                else:
                    # Bild ist höher als Zielverhältnis
                    scale = target_width / image.width

                new_size = (int(image.width * scale), int(image.height * scale))
                image = image.resize(new_size, Image.ANTIALIAS)

                # Überschüssiges Bild abschneiden
                left = (image.width - target_width) / 2
                top = (image.height - target_height) / 2
                right = (image.width + target_width) / 2
                bottom = (image.height + target_height) / 2
                image = image.crop((left, top, right, bottom))

                # Bild speichern
                image.save(file_path + '.tmp', format='JPEG')
                os.rename(file_path + '.tmp', file_path)

                logging.debug(f"Image saved at {file_path}")

                self.send_response(200)
                self.end_headers()
                response = {'status': 'success', 'message': 'Image uploaded, converted, and resized'}
                self.wfile.write(json.dumps(response).encode())
                logging.debug("Response sent to client")
                return
            else:
                logging.error("No filename in the uploaded file")
                self.send_error(400, "No filename")
                return
        else:
            logging.error("No file field in the form")
            self.send_error(400, "No file field")
            return
     except Exception as e:
        logging.exception("Exception occurred in POST request")
        self.send_error(500, f"Server error: {e}")
        return




    def do_GET(self):
        start_time = time.time()
        query = {}  # Initialize query as an empty dictionary

        try:
            success = True
            if "?" in self.path:
                query = dict(urlparse.parse_qsl(self.path.split("?")[1], True))
            else:
                success = False


            if self.path == '/upload':
             self.send_response(200)
             self.send_header('Content-type', 'text/html')
             self.end_headers()

             html_form = """
             <html><body>
             <h2>Upload Image</h2>
             <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*">
                <input type="submit" value="Upload">
             </form>
             </body></html>
             """
             self.wfile.write(html_form.encode())
             return



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
        return int(self._port)

    @Pre_5_15_2_fix(int, port, notify=port_changed)
    def port(self, value):
        self._port = int(value)
        self.settings.setValue("httpserver/port", value)
