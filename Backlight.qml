import QtQuick 2.0

Item {

Text {

text: "Backlight Settings"

}

    RangeSlider {
        id: backlightslider
        from: 1
        height: 100

        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width - 130
        anchors.verticalCenter: parent.verticalCenter
        anchors.bottom: parent.bottom
        to: 100
        anchors.bottomMargin: 20
        stepSize: 1
        second.value: backlight.brightness
        second.onMoved: backlight.brightness = second.value
        first.onMoved: backlight.set_min_brightness(first.value)

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


}
