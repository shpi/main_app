# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtCore  import QObject, QUrl, QUrlQuery
from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine

from Backlight import Backlight
from Weather import WeatherWrapper


os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
os.environ["QT_QPA_PLATFORM"] = "eglfs"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/usr/local/qt5pi/plugins/platforms"
os.environ["LD_LIBRARY_PATH"]= "/usr/local/qt5pi/lib"
os.environ["GST_DEBUG"] = "omx:4"



def main():

    app = QApplication(sys.argv)
    API_KEY = "20f7aab0a600927a8486b220200ee694"

    weather = WeatherWrapper()
    weather.api_key = API_KEY
    backlight = Backlight()



    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("weather", weather)
    engine.rootContext().setContextProperty("backlight", backlight)

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "qml/main.qml")

    engine.load(QUrl.fromLocalFile(filename))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()





