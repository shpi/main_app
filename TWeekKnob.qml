import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
    property int value: 0
    property string time: (value - minutes) / 60 + ":" + (minutes < 10 ? "0" : "") + minutes
    property int minutes: value % 60
    property int temperature: 25
    property int to: 1440
    property int from: 0
    property int width2: parent.width
    property int cold: 15
    property int warm: 32
    property real colortemp: ((temperature - cold) / (warm - cold))
    color: Qt.rgba(colortemp, 0, 1-colortemp, 1)
    anchors.verticalCenter: parent.verticalCenter
    width: parent.active ? parent.height  / 3 : parent.height / 1.5
    height: parent.active ? parent.height  / 3 : parent.height / 1.5
    opacity: active ? 1 : 0.5
    border.color: "black"
    border.width: 1
    radius: height / 2
    x: value * ((width2 - width) / to)

    Label {
        anchors.centerIn: parent
        text: parent.temperature
        font.pointSize: parent.parent.active ? 20 : 8
    }

    Label {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.bottom
        text: parent.time
        font.pointSize:  10
        visible: parent.parent.active
    }

    Label {

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.bottom
        text: "-"
        visible: (parent.parent.active)
        font.pointSize: 40
        MouseArea {
            enabled: parent.visible
            anchors.fill: parent
            onClicked: { parent.parent.temperature--;
                //var color = ((parent.parent.temperature - parent.parent.cold) / (parent.parent.warm - parent.parent.cold))
               // parent.parent.color = Qt.rgba(color, 0, 1-color, 1)
            }
        }
    }

    Label {

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.top
        text: "+"
        visible: (parent.parent.active)
        font.pointSize: 40
        MouseArea {
            enabled: parent.visible
            anchors.fill: parent
            onClicked: {parent.parent.temperature++;
                        //var color = ((parent.parent.temperature - parent.parent.cold) / (parent.parent.warm - parent.parent.cold))
                        //parent.parent.color = Qt.rgba(color, 0, 1-color, 1)
                        }

        }
    }

    MouseArea {
        anchors.fill: parent
        drag.target: parent
        drag.axis: Drag.XAxis
        drag.minimumX: 0
        drag.maximumX: parent.width2 - parent.width
        onPositionChanged: {
            parent.value = (parent.x )/ (parent.width2 - parent.width) * parent.to
            parent.minutes = parent.value % 60
            parent.time = (parent.value - minutes) / 60 + ":"
                    + (parent.minutes < 10 ? "0" : "") + parent.minutes
        }


    }
}
