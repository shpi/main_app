import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

import "../../fonts/"

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
    border.color: Colors.white
    color: Colors.whitetrans

    Text {
        text: dayname
        font.pixelSize: 24
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        color: Colors.black
    }

    Text {
        text: average_temp + "°C"
        anchors.centerIn: parent
        font.pixelSize: 32
        color: Colors.black
    }

    Text {
        text: Qt.formatDate(day, "dd.MM.")
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 15
        anchors.bottom: parent.bottom
        font.pixelSize: 24
        color: Colors.black
    }

    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 5

        Repeater {
            model: dayrect.weather_icons.length

            Image {
                source: "http://openweathermap.org/img/wn/" + weather_icons[index] + "@2x.png"
            }
        }
    }
}
