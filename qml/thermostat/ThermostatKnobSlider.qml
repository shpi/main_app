import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12



    Slider {
        id: control
        orientation: Qt.Vertical
        from: 15
        value: parent.value
        to: 32
        onPressedChanged: {

           if (!pressed) {
               loader.visible = false
               for (var i = 0; i < weekdays.children.length; i++)
                   if (typeof weekdays.children[i].active !== "undefined") weekdays.children[i].active = false

           }

           loader.value = value

        }
        onMoved: {parent.parent.temperature = value}

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

            property real colortemp: ((parent.value - parent.from) / (parent.to - parent.from))
            color: Qt.lighter(Qt.rgba(colortemp, (1 - 2 * Math.abs(colortemp - 0.5)), 1-colortemp, 1), 1.5)


            y: control.topPadding + control.visualPosition * (control.availableHeight - height)

            Label {
                anchors.centerIn: parent
                text: parent.parent.value.toFixed(0)
                font.pointSize:  22
                font.bold: true

            }



        }

    }

