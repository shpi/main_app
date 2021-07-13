# -*- coding: utf-8 -*-

from typing import List, Dict, Any

from PySide2.QtWidgets import QApplication


class MainAppBase(QApplication):
    def __init__(self, args: List[str]):
        QApplication.__init__(self, args)
        # self._root_propertydict = ModuleInstancePropertyDict(parent=None)
        # if self._root_propertydict is not PropertyDict.root(allowcreate=False):
        #    raise Exception("Root PropertyDict has been defined anywhere else before.")

    def qml_context_properties(self) -> Dict[str, Any]:
        """
        Properties identified by str exposed to qml top level
        """
