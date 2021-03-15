import QtQuick 2.15
import QtQuick.Controls 2.12
import QtQuick.Shapes 1.15
import QtGraphicalEffects 1.12

import "qrc:/fonts"

Rectangle {
    id: root
    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['UI']['PieChart'][0]
    property var instance: modules.loaded_instances['UI']['PieChart'][instancename]
    property bool shifted: false
    property real minimal: parent.width > parent.height ? parent.height : parent.width
    property bool iconview: parent.iconview != undefined ? parent.iconview : false

    function degToRad(degrees) {
          return degrees * (Math.PI / 180);
      }

      function radToDeg(radians) {
          return radians * (180 / Math.PI);
      }

    MouseArea {
        id: mouse
    anchors.fill: parent
    onClicked: root.shifted = !root.shifted


    }

    height: minimal
    width: minimal
    radius: 10
    color: Colors.whitetrans
    clip: true

    Repeater {

        model: instance.values

        Shape {
            property real startangle: root.instance.angle(index)
            property real sweepangle: (360 / root.instance.sum) * root.instance.values[index]
            property real centerangle: sweepangle/2 + startangle


            property real shifty:  root.shifted ? Math.sin(degToRad(centerangle)) * 6 : 0
            property real shiftx:  root.shifted ? Math.cos(degToRad(centerangle)) * 6 : 0


            Behavior on shifty {

                PropertyAnimation {}

            }

            Behavior on shiftx {

                PropertyAnimation {}

            }



            id: graphShape2
            layer.enabled: true
            layer.smooth: true
            layer.samples: 4
            width: minimal
            height: minimal
            anchors.centerIn: root
            asynchronous: true
            opacity: 0.7

            ShapePath {
                strokeWidth: 2
                strokeColor: Colors.black
                fillColor: root.instance.colors[index]
                startX: graphShape2.width / 2 + shiftx
                startY: graphShape2.height / 2 + shifty



                PathAngleArc {

                    centerX: graphShape2.width / 2 + shiftx
                    centerY: graphShape2.height / 2 + shifty
                    moveToStart: false
                    radiusX: graphShape2.width / 2.2
                    radiusY: radiusX
                    startAngle: startangle
                    sweepAngle: sweepangle
                }
                PathLine {
                    x: graphShape2.width / 2 + shiftx
                    y: graphShape2.height / 2 + shifty
                }
            }




               /* PathLine {
                    x: graphShape2.width / 2 + Math.cos(degToRad(centerangle)) * 100
                    y: graphShape2.height / 2 + Math.sin(degToRad(centerangle)) * 100
                }*/







            Text {
                color: Colors.black
                x: graphShape2.width / 2 + Math.cos(degToRad(centerangle)) * graphShape2.width / 4 - this.width/2
                y: graphShape2.height / 2 + Math.sin(degToRad(centerangle)) * graphShape2.width / 4
                text: root.instance.names[index]
                font.pixelSize:16
                rotation: centerangle - 90
                visible: root.iconview ? false : true
            }




        }
    }
}
