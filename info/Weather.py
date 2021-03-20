import datetime
import json
import logging
import os
import sys
import threading
import socket

import urllib.request
from urllib.error import HTTPError, URLError


from PySide2.QtCore import QSettings, Qt, QModelIndex, QAbstractListModel, Property, Signal, Slot, QObject
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from core.DataTypes import DataType
from core.Property import EntityProperty
from core.Toolbox import Pre_5_15_2_fix


class CityModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1000
    StateRole = Qt.UserRole + 1001
    LatRole = Qt.UserRole + 1002
    LonRole = Qt.UserRole + 1003
    CountryRole = Qt.UserRole + 1004

    def __init__(self):
        super(CityModel, self).__init__()
        self._entries = []

    def rowCount(self, parent=None):
        #if parent.isValid():
        #    return 0
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


class Weather(QObject):
    BASE_URL = "http://api.openweathermap.org/data/2.5/onecall?"

    def __init__(self, name, inputs,
                 settings: QSettings = None):

        super(Weather, self).__init__()
        self.settings = settings
        self.name = name
        self.inputs = inputs
        self._data = dict()
        self._cities = CityModel()
        self._properties = {}

        self._properties['module'] = EntityProperty(parent=self,
                                                    category='module/info',
                                                    entity=self.name,
                                                    value='NOT_INITIALIZED',
                                                    name=self.name,
                                                    description='Weather module: ' + self.name,
                                                    type=DataType.MODULE,
                                                    call=self.update,
                                                    interval=int(
                                                        settings.value('weather/' + self.name + '/interval', 1200)))

        self._properties['sunrise'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                     interval=-1, name='sunrise', description="sunrise time",
                                                     type=DataType.TIME,
                                                     value=settings.value('weather/' + self.name + "/sunrise", "6:00"))
        self._properties['sunset'] = EntityProperty(parent=self, category='info/weather', entity=self.name, interval=-1,
                                                    name='sunset', description="sunset time", type=DataType.TIME,
                                                    value=settings.value('weather/' + self.name + "/sunset", "22:00"))
        self._properties['current_pressure'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                              interval=-1, name='current_pressure',
                                                              description="pressure in Pa", type=DataType.PRESSURE)
        self._properties['current_humidity'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                              interval=-1, name='current_humidity',
                                                              description="humidity in %", type=DataType.HUMIDITY)
        self._properties['current_wind_speed'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                                interval=-1, name='current_wind_speed',
                                                                description="windspeed in kpH", type=DataType.VELOCITY)
        self._properties['current_wind_deg'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                              interval=-1, name='current_wind_deg',
                                                              description="Wind direction in Degrees",
                                                              type=DataType.DIRECTION)
        self._properties['current_clouds'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                            interval=-1, name='current_clouds',
                                                            description="Cloudiness in %", type=DataType.PERCENT_FLOAT)
        self._properties['current_pop'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                         interval=-1, name='current_pop',
                                                         description="Possibility of precipation in %",
                                                         type=DataType.PERCENT_FLOAT)
        self._properties['current_uvi'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                         interval=-1, name='current_uvi', description="UV Index",
                                                         type=DataType.UVINDEX)
        self._properties['current_rain'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                          interval=-1, name='current_rain',
                                                          description="Rain per sqm in mm", type=DataType.HEIGHT)
        self._properties['current_temp'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                          interval=-1, name='current_temp',
                                                          value = 0,
                                                          description="Temperature in °C", type=DataType.TEMPERATURE)
        self._properties['current_weather_icon'] = EntityProperty(parent=self, category='info/weather',
                                                                  entity=self.name, interval=-1,
                                                                  name='current_weather_icon',
                                                                  description="Weather icon", type=DataType.STRING)
        self._properties['current_weather_desc'] = EntityProperty(parent=self, category='info/weather',
                                                                  entity=self.name, interval=-1,
                                                                  name='current_weather_desc',
                                                                  description="Weather description",
                                                                  type=DataType.STRING)
        self._properties['current_dew_point'] = EntityProperty(parent=self, category='info/weather', entity=self.name,
                                                               interval=-1, name='current_dew_point',
                                                               description="dew point in °C", type=DataType.TEMPERATURE)
        self._properties['city'] = EntityProperty(parent=self, category='info/weather', entity=self.name, interval=-1,
                                                  name='city', description="City", type=DataType.STRING,
                                                  value=settings.value('weather/' + self.name + "/city", ""))
        self._properties['lat'] = EntityProperty(parent=self, category='info/weather', entity=self.name, interval=-1,
                                                 name='lat', description="Latitude", type=DataType.LATITUDE,
                                                 value=settings.value('weather/' + self.name + "/lat", ""))
        self._properties['lon'] = EntityProperty(parent=self, category='info/weather', entity=self.name, interval=-1,
                                                 name='lon', description="Longitude", type=DataType.LONGITUDE,
                                                 value=settings.value('weather/' + self.name + "/lon", ""))

        self._has_error = False
        self._api_key = settings.value('weather/' + self.name + "/api_key", "20f7aab0a600927a8486b220200ee694")
        self._current_date = ""

    def get_inputs(self) -> list:
        return list(self._properties.values())

    def delete_inputs(self):
        for key in self._properties:
            del self.inputs.entries[key]

    @property
    def manager(self) -> QNetworkAccessManager:
        return QNetworkAccessManager(self)

    @Property(str)
    def sunrise(self):
        return self._properties['sunrise'].value

    @Property(str)
    def sunset(self):
        return self._properties['sunset'].value

    @Property(str)
    def current_date(self):
        return self._current_date

    @Signal
    def api_keyChanged(self):
        pass

    # @Property(str, notify=api_keyChanged)
    def api_key(self):
        return self._api_key

    # @api_key.setter
    @Pre_5_15_2_fix(str, api_key, notify=api_keyChanged)
    def api_key(self, key):
        self._api_key = key
        self.settings.setValue('weather/' + self.name + "/api_key", key)

    # @Property(str)
    def lat(self):
        return self._properties['lat'].value

    # @lat.setter
    @Pre_5_15_2_fix(str, lat, notify=api_keyChanged)
    def lat(self, lat):

        self._properties['lat'].value = lat
        self.settings.setValue('weather/' + self.name + "/lat", lat)

    @Signal
    def intervalChanged(self):
        pass

    @Signal
    def dataChanged(self):
        pass

    # @Property(int, notify=intervalChanged)
    def interval(self):
        return self._properties['module'].interval

    # @interval.setter
    @Pre_5_15_2_fix(int, interval, notify=intervalChanged)
    def interval(self, interval):
        self._properties['module'].interval = int(interval)
        self.settings.setValue('weather/' + self.name + "/interval", interval)

    @Property(float, notify=dataChanged)
    def current_temp(self):
        return float(self._properties['current_temp'].value)

    @Property(float, notify=dataChanged)
    def lastupdate(self):
        return float(self._properties['current_temp'].last_update)

    @Property(str, notify=dataChanged)
    def current_weather_icon(self):
        return self._properties['current_weather_icon'].value

    # @Property(str)
    def lon(self):
        return self._properties['lon'].value

    # @lon.setter
    @Pre_5_15_2_fix(str, lon, notify=api_keyChanged)
    def lon(self, lon):

        self._properties['lon'].value = lon
        self.settings.setValue('weather/' + self.name + "/lon", lon)

    @Signal
    def cityChanged(self):
        pass

    # @Property(str, notify=cityChanged)
    def city(self):
        return self._properties['city'].value

    # @city.setter
    @Pre_5_15_2_fix(str, city, notify=cityChanged)
    def city(self, city: str) -> None:

        self._properties['city'].value = city
        self.settings.setValue('weather/' + self.name + "/city", city)
        self.cityChanged.emit()



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
                     'ü': 7108891, 'ý': 7110541, 'þ': 7110614, 'ā': 7110684,
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
                if line[0].lower() != city[0]:
                    break
                if line.lower().startswith(city):
                    if i > 100:
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

    @Slot(result=bool)
    def hasError(self):
        return self._has_error

    @Slot()
    def start_update(self):
        self.update()
        #threading.Thread(target=self.update).start()



    def update(self):
        status = 'NOT_INITIALIZED'
        try:
            if (self._properties['lon'].value != '') and (self._properties['lat'].value != ''):
                status = 'OK'
                url = Weather.BASE_URL
                params = {'lat': str(self._properties['lat'].value),
                          "lon": str(self._properties['lon'].value),
                          "appid": self._api_key,
                          "exclude": "minutely,hourly",
                          "units": "metric"}

                url += urllib.parse.urlencode(params)



                try:
                    response = urllib.request.urlopen(url, timeout=5)


                except HTTPError as error:
                    status = 'ERROR'
                    self._properties['module'].value = status
                    logging.debug('Data not retrieved because %s\nURL: %s', error, url)
                    return None
                except URLError as error:
                    status = 'ERROR'
                    if isinstance(error.reason, socket.timeout):
                        logging.debug('socket timed out - URL %s', url)
                    else:
                        logging.debug('some other error happened')
                    self._properties['module'].value = status
                    return None

                else:
                    data = response.read().decode('utf-8')
                    self._handle_reply(data)

        except Exception as e:
            status = 'ERROR'
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line: {line_number}')

        return status

    def _handle_reply(self,data):

            d = json.loads(data)
            has_error = False
            self._data = d

            self._properties['sunrise'].value = datetime.datetime.fromtimestamp(int(d["current"]["sunrise"])).strftime(
                '%H:%M:%S')
            self._properties['sunset'].value = datetime.datetime.fromtimestamp(int(d["current"]["sunset"])).strftime(
                '%H:%M:%S')

            self._properties['current_pressure'].value = float(d["current"]["pressure"])
            self._properties['current_humidity'].value = float(d["current"]["humidity"])
            self._properties['current_wind_speed'].value = float(d["current"]["wind_speed"])
            self._properties['current_wind_deg'].value = float(d["current"]["wind_deg"])
            self._properties['current_clouds'].value = float(d["current"]["clouds"])
            self._properties['current_pop'].value = float(d["current"]["pop"]) if 'pop' in d["current"] else 0
            self._properties['current_uvi'].value = float(d["current"]["uvi"])

            if 'rain' in d["current"]:
                if isinstance(d["current"]["rain"], dict) and '1h' in d["current"]["rain"]:
                    self._properties['current_rain'].value = float(str(d["current"]["rain"]['1h']))
                elif isinstance(d["current"]["rain"], float):
                    self._properties['current_rain'].value = float(str(d["current"]["rain"]))

            self._properties['current_temp'].value = float(d["current"]["temp"])
            # self._properties['current_temp']['lastupdate'] = float(d["current"]["dt"])

            self._properties['current_weather_icon'].value = d.get("current", {}).get("weather", [{}])[0].get('icon')
            self._properties['current_weather_desc'].value = d.get("current", {}).get("weather", [{}])[0].get(
                'description')
            self._properties['current_dew_point'].value = float(d["current"]["dew_point"])

            logging.debug(f"{self.current_date}: Weather: added forecast")


            self.dataChanged.emit()

