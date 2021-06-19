# -*- coding: utf-8 -*-

from typing import List

from PySide2.QtWidgets import QApplication
from interfaces.PropertySystem import PropertyDict


class MainAppBase(QApplication):
    def __init__(self, args: List[str]):
        QApplication.__init__(self, args)
        self._root_propertydict = PropertyDict(parent=None)
        if self._root_propertydict is not PropertyDict.root(allowcreate=False):
            raise Exception("Root PropertyDict has been defined anywhere else before.")

    @property
    def property_root(self) -> PropertyDict:
        return self._root_propertydict
