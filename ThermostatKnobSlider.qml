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
        color: "transparent"
        border.width: 1
        border.color: parent.parent.parent.parent.even ? "#aaa" : "#fff"


        }

        DropShadow {
              anchors.fill: sliderbg
              horizontalOffset: 3
              verticalOffset: 3
              radius: 8.0
              samples: 10
              color: "#000000"
              source: sliderbg
          }

        handle: Rectangle {
            radius: 40
            width: 80
            height: 80
            border.width: 1
            border.color: "black"
            property real colortemp: ((parent.value - parent.from) / (parent.to - parent.from))
            color: Qt.rgba(colortemp+0.3, (1 - 2 * Math.abs(colortemp - 0.5)), 1.3-colortemp, 1)


            y: control.topPadding + control.visualPosition * (control.availableHeight - height)

            Label {
                anchors.centerIn: parent
                text: parent.parent.value.toFixed(0)
                font.pointSize:  22
                font.bold: true

            }



        }

    }


