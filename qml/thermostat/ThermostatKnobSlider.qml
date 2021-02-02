import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

import "../../fonts/"

Slider {
    id: control
    orientation: Qt.Vertical
    from: -10
    value: parent.value
    to: 10
    onPressedChanged: {

        if (!pressed) {
            loader.visible = false
            extractSchedule()
            for (var i = 0; i < weekdays.children.length; i++)
                if (typeof weekdays.children[i].active !== "undefined")
                    weekdays.children[i].active = false
        }

        loader.value = value
    }
    onMoved: {
        parent.parent.offset = value
    }

    background: Rectangle {
        id: sliderbg
        radius: 40
        height: parent.height
        width: parent.width

        color: parent.parent.parent.parent.even ? "#aaa" : "#fff"
    }

    handle: Rectangle {
        radius: 40
        width: 80
        height: 80
        border.width: 2
        border.color: Colors.black
        property real colortemp: ((parent.value - parent.from) / (parent.to - parent.from))
        color: Qt.lighter(Qt.rgba(colortemp,
                                  (1 - 2 * Math.abs(colortemp - 0.5)),
                                  1 - colortemp, 1), 1.5)

        y: control.topPadding + control.visualPosition * (control.availableHeight - height)

        Label {
            anchors.centerIn: parent
            text: parent.parent.value > 0 ? '+' + parent.parent.value.toFixed(0) : parent.parent.value.toFixed(0)
            font.pixelSize: 40
            font.bold: true
        }
    }
}
