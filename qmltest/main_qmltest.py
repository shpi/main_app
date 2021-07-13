from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QObject
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Signal, Property as QtProperty

from interfaces.PropertySystem import PropertyDict, Property, QtPropLink, properties_stop, properties_start
from interfaces.DataTypes import DataType

# from PySide2.QtQml import QQmlDebuggingEnabler
# debug = QQmlDebuggingEnabler()

# pyside2-rcc main_qmltest.qrc -o qmltestres.py --compress 9 --threshold 9
import qmltestres

properties_start()

pd = PropertyDict.root(allowcreate=True)


class Appearance(QObject):
    minChanged = Signal()
    maxChanged = Signal()
    nightChanged = Signal()

    minbacklight = QtPropLink(int, path="min", notify=minChanged)
    maxbacklight = QtPropLink(int, path="max", notify=maxChanged)

    def __init__(self):
        QObject.__init__(self)
        self._night = 0
        self.properties = PropertyDict(
            min=Property(DataType.INTEGER, 40),
            max=Property(DataType.INTEGER, 60)
        )
        self.instancename = None

    def get_night(self):
        return self._night

    def set_night(self, night):
        self._night = night

    night = QtProperty(int, get_night, set_night, notify=nightChanged)


app = QApplication([])
engine = QQmlApplicationEngine()

appearance = Appearance()
pd["Appearance"] = appearance.properties
pd.load()

root_context = engine.rootContext()
root_context.setContextProperty("appearance", appearance)

# url = QUrl("main_qmltest.qml")

engine.load("main_qmltest.qml")

app.exec_()
del engine

properties_stop()
