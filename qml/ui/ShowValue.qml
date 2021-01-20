import QtQuick 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {

    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['UI']['ShowValue'][0]

    height: parent.height
    width: height * 0.7
    radius: 10
    color: Colors.whitetrans
    clip: true

    Text {
        id: icontext
        text: modules.loaded_instances['UI']['ShowValue'][instancename].icon
        color: Colors.black
        anchors.top: parent.top
        anchors.topMargin: 5
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 90
        font.family: localFont.name
    }

    Text {
        id: valuetext
        text: modules.loaded_instances['UI']['ShowValue'][instancename].value
        color: Colors.black
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 5
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 40
    }


    MouseArea {
    anchors.fill: parent
    enabled: modules.loaded_instances['UI']['ShowValue'][instancename].logging
    onClicked: {
    graphLoader.sensorpath = modules.loaded_instances['UI']['ShowValue'][instancename].value_path
    graphLoader.divider = modules.loaded_instances['UI']['ShowValue'][instancename].divider
    graphPopup.open()
    }

    }


}
