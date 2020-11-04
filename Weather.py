#from functools import cached_property
import json
import datetime
from PySide2.QtCore  import QByteArray, Qt, QModelIndex,QAbstractListModel, Property, Signal, Slot, QObject, QUrl, QUrlQuery
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlExtensionPlugin
from enum import Enum
import typing
import logging
import os


os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
os.environ["QT_QPA_PLATFORM"] = "eglfs"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/usr/local/qt5pi/plugins/platforms"
os.environ["LD_LIBRARY_PATH"]= "/usr/local/qt5pi/lib"
os.environ["GST_DEBUG"] = "omx:4"



logging.basicConfig(level=logging.DEBUG)


class MyModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1000
    StateRole = Qt.UserRole + 1001
    LatRole = Qt.UserRole + 1002
    LonRole = Qt.UserRole + 1003
    CountryRole = Qt.UserRole + 1004

    def __init__(self, entries=[], parent=None):
        super(MyModel, self).__init__(parent)
        self._entries = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self._entries[index.row()]
            if role == MyModel.NameRole:
                return item["name"]
            elif role == MyModel.StateRole:
                return item["stat"]
            elif role == MyModel.LonRole:
                return item["lon"]
            elif role == MyModel.LatRole:
                return item["lat"]
            elif role == MyModel.CountryRole:
                return item["country"]

    def roleNames(self):
        roles = dict()
        roles[MyModel.NameRole] = b"name"
        roles[MyModel.StateRole] = b"stat"
        roles[MyModel.LatRole] = b"lat"
        roles[MyModel.LonRole] = b"lon"
        roles[MyModel.CountryRole] = b"country"
        return roles

    def appendRow(self, n):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._entries.append(n)
        self.endInsertRows()



class WeatherWrapper(QObject):

    BASE_URL = "http://api.openweathermap.org/data/2.5/onecall?"


    def __init__(self, api_key: str ="", parent: QObject = None):
        super(WeatherWrapper, self).__init__(parent)

        self._data = dict()
        self._cities = MyModel()
        self._city = " test "
        self._lat = ""
        self._lon = ""
        self._has_error = False
        self._api_key = api_key
        self._current_date = ""
        self._sunrise = ""
        self._sunset =  ""

    @property
    def manager(self) -> QNetworkAccessManager:
        return QNetworkAccessManager(self)

    @property
    def api_key(self):
        return self._api_key

    @Property(str)
    def lon(self):
        return self._lon

    @Property(str)
    def sunrise(self):
        return self._sunrise

    @Property(str)
    def sunset(self):
        return self._sunset


    @Property(str)
    def current_date(self):
        return self._current_date



    @Property(str)
    def lat(self):
        return self._lat


    @api_key.setter
    def api_key(self, key):
        self._api_key = key


    @Slot(str)
    def set_api_key(self, key: str) -> None:
         self._api_key = key

    @lat.setter
    def lat(self, lat):
            self._lat = lat

    @Slot(str)
    def set_lat(self, lat: str) -> None:
        self._lat = lat

    @lon.setter
    def lon(self, lon):
         self._lon = lon

    @Slot(str)
    def set_lon(self, lon: str) -> None:
        self._lon = lon

    def set_city(self, city: str) -> None:
         self._city = city
         self.cityChanged.emit()

    def read_city(self):
        return self._city

    @Signal
    def dataChanged(self):
        pass


    @Signal
    def citiesChanged(self):
        pass

    @Signal
    def cityChanged(self):
        pass

    city = Property(str, read_city, set_city, notify=cityChanged)

    @Property("QVariantMap", notify=dataChanged)
    def data(self) -> dict:
        return self._data

    @Property(QObject, notify=citiesChanged, constant=False)
    def cities(self):
        return self._cities

    @Slot(str)
    def update_cities(self, city: str) -> None:

        positions = {'\'': 71,'(': 321,'-': 343,'1': 597,'2': 630,'6': 790,
                     'a': 823,'b': 370614,'c': 945166,'d': 1476711,'e': 1713503,
                     'f': 1877167,'g': 2044843,'h': 2351231,'i': 2611321,'j': 2693767,
                     'k': 2785650,'l': 3123644,'m': 3532057,'n': 4051031,'o': 4296924,
                     'p': 4461577,'q': 4913273,'r': 4949714,'s': 5209484,'t': 6080062,
                     'u': 6384291,'v': 6449785,'w': 6696941,'x': 6919821,'y': 6948590,
                     'z': 7007176,'à': 7087615,'á': 7087669,'â': 7091789,'ä': 7091819,
                     'å': 7092421,'æ': 7094192,'ç': 7094262,'è': 7096683,'é': 7096745,
                     'í': 7102778,'î': 7103128,'ð': 7103237,'ñ': 7103306,'ò': 7103396,
                     'ó': 7103512,'ô': 7104100,'ö': 7104262,'ø': 7107426,'ú': 7107904,
                     'ü': 7108891,'ý': 7110541,'þ': 7110614,'á': 7110646,'ā': 7110684,
                     'ć': 7112569,'č': 7112700,'ď': 7115548,'đ': 7115580,'ē': 7115647,
                     'ħ': 7115683,'ī': 7115744,'i̇': 7115833,'ķ': 7116964,'ļ': 7117057,
                     'ľ': 7117089,'ł': 7117122,'ō': 7120703,'ő': 7122270,'œ': 7122402,
                     'ř': 7122465,'ś': 7122762,'ş': 7124897,'š': 7129301,'ţ': 7132432,
                     'ū': 7133369,'ŭ': 7133615,'ż': 7133672,'ž': 7135254,'ə': 7137353,
                     'ș': 7137379,'ј': 7137484,'а': 7137523,'б': 7137700,'г': 7137814,
                     'з': 7137854,'и': 7137894,'к': 7137934,'м': 7138017,'о': 7138063,
                     'п': 7138101,'р': 7138141,'с': 7138182,'ф': 7138317,'ч': 7138369,
                     'ḏ': 7138404,'ḥ': 7138439,'ḩ': 7138471,'ṟ': 7140489,'ṭ': 7140525,
                     'ẕ': 7140655,'ấ': 7140723,'‘': 7140812,'’': 7144455,'城': 7144974,
                     '御': 7145006,'松': 7145040,'芦': 7145071}


        self._cities = MyModel()
        with open("citylist.csv", "r") as rf:
            i = 0
            city = city.lower()
            rf.seek(positions[city[0]],0)
            line = rf.readline()
            while line:
                line = rf.readline()
                if (line[0].lower() != city[0]): break
                if line.lower().startswith(city):
                    if (i > 100): break
                    i += 1
                    line = line.split(";", 5)
                    self._cities.appendRow(dict(name = line[0],
                                        lat = line[3],
                                        lon = line[4].rstrip(),
                                        stat = line[1],
                                        country = line[2]))
        self.citiesChanged.emit()
        rf.close()

    """
        i = 0
        self._cities = MyModel()
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "city.list.json"), "r",  encoding="utf8") as rf:
            city_data = json.load(rf)

        for s in range(len(city_data)):
            if city_data[s]["name"].lower().startswith(city.lower()):
                i += 1
                self._cities.appendRow(dict(name = city_data[s]["name"],
                                        lat = city_data[s]["coord"]['lat'],
                                        lon = city_data[s]["coord"]['lon'],
                                        stat = city_data[s]["state"],
                                        country = city_data[s]["country"]))
                if (i > 100):
                   break

        self.citiesChanged.emit()
        rf.close()
    """
    @Slot(result=bool)
    def hasError(self):
        return self._has_error

    @Slot()
    def update(self) -> None:

        url = QUrl(WeatherWrapper.BASE_URL)
        query = QUrlQuery()
        query.addQueryItem("lat", self._lat)
        query.addQueryItem("lon", self._lon)
        query.addQueryItem("appid", self._api_key)
        query.addQueryItem("exclude", "minutely,hourly")
        query.addQueryItem("units", "metric")

        url.setQuery(query)

        request = QNetworkRequest(url)
        reply: QNetworkReply = self.manager.get(request)
        reply.finished.connect(self._handle_reply)

    def _handle_reply(self) -> None:
        has_error = False
        reply: QNetworkReply = self.sender()
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll().data()
            # logging.debug(f"data: {data}")
            d = json.loads(data)
            self._data = dict()
            has_error = False
            self._data = d

            self._current_date = datetime.datetime.fromtimestamp(int(d["current"]["dt"])).strftime('%m-%d-%Y %H:%M:%S')
            self._sunrise =  datetime.datetime.fromtimestamp(int(d["current"]["sunrise"])).strftime('%H:%M:%S')
            self._sunset = datetime.datetime.fromtimestamp(int(d["current"]["sunset"])).strftime('%H:%M:%S')
            logging.debug(f"added forecast from: {self.current_date}")


        else:
            self._data = dict()
            has_error = True
            logging.debug(f"error: {reply.errorString()}")
        self._has_error = has_error
        self.dataChanged.emit()
        reply.deleteLater()

