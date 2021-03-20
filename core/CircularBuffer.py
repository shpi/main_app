# from core.DataTypes import DataType
# from core.Toolbox import Pre_5_15_2_fix
import ctypes
import datetime
import time

import numpy as np
import shiboken2
from PySide2.QtGui import QPolygonF


class CircularBuffer:

    # version = "1.0"
    # required_packages = 'numpy',
    # allow_instances = True
    # description = "CircularBuffer based on Numpy arrays"

    def __init__(self, length=100, initialvalue = 0, dtype=np.float):

        super(CircularBuffer, self).__init__()

        self._time = np.full(length, np.datetime64(int(time.time() * 1000), 'ms'), dtype='datetime64[ms]')
        self._data = np.full(length, initialvalue, dtype=dtype)
        self._index = 0
        self._count = 0
        self._length = length
        self._datatype = dtype

    def append(self, value, datetime_value=None):

        if datetime_value is None: datetime_value = time.time()
        self._time[self._index] = np.datetime64(int(datetime_value * 1000), 'ms')
        self._data[self._index] = value
        self._count += 1
        self._index += 1
        if self._index == self._length: self._index = 0

    def length(self):

        if self._count <= self._length:
            return self._count
        else:
            return self._length

    def data(self, size=None):

        if size:
            if size > self._length:
                size = self._length
            elif size > self._count:
                size = self._count

        if self._count < self._length:
            if size is not None:
                return self._data[self._index - size:self._index]
            else:
                return self._data[:self._index]
        else:
            if size is not None:
                if size > self._index:
                    return np.r_[self._data[self._index - size:], self._data[:self._index]]
                if size <= self._index:
                    return self._data[self._index - size:self._index]
            else:
                return np.r_[self._data[self._index:], self._data[:self._index]]

    def time(self, size=None):

        if size:
            if size > self._length:
                size = self._length
            elif size > self._count:
                size = self._count

        if self._count < self._length:
            if size is not None:
                return self._time[self._index - size:self._index]
            else:
                return self._time[:self._index]
        else:
            if size is not None:
                if size > self._index:
                    return np.r_[self._time[self._index - size:], self._time[:self._index]]
                if size <= self._index:
                    return self._time[self._index - size:self._index]
            else:
                return np.r_[self._time[self._index:], self._time[:self._index]]

    def min_time(self):

        if self._count < self._length:
            return self._time[0].astype(datetime.datetime)
        else:
            return self._time[self._index].astype(datetime.datetime)

    def max_time(self):
        return self._time[self._index - 1].astype(datetime.datetime)

    def min_data(self):

        if self._count < self._length:
            return np.min(self._data[:self._index])
        else:
            return np.min(self._data)

    def max_data(self):

        if self._count < self._length:
            return np.max(self._data[:self._index])
        else:
            return np.max(self._data)

    def preview(self, width=100, height=100, divider=1):

        startx = self.min_time()
        endx = self.max_time()

        scalex = 1

        if (startx != endx):
            scalex = width / ((endx - startx).total_seconds() * 1000)

        max = self.max_data()
        min = self.min_data()

        scaley = 1

        if (min != max):
            scaley = height / (abs(min - max))



        size = self.length()
        polyline = QPolygonF(size)
        buffer = (ctypes.c_double * 2 * size).from_address(shiboken2.getCppPointer(polyline.data())[0])
        memory = np.frombuffer(buffer, np.float)
        memory[: (size - 1) * 2 + 1: 2] = (self.time() - np.datetime64(startx, 'ms')).astype(
            float) * scalex
        memory[1: (size - 1) * 2 + 2: 2] = height - (self.data() - min) * scaley

        return polyline
