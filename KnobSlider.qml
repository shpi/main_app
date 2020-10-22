import QtQuick 2.12
import QtQuick.Controls 2.12



    Slider {
        id: control
        anchors.fill: parent
        orientation: Qt.Vertical
        from: 15
        value: parent.value
        to: 35
        onPressedChanged: {

           if (!pressed) loader.visible = false
                           loader.value = value

        }
        onMoved: {parent.parent.temperature = value}
        background: Rectangle {

        radius: 25
        height: parent.height
        width: parent.width
        color: parent.parent.parent.parent.even ? "#aaa" : "#fff"

        }
        handle: Rectangle {
            radius: 25
            width: 80
            height: 80
            border.width: 2
            border.color: "black"
            property real colortemp: ((parent.value - parent.from) / (parent.to - parent.from))
            color: Qt.rgba(colortemp, 0, 1-colortemp, 1)

            y: control.topPadding + control.visualPosition * (control.availableHeight - height)

            Label {
                anchors.centerIn: parent
                text: parent.parent.value.toFixed(0)
                font.pointSize:  22
            }

        }

    }


