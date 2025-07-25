import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15
import QtGraphicalEffects 1.12



import "qrc:/fonts"

Rectangle {

    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['UI']['ShowValue'][0]
    property var instance: modules.loaded_instances['UI']['ShowValue'][instancename]


    height: parent.height
    width: height * 0.7
    radius: 10
    color: Colors.whitetrans
    clip: true

    Shape {
        id: graphShape
        smooth: true
        //layer.enabled: true
        //layer.samples: 4
        width: parent.width
        height: parent.height * 0.7
        anchors.centerIn: parent
        asynchronous: true



        ShapePath {
            scale.height: graphShape.height / 100
            scale.width: graphShape.width / 100
            fillColor: "#77FF4444"
            capStyle: ShapePath.FlatCap
            strokeWidth: 3
            strokeColor: "#77FF4444"
            startX: 0
            startY: 100

            PathLine { x: 0; y: 100 }

            PathPolyline {
                id: ppl
                path: modules.loaded_instances['UI']['ShowValue'][instancename].preview
            }
            PathLine { x: 100; y: 100 }
            PathLine { x: 0; y: 100 }
        }


        }








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

    onClicked:  {
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
