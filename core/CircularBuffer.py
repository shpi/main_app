import datetime
import ctypes
import time
import numpy as np
import shiboken2
from PySide2.QtGui import QPolygonF

class CircularBuffer:
    def __init__(self, length=100, initialvalue=0, dtype=np.float):
        super(CircularBuffer, self).__init__()
        self._time = np.full(length, np.datetime64(int(time.time() * 1000), 'ms'), dtype='datetime64[ms]')
        self._data = np.full(length, initialvalue, dtype=dtype)
        self._index = 0
        self._count = 0
        self._length = length
        self._datatype = dtype

    def append(self, value, datetime_value=None):
        if datetime_value is None: 
            datetime_value = time.time()
        self._time[self._index] = np.datetime64(int(datetime_value * 1000), 'ms')
        self._data[self._index] = value
        self._count = min(self._count + 1, self._length)  # Cap the count at _length
        self._index = (self._index + 1) % self._length    # Wrap around using modulo

    def length(self):
        return min(self._count, self._length)

    def _get_circular_slice(self, array, size=None):
        if size is None or size > self._count:
            size = self._count
        if self._count < self._length:
            return array[:self._index][-size:]
        else:
            return np.concatenate((array[self._index:], array[:self._index]))[-size:]

    def data(self, size=None):
        return self._get_circular_slice(self._data, size)

    def time(self, size=None):
        return self._get_circular_slice(self._time, size)

    def min_time(self):
        return self._time[self._index].astype(datetime.datetime) if self._count >= self._length else self._time[0].astype(datetime.datetime)

    def max_time(self):
        return self._time[(self._index - 1) % self._length].astype(datetime.datetime)

    def min_data(self):
        return np.min(self.data()) if self._count > 0 else None

    def max_data(self):
        return np.max(self.data()) if self._count > 0 else None

    def preview(self, width=100, height=100, divider=1):
        if self._count == 0:
            return QPolygonF()  # Return empty QPolygonF if no data

        startx = self.min_time()
        endx = self.max_time()

        if startx == endx:
            return QPolygonF()  # Return empty QPolygonF if insufficient data range

        scalex = width / ((endx - startx).total_seconds() * 1000)
        max = self.max_data()
        min = self.min_data()

        if min == max:
            return QPolygonF()  # Return empty QPolygonF if no data variation

        scaley = height / (abs(min - max))
        size = self.length()
        polyline = QPolygonF(size)
        buffer = (ctypes.c_double * 2 * size).from_address(shiboken2.getCppPointer(polyline.data())[0])
        memory = np.frombuffer(buffer, np.float)

        time_data = self.time(size)
        data = self.data(size)

        memory[: (size - 1) * 2 + 1: 2] = (time_data - np.datetime64(startx, 'ms')).astype(float) * scalex
        memory[1: (size - 1) * 2 + 2: 2] = height - (data - min) * scaley

        return polyline
