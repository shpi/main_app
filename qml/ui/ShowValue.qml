import QtQuick 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {

    property string name: modules.modules['UI']['ShowValue'][0]

    height: parent.height
    width: height * 0.7

    radius: 10

    color: "#11000000"

    clip: true

    Text {
        id: icontext
        text: modules.loaded_instances['UI']['ShowValue'][name].icon
        color: Colors.black
        anchors.top: parent.top
        anchors.topMargin: 5
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 90
        font.family: localFont.name
    }

    Text {
        id: valuetext
        text: modules.loaded_instances['UI']['ShowValue'][name].value
        color: Colors.black
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 5
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 50
    }
}
