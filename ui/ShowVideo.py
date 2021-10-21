# -*- coding: utf-8 -*-

import logging

from PySide2.QtCore import QSettings, QObject, Property, Signal
from PySide2.QtGui import QPolygonF

from core.CircularBuffer import CircularBuffer
from core.Toolbox import Pre_5_15_2_fix


class ShowVideo(QObject):
    def __init__(self, name, inputs, settings: QSettings = None):

        super(ShowVideo, self).__init__()
        self.settings = settings
        #self.inputs = inputs
        self.name = name
        self._video_path = settings.value('showvideo/' + self.name + "/path", '')
        self._icon = settings.value('showvideo/' + self.name + "/icon", '')

    @Signal
    def settingsChanged(self):
        pass


    def delete_inputs(self):
        pass


    # @Property(str,notify=settingsChanged)
    def video_path(self):
        return self._video_path

    # @value_path.setter
    @Pre_5_15_2_fix(str, video_path, notify=settingsChanged)
    def video_path(self, key):
        logging.info('setter ' + key)
        self.settings.setValue('showvideo/' + self.name + "/path", key)
        logging.info(self.settings.value('showvideo/' + self.name + "/path", ''))
        self._video_path = key
        self.settingsChanged.emit()

    # @Property(str,notify=settingsChanged)
    def icon(self):
        return self._icon

    # @icon.setter
    @Pre_5_15_2_fix(str, icon, notify=settingsChanged)
    def icon(self, key):
        self._icon = key
        self.settings.setValue('showvideo/' + self.name + "/icon", key)
        self.settingsChanged.emit()


