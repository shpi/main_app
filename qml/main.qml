import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.VirtualKeyboard 2.1


import "../fonts/"




ApplicationWindow {
    id: window
    title: qsTr("SHPI")
    width: 800
    height: 480
    visible: true


    FontLoader { id: localFont; source: "../fonts/orkney-custom.ttf"}


    Drawer {
        id: drawer
        width: window.width
        height: window.height / 2
        edge: Qt.TopEdge
        interactive: true
        position: 0
        visible: true

        background: Rectangle {

        color: "transparent"
        }


        Rectangle {
                color: "#000000"
                opacity: 0.7
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 20
                height: row.height + 20
                anchors.top: parent.top
                radius: 20
                anchors.topMargin: 5






        Row {
            id: row
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 10

            spacing: 10

        RoundButton {
            font.family: localFont.name
            font.pointSize: 30
            text: Icons.sun
            width: height

        }

        RoundButton {
            font.family: localFont.name
            font.pointSize: 30
            text: Icons.wifi
            width: height

        }

        RoundButton {
            font.family: localFont.name
            font.pointSize: 30
            text: Icons.speaker
            width: height

        }

        RoundButton {
            font.family: localFont.name
            font.pointSize: 30
            text: Icons.reset
            width: height

        }

        RoundButton {
            font.family: localFont.name
            font.pointSize: 30
            text: Icons.alarmclock
            width: height

        }

        }
        }

        Rectangle {
            width: parent.width - 10

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            color: "black"
            opacity: 0.4
            height: 50
            visible: true
            radius: 20


        RangeSlider {
            id: backlightslider
            from: 1
            height: 100

            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 130
            anchors.verticalCenter: parent.verticalCenter
            anchors.bottom: parent.bottom
            to: 100
            anchors.bottomMargin: 20
            stepSize: 1
            second.value : backlight.brightness
            second.onMoved: backlight.brightness = second.value
            first.onMoved: backlight.set_min_brightness(first.value)

            Label {
            text: "MIN"
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.left
            color: "white"
            }


            Label {
            text: "MAX"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            color: "white"
            }
        }}




     onOpened: {
               backlightslider.first.value = backlight.get_min_brightness()
               }

    }

    SwipeView {
        id: view

        currentIndex: 1
        anchors.fill: parent
        anchors.bottom: inputPanel.top


            Loader {
                id: shutter
                source: "shutter/Shutter.qml"
             }


            Loader {
                id: screensaver
                property bool _isCurrentItem: SwipeView.isCurrentItem
                source: "screensaver/Screensaver.qml"
             }

            Loader {
                id: thermostat
                source: "thermostat/Thermostat.qml"
             }


                Loader {
                id: weatherslide
                source: "weather/Weather.qml"
             }


    }

    PageIndicator {
        id: indicator
        count: view.count
        currentIndex: view.currentIndex
        anchors.bottom: view.bottom
        anchors.horizontalCenter: parent.horizontalCenter
    }



InputPanel {
        id: inputPanel
        y: Qt.inputMethod.visible ? parent.height - inputPanel.height : parent.height
        anchors.left: parent.left
        anchors.right: parent.right
    }


Text {

    anchors.bottom: view.bottom
    anchors.right: view.right
    anchors.rightMargin: 30
    font.family: localFont.name
    font.pointSize: 50
    text: Icons.logo
    color: "white"
    visible: drawer.visible
}



}
