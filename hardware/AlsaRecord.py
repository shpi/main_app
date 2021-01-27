import logging
from subprocess import Popen, PIPE
from threading import Thread
# import socket for later audio intercom
import time
from core.DataTypes import DataType
from functools import partial


class AlsaRecord:

    def __init__(self, inputs, card='1'):

        super(AlsaRecord, self).__init__()
        self.inputs = inputs
        self.input = dict()
        self._control = {
            'type': DataType.BOOL,
            'lastupdate': 0,
            'description': 'Microphone Thread start/stop',
            'value': 1,
            'set': partial(self.control),
            'interval': 60,
            'call': self.check_process
        }
        self.card = card
        self.bufferpos = 0
        self.buffersize = 10
        self.buffer = [b'' for x in range(self.buffersize)]
        self.rate = 44100
        self.input['interval'] = -1
        self.input['type'] = DataType.PERCENT_INT
        self.input['lastupdate'] = 0
        self.input['description'] = card + ' mic volume'
        self.input['value'] = 0
        self.format = 'S16_LE'
        self.bits = 16  # S8, S16_LE, S32_BE ..
        self.channels = 1
        self.chunksize = int((self.rate * (self.bits / 8) * self.channels) // 10)
        # self.input['sending'] = False
        # self.input['receiver'] = [] for later use, to send audio packages for intercom
        self.arecord_process = None
        self.thread_stdout = None
        self.thread_stderr = None

        self._control['value'] = self.check_process()

    def control(self, onoff):
        self._control['value'] = onoff

    def delete_inputs(self):
        if f'alsa/{self.card}/recording' in self.inputs.entries:
            del self.inputs.entries[f'alsa/{self.card}/recording']
        if f'alsa/{self.card}/thread' in self.inputs.entries:
            del self.inputs.entries[f'alsa/{self.card}/recording']

    def get_inputs(self) -> dict:

        return {f'alsa/{self.card}/recording': self.input,
                f'alsa/{self.card}/thread': self._control
                }

    def process_arecord_stdout(self, arecord_process):  # output-consuming thread

        while self._control['value'] > 0:
            for i in range(0, self.buffersize):
                self.bufferpos = i
                self.buffer[i] = arecord_process.stdout.read(self.chunksize)

    def process_arecord_stderr(self, arecord_process):
        dat = bytearray()
        value = -1

        while self._control['value'] > 0:
            buf = arecord_process.stderr.read(1)
            if buf == b'\r':
                if dat.endswith(b'MAX'):
                    value = 100
                elif dat.endswith(b'%'):
                    value = int(dat[-3:-1])

                if value != self.input['value']:
                    self.input['value'] = value
                    self.input['lastupdate'] = time.time()
                    self.inputs.update_remote([f'alsa/{self.card}/recording'])
                dat = bytearray()
            else:
                dat += buf

    def check_process(self):

        if self._control['value'] > 0:
            if not self.arecord_process or self.arecord_process.poll() is not None:
                logging.debug('starting arecord process on ' + self.card)
                self.arecord_process = Popen(
                    ['arecord', '-D', 'plughw:' + self.card, '-c', str(self.channels), '-r', str(
                        self.rate), '-t', 'raw', '-f', self.format, '-V', 'mono'], stdout=PIPE,
                    stderr=PIPE)  # output-producing process

            if not self.thread_stdout or not self.thread_stdout.is_alive():
                self.thread_stdout = Thread(target=self.process_arecord_stdout, args=(
                    self.arecord_process,))  # output-consuming thread
                self.thread_stdout.start()

            if not self.thread_stderr or not self.thread_stderr.is_alive():
                self.thread_stderr = Thread(target=self.process_arecord_stderr, args=(
                    self.arecord_process,))  # output-consuming thread
                self.thread_stderr.start()

        # kill process; will automatically stop thread
        elif self.arecord_process and self.arecord_process.poll() is None:
            self.arecord_process.kill()
            self.arecord_process.wait()

        return self._control['value']
