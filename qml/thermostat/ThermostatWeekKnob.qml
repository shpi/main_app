import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

import "../../fonts/"

Rectangle {
    id: weekdayknob
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
    color: parent.active ? "transparent" : Qt.lighter(Qt.rgba(colortemp, (1 - 2 * Math.abs(colortemp - 0.5)), 1-colortemp, 1),1.5)



    anchors.verticalCenter: parent.verticalCenter
    width: 80
    height: 80
    radius: height / 2
    x: value * ((width2 - width) / to)

    Label {
        anchors.centerIn: parent
        text: parent.temperature
        font.pointSize: parent.parent.active ? 22 : 17
        visible: parent.parent.active ? false : true
    }

    Label {
        id: timeindicator
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter:  parent.horizontalCenter
        anchors.horizontalCenterOffset: (parent.value > (parent.to / 2)) ? -100 : 100

        text: parent.time
        font.pointSize:  14
        visible: false
    }




    MouseArea {
        anchors.centerIn:parent
        width: 120
        height: 120
        drag.target: parent
        drag.axis: Drag.XAxis
        drag.minimumX: 0
        drag.maximumX: parent.width2 - parent.width
        onReleased:
                timeindicator.visible = false
        onClicked: {
            timeindicator.visible = true;
        timeindicator.z = parent.z + 2;
        parent.z = parent.z + 2; }
        onPositionChanged: {
            parent.value = (parent.x )/ (parent.width2 - parent.width) * parent.to
            parent.minutes = parent.value % 60
            parent.time = (parent.value - minutes) / 60 + ":"
                    + (parent.minutes < 10 ? "0" : "") + parent.minutes
            timeindicator.visible = true


        }
        function activateKnobSlider() {

            for (var i = 0; i < weekdays.children.length; i++)
                if (typeof weekdays.children[i].active !== "undefined") {weekdays.children[i].active = false;

                }

             parent.parent.active = true;
             loader.value = parent.temperature;
             loader.visible = true;
             loader.z = parent.z + 1;
             loader.parent = parent;
             loader.anchors.centerIn = parent.center
             flickable.contentY = parent.parent.y - (150)
             parent.parent.parent.parent.opacity = 1

        }

        onPressAndHold:  Qt.callLater(activateKnobSlider)
        onDoubleClicked:  Qt.callLater(activateKnobSlider)
    }




}



