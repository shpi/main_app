#from functools import cached_property
import json
import datetime
from PySide2.QtCore  import Qt, QModelIndex,QAbstractListModel,Property, Signal, Slot, QObject, QUrl, QUrlQuery
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlExtensionPlugin
from enum import Enum
import typing
import logging
import os

logging.basicConfig(level=logging.DEBUG)


class MyModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1000
    StateRole = Qt.UserRole + 1001
    LatRole = Qt.UserRole + 1002
    LonRole = Qt.UserRole + 1003
    CountryRole = Qt.UserRole + 1004

    def __init__(self, entries = [], parent=None):
        super(MyModel, self).__init__(parent)
        self._entries = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid(): return 0
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


class CityListModel(QAbstractListModel):

     class Roles(Enum):
           name = Qt.UserRole+0
           stat = Qt.UserRole+1
           lat = Qt.UserRole+2
           lon = Qt.UserRole+3
           country = Qt.UserRole+4

     def __init__(self, parent=None):
         super(CityListModel, self).__init__(parent)
         self._entries = []

     def rowCount(self, parent:QModelIndex=...) -> int:
                 return len(self._entries)

     def data(self, index:QModelIndex, role:int=...) -> typing.Any:
         if 0 <= index.row() < self.rowCount() and index.isValid():

             if role == QtCore.Qt.DisplayRole:
                         return self._entries[index.row()]["name"]
             if role == self.Roles.name.value:
                         return self._entries[index.row()]["name"]
             if role == self.Roles.stat.value:
                         return self._entries[index.row()]["stat"]
             if role == self.Roles.lat.value:
                         return self._entries[index.row()]["lat"]
             if role == self.Roles.lon.value:
                         return self._entries[index.row()]["lon"]
             if role == self.Roles.country.value:
                         return self._entries[index.row()]["country"]

     def roleNames(self) -> typing.Dict:
         roles = super().roleNames()
         roles[self.Roles.name.value] = QByteArray(b'name')
         roles[self.Roles.stat.value] = QByteArray(b'stat')
         roles[self.Roles.lat.value] = QByteArray(b'lat')
         roles[self.Roles.lon.value] = QByteArray(b'lon')
         roles[self.Roles.country.value] = QByteArray(b'country')

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
        i = 0
        self._cities = MyModel()
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "city.list.json"), "r",  encoding="utf8") as rf:
            city_data = json.load(rf)

        for s in range(len(city_data)):
            if city_data[s]["name"].lower().startswith(city.lower()):
                i += 1
                #print("FOUND {} {} ".format(city_data[s]["name"], city_data[s]["state"]))
                self._cities.appendRow(dict(name = city_data[s]["name"],
                                        lat = city_data[s]["coord"]['lat'],
                                        lon = city_data[s]["coord"]['lon'],
                                        stat = city_data[s]["state"],
                                        country = city_data[s]["country"]))
                if (i > 100):
                   break

        self.citiesChanged.emit()


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
            #logging.debug(f"data: {data}")
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

