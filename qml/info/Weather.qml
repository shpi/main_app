import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

import "../../fonts/"

Rectangle {

    property string name: modules.modules['Info']['Weather'][0]
    property string weatherimage: inputs.data['weather/' + name + '/current_weather_icon']['value']
    property string average_temp: inputs.data['weather/' + name + '/current_temp']['value']
    property string day: new Date(inputs.data['weather/' + name + '/lastupdate']['value'] * 1000)
    property string dayname: Qt.formatDate(day, "dddd")

    id: dayrect

    height: parent.height
    width: height * 0.7
    radius: 10

    color: "#11000000"

    Text {
        text: dayname
        font.pixelSize: 32
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        color: Colors.black
    }

    Text {
        text: average_temp
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 5
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 50
        color: Colors.black
    }

    Image {
        anchors.horizontalCenter: parent.horizontalCenter
        source: weatherimage !== ''
                && weatherimage !== undefined ? "http://openweathermap.org/img/wn/"
                                                + weatherimage + "@2x.png" : ""
    }

    Connections {
        id: weatherdaysconn
        target: modules.loaded_instances['Info']['Weather'][name]
        onDataChanged: {

            weatherimage = inputs.data['weather/' + name + '/current_weather_icon']['value']
            average_temp = inputs.data['weather/' + name + '/current_temp']['value']
            day = new Date(inputs.data['weather/' + name + '/lastupdate']['value'] * 1000)
        }
    }

    MouseArea {
        anchors.fill: parent

        onClicked: popupWeather.open()
    }

    Popup {
        id: popupWeather

        height: window.height
        width: window.width

        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        padding: 0
        topInset: 0
        leftInset: 0
        rightInset: 0
        bottomInset: 0

        background: Rectangle {
            color: Colors.white
        }

        Loader {
            anchors.fill: parent
            id: thermostatSchedule
            source: "../weather/WeatherFull.qml"
            asynchronous: true

        }

        RoundButton {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.topMargin: 10
            anchors.leftMargin: 10
            width: height
            text: Icons.close
            palette.button: "darkred"
            palette.buttonText: "white"
            font.pixelSize: 50
            font.family: localFont.name
            onClicked: popupWeather.close()
        }
    }
}
