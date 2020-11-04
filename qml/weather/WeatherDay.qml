import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

Rectangle {
    id: dayrect
    property int index
    property string weather_icon
    property int wind_deg
    property int humidity
    property date sunrise
    property date sunset
    property date day
    property string dayname: Qt.formatDate(day, "dddd")
    property real average_temp
    property real max_temp
    property real feel_temp
    property real min_temp
    property real pressure
    property real wind_speed
    property variant weather_icons: []
    property variant weather_descriptions: []
    property int clouds
    property int pop
    property real rain
    property real snow
    property real uvi
    width: 160
    height: 200
    radius: 10
    border.width: 2
    border.color: "black"

    Text {
        text: dayname
        font.pointSize: 10
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Text {
    text: average_temp + "°C"
    anchors.centerIn:parent
    font.pointSize: 15
    }

    Text {
    text: Qt.formatDate(day, "dd.MM.")
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottomMargin: 10
    anchors.bottom:parent.bottom
    font.pointSize: 10
    }

    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10

    Repeater {
     model: dayrect.weather_icons.length

    Image {
    source: "http://openweathermap.org/img/wn/" + weather_icons[index] + "@2x.png"

    }}}



}

/*



{"dt":1603879200,
"sunrise":1603864531,
"sunset":1603899856,
"temp":{"day":10.08,"min":8.84,"max":13.42,"night":10.58,"eve":12.94,"morn":9.32},
"feels_like":{"day":5.87,"night":6.49,"eve":8.73,"morn":3.94},
"pressure":1010,
"humidity":81,
"dew_point":6.97,
"wind_speed":5,
"wind_deg":206,
"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],

"clouds":94,"pop":0.83,"rain":1.63,"uvi":1.25},



  */
