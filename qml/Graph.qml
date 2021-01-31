import QtQuick 2.15
import QtQuick.Controls 2.12
import QtQuick.Shapes 1.15

import "../fonts/"

Item {

    property string sensorpathold: ''
    property var points
    property bool allowedtimer
    property int xAxiscount: 5
    property real xAxisDiff
    property date startDate
    property date endDate
    property int pointsCount: 0

    id: graph
    anchors.fill: parent

    function reload(start) {

        allowedtimer = false
        points = inputs.get_calc_points(graphLoader.sensorpath,
                                        graphShape.width, graphShape.height,
                                        graphLoader.divider)
        ppl.path = points['points']
        pointsCount = points['count']
        allowedtimer = true

        startDate = points['start']
        endDate = points['end']
        xAxisDiff = (endDate - startDate) / xAxiscount
    }

    Shape {
        id: graphShape
        width: graph.width
        height: graph.height * 0.8
        anchors.centerIn: parent
        asynchronous: true
        ShapePath {
            //scale.width
            fillColor: "transparent"
            strokeWidth: 1
            strokeColor: "red"
            startX: 0
            startY: 0

            PathPolyline {
                id: ppl
            }
        }

        Text {

            anchors.bottom: parent.top
            anchors.topMargin: 10
            anchors.right: parent.right
            text: pointsCount.toString() + ' Elements'
            color: Colors.black
            font.pixelSize: 20

        }

        Repeater {
            anchors.fill: parent
            model: xAxiscount

            Rectangle {
                anchors.top: parent.top
                width: 1
                height: parent.height
                color: Colors.black
                x: (index + 0.5) * (graphShape.width / xAxiscount)

                Text {

                    text: new Date(startDate.getTime(
                                       ) + (xAxisDiff * (index + 0.5))).toLocaleTimeString(
                              Qt.locale("de_DE"), "h:mm:ss")
                    color: Colors.black
                    font.pixelSize: 20
                    anchors.top: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }
    }

    Timer {

        interval: graphLoader.interval > 0 ? (graphLoader.interval * 1000) : 100
        repeat: true
        running: graphLoader.sensorpath !== '' && allowedtimer ? true : false
        onTriggered: {

            reload(0)
        }
    }
}
