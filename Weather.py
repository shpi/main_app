from PySide2.QtCore import QSettings, Qt, QModelIndex, QAbstractListModel, Property, Signal, Slot, QObject, QUrl, QUrlQuery
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
import logging
import os
import json
import time
import datetime


class CityModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1000
    StateRole = Qt.UserRole + 1001
    LatRole = Qt.UserRole + 1002
    LonRole = Qt.UserRole + 1003
    CountryRole = Qt.UserRole + 1004

    def __init__(self, entries=[], parent=None):
        super(CityModel, self).__init__(parent)
        self._entries = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self._entries[index.row()]
            if role == CityModel.NameRole:
                return item["name"]
            elif role == CityModel.StateRole:
                return item["stat"]
            elif role == CityModel.LonRole:
                return item["lon"]
            elif role == CityModel.LatRole:
                return item["lat"]
            elif role == CityModel.CountryRole:
                return item["country"]

    def roleNames(self):
        roles = dict()
        roles[CityModel.NameRole] = b"name"
        roles[CityModel.StateRole] = b"stat"
        roles[CityModel.LatRole] = b"lat"
        roles[CityModel.LonRole] = b"lon"
        roles[CityModel.CountryRole] = b"country"
        return roles

    def appendRow(self, n):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._entries.append(n)
        self.endInsertRows()


class WeatherWrapper(QObject):

    BASE_URL = "http://api.openweathermap.org/data/2.5/onecall?"

    def __init__(self, path: str = "weather",
                 settings: QSettings = None, parent: QObject = None):

        super(WeatherWrapper, self).__init__(parent)
        self.settings = settings
        self.path = path
        self._data = dict()
        self._cities = CityModel()
        self.weatherinputs = dict()

        self.weatherinputs[self.path + '/sunrise'] = dict({"description" : "sunrise time","type" : "time","interval" : -1,  'value' : settings.value(self.path + "/sunrise", "6:00")})
        self.weatherinputs[self.path + '/sunset'] = dict({"description" : "sunset time","type" : "time","interval" : -1, 'value' : settings.value(self.path + "/sunset", "22:00")})
        self.weatherinputs[self.path + '/lastupdate'] = dict({"description" : "lastUpdate time","type" : "time","interval" : -1})
        self.weatherinputs[self.path + '/current_pressure'] = dict({"description" : "pressure in Pa","type" : "float","interval" : -1})
        self.weatherinputs[self.path + '/current_humidity'] = dict({"description" : "humidity in %","type" : "percent","interval" : -1})
        self.weatherinputs[self.path + '/current_wind_speed'] = dict({"description" : "windspeed in kpH","type" : "float","interval" : -1})
        self.weatherinputs[self.path + '/current_wind_deg'] = dict({"description" : "Wind direction in Degrees","type" : "int","interval" : -1})
        self.weatherinputs[self.path + '/current_clouds'] = dict({"description" : "Cloudiness in %","type" : "percent","interval" : -1})
        self.weatherinputs[self.path + '/current_pop'] = dict({"description" : "Possibility of precipation in %","type" : "percent","interval" : -1})
        self.weatherinputs[self.path + '/current_uvi'] = dict({"description" : "UV Index","type" : "float","interval" : -1})
        self.weatherinputs[self.path + '/current_rain'] = dict({"description" : "Rain per sqm in mm","type" : "float","interval" : -1})
        self.weatherinputs[self.path + '/current_temp'] = dict({"description" : "Temperature in °C","type" : "temperature","interval" : -1})
        self.weatherinputs[self.path + '/current_weather_icon'] = dict({"description" : "Weather icon","type" : "string","interval" : -1})
        self.weatherinputs[self.path + '/current_weather_desc'] = dict({"description" : "Weather description","type" : "string","interval" : -1})
        self.weatherinputs[self.path + '/current_dew_point'] = dict({"description" : "dew point in °C","type" : "temperature","interval" : -1})
        self.weatherinputs[self.path + '/city'] = dict({"description" : "City","type" : "string","interval" : -1, "value" : settings.value(self.path + "/city", "")})
        self.weatherinputs[self.path + '/lat'] = dict({"description" : "Latitude","type" : "float","interval" : -1,  "value" : settings.value(self.path + "/lat", "")})
        self.weatherinputs[self.path + '/lon'] = dict({"description" : "Longitude","type" : "float","interval" : -1, "value" : settings.value(self.path + "/lon", "")})

        self._has_error = False
        self._api_key = settings.value(self.path + "/api_key",
                                       "20f7aab0a600927a8486b220200ee694")
        self._current_date = ""
        self._interval = int(settings.value(self.path + "/interval", 60*60*6))


    def get_inputs(self) -> dict:
        return self.weatherinputs

    @property
    def manager(self) -> QNetworkAccessManager:
        return QNetworkAccessManager(self)

    @Property(str)
    def sunrise(self):
        return self.weatherinputs[self.path + '/sunrise']['value']

    @Property(str)
    def sunset(self):
        return self.weatherinputs[self.path + '/sunset']['value']

    @Property(str)
    def current_date(self):
        return self._current_date

    @Signal
    def api_keyChanged(self):
        pass

    @Property(str, notify=api_keyChanged)
    def api_key(self):
        return self._api_key

    @api_key.setter
    def set_api_key(self, key):
        self._api_key = key
        self.settings.setValue(self.path + "/api_key", key)

    @Property(str)
    def lat(self):
        return self.weatherinputs[self.path + '/lat']['value']

    @lat.setter
    def set_lat(self, lat):
        self.weatherinputs[self.path + '/lat']['lastupdate'] = time.time()
        self.weatherinputs[self.path + '/lat']['value'] = lat
        self.settings.setValue(self.path + "/lat", lat)

    @Signal
    def intervalChanged(self):
        pass

    @Property(int, notify=intervalChanged)
    def interval(self):
        return self._interval

    @interval.setter
    def set_interval(self, interval):
        self._interval = int(interval)
        self.settings.setValue(self.path + "/interval", interval)

    @Property(str)
    def lon(self):
        return self.weatherinputs[self.path + '/lon']['value']

    @lon.setter
    def set_lon(self, lon):
        self.weatherinputs[self.path + '/lon']['lastupdate'] = time.time()
        self.weatherinputs[self.path + '/lon']['value'] = lon
        self.settings.setValue(self.path + "/lon", lon)

    @Signal
    def cityChanged(self):
        pass

    @Property(str, notify=cityChanged)
    def city(self):
        return self.weatherinputs[self.path + '/city']['value']

    @city.setter
    def set_city(self, city: str) -> None:
        self.weatherinputs[self.path + '/city']['lastupdate'] = time.time() 
        self.weatherinputs[self.path + '/city']['value'] = city
        self.settings.setValue(self.path + "/city", city)
        self.cityChanged.emit()

    @Signal
    def dataChanged(self):
        pass

    @Property("QVariantMap", notify=dataChanged)
    def data(self) -> dict:
        return self._data

    @Signal
    def citiesChanged(self):
        pass

    @Property(QObject, notify=citiesChanged)
    def cities(self):
        return self._cities

    @Slot(str)
    def update_cities(self, city: str) -> None:

        positions = {'\'': 71, '(': 321, '-': 343, '1': 597, '2': 630, '6': 790,
                     'a': 823, 'b': 370614, 'c': 945166, 'd': 1476711, 'e': 1713503,
                     'f': 1877167, 'g': 2044843, 'h': 2351231, 'i': 2611321, 'j': 2693767,
                     'k': 2785650, 'l': 3123644, 'm': 3532057, 'n': 4051031, 'o': 4296924,
                     'p': 4461577, 'q': 4913273, 'r': 4949714, 's': 5209484, 't': 6080062,
                     'u': 6384291, 'v': 6449785, 'w': 6696941, 'x': 6919821, 'y': 6948590,
                     'z': 7007176, 'à': 7087615, 'á': 7087669, 'â': 7091789, 'ä': 7091819,
                     'å': 7092421, 'æ': 7094192, 'ç': 7094262, 'è': 7096683, 'é': 7096745,
                     'í': 7102778, 'î': 7103128, 'ð': 7103237, 'ñ': 7103306, 'ò': 7103396,
                     'ó': 7103512, 'ô': 7104100, 'ö': 7104262, 'ø': 7107426, 'ú': 7107904,
                     'ü': 7108891, 'ý': 7110541, 'þ': 7110614, 'á': 7110646, 'ā': 7110684,
                     'ć': 7112569, 'č': 7112700, 'ď': 7115548, 'đ': 7115580, 'ē': 7115647,
                     'ħ': 7115683, 'ī': 7115744, 'i̇': 7115833, 'ķ': 7116964, 'ļ': 7117057,
                     'ľ': 7117089, 'ł': 7117122, 'ō': 7120703, 'ő': 7122270, 'œ': 7122402,
                     'ř': 7122465, 'ś': 7122762, 'ş': 7124897, 'š': 7129301, 'ţ': 7132432,
                     'ū': 7133369, 'ŭ': 7133615, 'ż': 7133672, 'ž': 7135254, 'ə': 7137353,
                     'ș': 7137379, 'ј': 7137484, 'а': 7137523, 'б': 7137700, 'г': 7137814,
                     'з': 7137854, 'и': 7137894, 'к': 7137934, 'м': 7138017, 'о': 7138063,
                     'п': 7138101, 'р': 7138141, 'с': 7138182, 'ф': 7138317, 'ч': 7138369,
                     'ḏ': 7138404, 'ḥ': 7138439, 'ḩ': 7138471, 'ṟ': 7140489, 'ṭ': 7140525,
                     'ẕ': 7140655, 'ấ': 7140723, '‘': 7140812, '’': 7144455, '城': 7144974,
                     '御': 7145006, '松': 7145040, '芦': 7145071}

        self._cities = CityModel()
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "citylist.csv"), "r") as rf:
            i = 0
            city = city.lower()
            rf.seek(positions[city[0]], 0)
            line = rf.readline()
            while line:
                line = rf.readline()
                if (line[0].lower() != city[0]):
                    break
                if line.lower().startswith(city):
                    if (i > 100):
                        break
                    i += 1
                    line = line.split(";", 5)
                    self._cities.appendRow(dict(name=line[0],
                                                lat=line[3],
                                                lon=line[4].rstrip(),
                                                stat=line[1],
                                                country=line[2]))
        self.citiesChanged.emit()
        rf.close()

    """
        i = 0
        self._cities = CityModel()
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                  "city.list.json"), "r",  encoding="utf8") as rf:
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
        if ((self.weatherinputs[self.path + '/lon']['value'] != '') and (self.weatherinputs[self.path + '/lat']['value'] != '') and
           (self.weatherinputs[self.path + '/lastupdate']['value'] + self._interval) < time.time()):
 
            url = QUrl(WeatherWrapper.BASE_URL)
            query = QUrlQuery()
            query.addQueryItem("lat", str(self.weatherinputs[self.path + '/lat']['value']))
            query.addQueryItem("lon", str(self.weatherinputs[self.path + '/lon']['value']))
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

            self.weatherinputs[self.path + '/sunrise']['value'] =  datetime.datetime.fromtimestamp(int(d["current"]["sunrise"])).strftime('%H:%M:%S')
            self.weatherinputs[self.path + '/sunset']['value'] =  datetime.datetime.fromtimestamp(int(d["current"]["sunset"])).strftime('%H:%M:%S')
            self.weatherinputs[self.path + '/lastupdate']['value'] = int(d["current"]["dt"])
            self.weatherinputs[self.path + '/current_pressure']['value'] = float(d["current"]["pressure"])
            self.weatherinputs[self.path + '/current_humidity']['value'] = float(d["current"]["humidity"])
            self.weatherinputs[self.path + '/current_wind_speed']['value'] = float(d["current"]["wind_speed"])
            self.weatherinputs[self.path + '/current_wind_deg']['value'] = float(d["current"]["wind_deg"])
            self.weatherinputs[self.path + '/current_clouds']['value'] = float(d["current"]["clouds"])
            self.weatherinputs[self.path + '/current_pop']['value'] = float(d["current"]["pop"]) if 'pop' in d["current"] else 0
            self.weatherinputs[self.path + '/current_uvi']['value'] = float(d["current"]["uvi"])
            self.weatherinputs[self.path + '/current_rain']['value'] = float(d["current"]["rain"]) if 'rain' in d["current"] else 0
            self.weatherinputs[self.path + '/current_temp']['value'] = float(d["current"]["temp"])
            self.weatherinputs[self.path + '/current_weather_icon']['value'] = d.get("current", {}).get("weather", [{}])[0].get('icon')
            self.weatherinputs[self.path + '/current_weather_desc']['value'] = d.get("current", {}).get("weather", [{}])[0].get('description')
            self.weatherinputs[self.path + '/current_dew_point']['value'] = float(d["current"]["dew_point"])


            self.settings.setValue(f"{self.path}/sunset", self.weatherinputs[self.path + '/sunset']['value'])
            self.settings.setValue(f"{self.path}/sunrise", self.weatherinputs[self.path + '/sunrise']['value'])

            logging.debug(f"{self.current_date}: Weather: added forecast")

        else:
            self._data = dict()
            has_error = True
            logging.debug(f"error: {reply.errorString()}")

        self._has_error = has_error
        self.dataChanged.emit()
        reply.deleteLater()
