import QtQuick 2.15
import QtQuick.Controls 2.12
import QtQuick.Shapes 1.15

import "../fonts/"

Item {
    property variant graphmap: {'startDate':new Date(),
                         'endDate': new Date(),
                         'polyline': [],
                         'count': 0,
                         'minValue': 0,
                         'maxValue': 100}

    property string sensorpathold: ''
    property bool allowedtimer
    property int xAxiscount: 5
    property int yAxiscount: 5
    property real xAxisDiff
    property real yAxisDiff

    id: graph
    anchors.fill: parent

    function reload(start) {

        allowedtimer = false
        graphmap = inputs.get_calc_points(graphLoader.sensorpath,
                                        graphShape.width, graphShape.height,
                                        graphLoader.divider)

        allowedtimer = true



        yAxisDiff = (graphmap.maxValue - graphmap.minValue) / yAxiscount
        xAxisDiff = (graphmap.endDate - graphmap.startDate) / xAxiscount


    }

    Shape {
        id: graphShape
        smooth: true
        layer.enabled: true
        layer.samples: 4
        width: graph.width
        height: graph.height * 0.85
        anchors.centerIn: parent
        asynchronous: true
        ShapePath {
            //scale.height: -1
            //scale.width
            fillColor: "transparent"
            capStyle: ShapePath.FlatCap
            strokeWidth: 2

            strokeColor: "red"


            PathPolyline {

                id: ppl
                path: graph.graphmap.polyline
            }
        }

        Text {

            anchors.bottom: parent.top
            anchors.topMargin: 10
            anchors.right: parent.right
            text: graph.graphmap.count // + ' Elements '
            color: Colors.black
            font.pixelSize: 20

        }

        Repeater {
            id: xAxis
            anchors.fill: graphShape
            model: xAxiscount

            Rectangle {
                anchors.top: parent.top
                width: 1
                height: parent.height - dateText.height

                color: Colors.black
                x: (index + 0.5) * (graphShape.width / xAxiscount)

                Text {
                    id: dateText
                    text: new Date(graph.graphmap.startDate.getTime() + (xAxisDiff * (index + 0.5))).toLocaleTimeString([], "h:mm:ss")
                    color: Colors.black
                    font.pixelSize: 20
                    anchors.top: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                 }
            }
        }


        Repeater {
            id: yAxis
            anchors.fill: graphShape
            model: yAxiscount

            Rectangle {
                anchors.right: parent.right
                height: 1
                width: parent.width - scaleText.width
                color: Colors.black
                y: (index + 0.5) * (graphShape.height / yAxiscount)

                Text {
                    id: scaleText
                    text: (graph.graphmap.minValue + (yAxisDiff * (index + 0.5))).toFixed(2)
                    color: Colors.black
                    font.pixelSize: 20
                    anchors.right: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }


    }

    Timer {

        interval: graphLoader.interval > 0 ? (graphLoader.interval * 1000) : 100
        repeat: true
        running: graphLoader.sensorpath !== '' && allowedtimer
        onTriggered: { reload(0)  }
    }



}
