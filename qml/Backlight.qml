import QtQuick 2.15
import QtQuick.Controls 2.12

Item {

Flickable {

    anchors.fill:parent
    contentHeight: settingscolumn.implicitHeight

Column {
    id: settingscolumn
    anchors.fill:parent
    spacing: 15
    padding: 10


    Text {

    text: "Backlight Range"
    color: "white"
    font.bold: true

    }

    RangeSlider {
        id: backlightslider
        from: 0
        height: 100
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width - 130


        to: 100

        stepSize: 1
        first.value:  appearance.minbacklight
        second.value: appearance.maxbacklight
        second.onMoved: appearance.maxbacklight = second.value
        first.onMoved: appearance.minbacklight = first.value

        Label {
            anchors.horizontalCenter: parent.first.handle.horizontalCenter
            text: parent.first.value
            color: "white"
        }

        Label {
            anchors.horizontalCenter: parent.second.handle.horizontalCenter
            text: parent.second.value
            color: "white"
        }

        Label {
            text: "MIN"
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.left
            color: "white"
        }

        Label {
            text: "MAX"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            color: "white"
        }


    }



    SpinBox {
        value: appearance.dim_timer
        anchors.horizontalCenter: parent.horizontalCenter
        stepSize: 1
        onValueChanged: appearance.dim_timer = this.value
        from: 0
        to: 1000
        Label {
            anchors.left: parent.right
            anchors.leftMargin: 10
            text: "seconds inactivity."
            color: "white"
        }

        Label {
            anchors.right: parent.left
            anchors.rightMargin: 10
            text: "Dim Backlight after"
            color: "white"
        }

    }



    SpinBox {
        value: appearance.off_timer
        anchors.horizontalCenter: parent.horizontalCenter
        stepSize: 1
        onValueChanged: appearance.off_timer = this.value
        from: 0
        to: 1000
        Label {
            anchors.left: parent.right
            anchors.leftMargin: 10
            text: "seconds inactivity."
            color: "white"
        }

        Label {
            anchors.right: parent.left
            anchors.rightMargin: 10
            text: "Turn display off after"
            color: "white"
        }

    }

    SpinBox {
        value: appearance.jump_timer
        anchors.horizontalCenter: parent.horizontalCenter
        stepSize: 1
        onValueChanged: appearance.jump_timer = this.value
        from: 0
        to: 1000
        Label {
            anchors.left: parent.right
            anchors.leftMargin: 10
            text: "seconds inactivity."
            color: "white"
        }

        Label {
            anchors.right: parent.left
            anchors.rightMargin: 10
            text: "Jump to home after"
            color: "white"
        }

    }



    Text {

        text: "Track Input Devices for activity"
        color: "white"
        font.bold: true
        anchors.topMargin: 20

    }

    Repeater {
          model: appearance.devices.list
          CheckBox { checked: appearance.devices[modelData]
                     Text {
                     anchors.left: parent.right
                     anchors.leftMargin: 10
                     color: "white"
                     text: inputs.data[modelData]['description'] }
                     onCheckStateChanged: appearance.setDeviceTrack(modelData, this.checked)

          }
      }

}




}
}
