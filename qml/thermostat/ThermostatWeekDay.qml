﻿import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    property string dayname
    property bool active: false
    property bool selected: false
    property bool even: false

    //opacity: 0.7
    width: parent.width
    height: active ? 300 : 100
    border.color: selected ? "lightgreen" : "grey"
    border.width: selected ? 5 : 1
    color: even ? Colors.white : "#aaa"
    Behavior on height {
        NumberAnimation {}
    }
    Label {

        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 10
        text: parent.dayname

        color: even ? "#aaa" : Colors.white

        font.pixelSize: parent.active ? 90 : 50
    }

    MouseArea {

        anchors.fill: parent
        onClicked: {
            var component

            for (var i = 0; i < dayrepeater.count; i++) {
                dayrepeater.itemAt(i).selected = false
            }
            parent.selected = true
        }
    }
}
