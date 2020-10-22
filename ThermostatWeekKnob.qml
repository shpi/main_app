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
    width: 80
    height: 80

    border.color: "black"
    border.width: 1
    radius: height / 2
    x: value * ((width2 - width) / to)

    Label {
        anchors.centerIn: parent
        text: parent.temperature
        font.pointSize: parent.parent.active ? 22 : 17
    }

    Label {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.bottom
        text: parent.time
        font.pointSize:  10
        visible: parent.parent.active
    }




    MouseArea {
        anchors.centerIn:parent
        width: 120
        height: 120
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


        onPressAndHold:  {
                         for (var i = 0; i < weekdays.children.length; i++)
                             if (typeof weekdays.children[i].active !== "undefined") weekdays.children[i].active = false

                          parent.parent.active = true;
                          loader.value = parent.temperature;
                          loader.visible = true;
                          loader.z = parent.z + 1;
                          loader.parent = parent;
                          loader.anchors.centerIn = parent.center
                          flickable.contentY = parent.parent.y - (150)

                        }

    }
}
