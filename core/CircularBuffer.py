
#from core.DataTypes import DataType
#from core.Toolbox import Pre_5_15_2_fix
import logging
import time
import datetime
import numpy as np


class CircularBuffer():

    #version = "1.0"
    #required_packages = 'numpy',
    #allow_instances = True
    #description = "CircularBuffer based on Numpy arrays"

    def __init__(self, length=100, dtype=np.float):

        super(CircularBuffer, self).__init__()


        self._time = np.zeros(length, dtype='datetime64[ms]')
        self._data = np.zeros(length, dtype=dtype)
        self._index = 0
        self._count = 0
        self._length = length
        self._datatype = dtype

    def append(self, value, datetimevalue=None):

        if datetimevalue == None: datetimevalue = time.time()
        self._time[self._index] = np.datetime64(int(datetimevalue*1000),'ms')

        self._data[self._index] = value

        self._count += 1
        self._index += 1

        if self._index == self._length: self._index = 0


    def length(self):

        if self._count <= self._length:
            return self._count
        else:
            return self._length

    def data(self):

        if self._count < self._length:
            return self._data[:self._index]
        else:
            return np.r_[self._data[self._index:],self._data[:self._index]]


    def time(self):

        if self._count < self._length:
            return self._time[:self._index]
        else:
            return np.r_[self._time[self._index:],self._time[:self._index]]


    def min_time(self):

        if self._count < self._length:
            return self._time[0].astype(datetime.datetime)
        else:
            return self._time[self._index].astype(datetime.datetime)


    def max_time(self):
        return self._time[self._index-1].astype(datetime.datetime)



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















