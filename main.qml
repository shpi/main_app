import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Controls.Material 2.12

import "fonts/"


ApplicationWindow {
    id: window
    title: qsTr("SHPI")
    width: 800
    height: 480
    visible: true


    FontLoader { id: localFont; source: "./fonts/opensans.ttf"}


    Drawer {
        id: drawer
        width: window.width
        height: window.height / 2
        edge: Qt.TopEdge
        interactive: true
        position: 1
        visible: true
        opacity: 0.8
        background: Rectangle {
                color: "#000000"
        }




        Text {
            font.family: localFont.name
            font.pointSize: 40
            text: Icons.sun
            color: "#FFFFFF"

        }

        RangeSlider {
            id: backlightslider
            from: 1
            to: 100
            stepSize: 1
            second.onMoved: backlight.set_max_brightness(second.value)
            first.onMoved: backlight.set_min_brightness(first.value)

        }


     Text {
     text: "ᵕ"
     width: parent.width

     horizontalAlignment: Text.AlignHCenter
     anchors.top: drawer.Bottom

     font.pointSize: 40
     color: "#FFFFFF"
     }

     onOpened: {backlightslider.second.value = backlight.get_brightness()
               backlightslider.first.value = backlight.get_min_brightness()
               }

    }

    SwipeView {
        id: view

        currentIndex: 1
        anchors.fill: parent

            Loader {
                id: thermostat
                source: "Thermostat.qml"
             }


            Loader {
                id: screensaver
                source: "Screensaver.qml"
             }


        Item {
            id: thirdPage
        }
    }

    PageIndicator {
        id: indicator
        count: view.count
        currentIndex: view.currentIndex
        anchors.bottom: view.bottom
        anchors.horizontalCenter: parent.horizontalCenter
    }



}
