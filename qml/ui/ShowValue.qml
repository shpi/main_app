import QtQuick 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {

    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['UI']['ShowValue'][0]
    property var instance: modules.loaded_instances['UI']['ShowValue'][instancename]



    height: parent.height
    width: height * 0.7
    radius: 10
    color: Colors.whitetrans
    clip: true

    Text {
        id: icontext
        text: instance.icon
        color: Colors.black
        anchors.top: parent.top
        anchors.topMargin: 3
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 90
        font.family: localFont.name
    }

    Text {
        id: valuetext
        text: instance.value
        color: Colors.black
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 3
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 40
    }


    MouseArea {
    anchors.fill: parent
    enabled: instance.logging
    onClicked: {
    graphLoader.sensorpath = instance.value_path
    graphLoader.divider = instance.divider
    graphLoader.interval = instance.interval

        if (graphLoader.sensorpath !== graphLoader.item.sensorpathold)
        {
        graphLoader.item.reload(0)

        }

    graphPopup.open()
    }

    }


}
