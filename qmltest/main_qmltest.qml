import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

ApplicationWindow {
    id: window
    title: "SHPI"
    width: 800
    height: 480
    visible: true

    Text {
        text: "Hello World"
        anchors.centerIn: parent
    }

    RangeSlider {
        id: backlightslider
        from: 0
        to: 100
        height: 100
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width - 130

        stepSize: 1
        // snapMode: RangeSlider.SnapAlways
        first.value: appearance.minbacklight
        second.value: appearance.maxbacklight
        second.onMoved: appearance.maxbacklight = Math.round(second.value)
        first.onMoved: appearance.minbacklight = Math.round(first.value)

        background: Rectangle {
            x: backlightslider.leftPadding
            y: backlightslider.topPadding + backlightslider.availableHeight / 2 - height / 2
            implicitWidth: 200
            implicitHeight: 8
            width: backlightslider.availableWidth
            height: implicitHeight
            radius: 2
            color: "#bdbebf"

            Rectangle {
                x: backlightslider.first.visualPosition * parent.width
                width: backlightslider.second.visualPosition * parent.width - x
                height: parent.height
                color: "#21be2b"
                radius: 2
            }
        }

        Label {
            anchors.horizontalCenter: parent.first.handle.horizontalCenter
            text: appearance.minbacklight
            color: Colors.black
        }

        Label {
            anchors.horizontalCenter: parent.second.handle.horizontalCenter
            text: appearance.maxbacklight
            color: Colors.black
        }

        Label {
            text: "MIN"
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.left
            color: Colors.black
        }

        Label {
            text: "MAX"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            color: Colors.black
        }
    }
}
