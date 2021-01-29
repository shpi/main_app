import QtQuick 2.15
import QtQuick.Controls 2.12
import QtQuick.Shapes 1.15

import "../fonts/"

Item {

    property string sensorpathold: ''
    property var points
    property var startx_x
    property var lastx_x

    id: graph
    anchors.fill: parent

     function reload(start) {



            points = inputs.get_calc_points(graphLoader.sensorpath, 800, 400, graphLoader.divider)


    }

     Shape {
         width: 800
         height: 400
         anchors.centerIn: parent
         ShapePath {
             //scale.width
             fillColor: "transparent"
             strokeWidth: 2
             strokeColor: "red"
             startX: 0; startY: 0

             PathPolyline {

                 id: ppl
                 path: points
             }

         }
     }


     Timer {

         interval: graphLoader.interval > 0 ? (graphLoader.interval * 1000) : 100
         repeat: true
         running: graphLoader.sensorpath !== ''  ? true : false
         onTriggered: {

                       reload(0)
         }
     }


}
