# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtCore  import Qt, QModelIndex,QAbstractListModel,Property, Signal, Slot, QObject, QUrl, QUrlQuery
from PySide2.QtGui import QGuiApplication
from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine

from Backlight import Backlight
from Weather import WeatherWrapper


def main():


    app = QApplication(sys.argv)
    API_KEY = "20f7aab0a600927a8486b220200ee694"
    weather = WeatherWrapper()
    weather.api_key = API_KEY

    backlight = Backlight()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("weather", weather)
    engine.rootContext().setContextProperty("backlight", backlight)

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "main.qml")

    engine.load(QUrl.fromLocalFile(filename))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()





