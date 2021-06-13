import logging
from subprocess import Popen, PIPE
from threading import Thread

# import socket for later audio intercom
from core.DataTypes import DataType
from core.Property import EntityProperty


class AlsaRecord:
    def __init__(self, inputs, card='1'):
        self.inputs = inputs
        self.input = dict()
        self.name = card

        self._control = EntityProperty(parent=self,
                                       category='sound',
                                       entity=card,
                                       value=1,
                                       name='thread',
                                       description='Microphone thread',
                                       type=DataType.UNDEFINED,  # TODO
                                       set=self.control,
                                       call=self.check_process,
                                       interval=60)

        self.card = card
        self.bufferpos = 0
        self.buffersize = 10
        self.buffer = [b'' for x in range(self.buffersize)]
        self.rate = 44100

        self.input = EntityProperty(parent=self,
                                    category='sound',
                                    entity=card,
                                    value=0,
                                    name='microphone',
                                    description='Microphone volume',
                                    type=DataType.PERCENT_INT,
                                    interval=-1)

        self.format = 'S16_LE'
        self.bits = 16  # S8, S16_LE, S32_BE ..
        self.channels = 1
        self.chunksize = int((self.rate * (self.bits / 8) * self.channels) // 10)

        self.arecord_process = None
        self.thread_stdout = None
        self.thread_stderr = None

        self._control.value = self.check_process()

    def control(self, onoff):
        logging.error('Microphone thread control called with: ' + str(onoff))
        self._control.value = onoff
        self.check_process()

    def delete_inputs(self):
        return [self.input.path, self._control.path]

    def get_inputs(self) -> list:
        return [self.input, self._control]

    def process_arecord_stdout(self, arecord_process):  # output-consuming thread
        while self._control.value:
            for i in range(0, self.buffersize):
                self.bufferpos = i
                self.buffer[i] = arecord_process.stdout.read(self.chunksize)

    def process_arecord_stderr(self, arecord_process):
        dat = bytearray()
        value = -1

        while self._control.value:
            buf = arecord_process.stderr.read(1)
            if buf == b'\r':
                if dat.endswith(b'MAX'):
                    value = 100
                elif dat.endswith(b'%'):
                    value = int(dat[-3:-1])

                self.input.value = value

                dat = bytearray()
            else:
                dat += buf

    def check_process(self):
        if self._control.value:
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

        return self._control.value
