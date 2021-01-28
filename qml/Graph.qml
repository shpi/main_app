import QtQuick 2.12
import QtCharts 2.3
import QtQuick.Controls 2.12

import "../fonts/"

Item {

    property string sensorpathold: ''
    id: graph
    anchors.fill: parent

     function reload(start) {
        var points;

         if (graph.sensorpathold !== graphLoader.sensorpath) {
             graph.sensorpathold = graphLoader.sensorpath
             graphseries.removePoints(0, graphseries.count)
             start = 0
         }

            points = inputs.get_points(graphLoader.sensorpath, start, graphLoader.divider)

            if (points.length > 0) {
                graphseries.visible = false

                for (var i = 0; i < points.length; i++) {
                    graphseries.append(points[i].x,points[i].y)
                }

                dateAxis.min = new Date(graphseries.at(0).x)
                dateAxis.max = new Date(graphseries.at(graphseries.count - 1).x)
                graphseries.visible = true

            }

    }

    Timer {

        interval: 100
        repeat: true
        running: graphLoader.sensorpath !== '' ? true : false
        onTriggered: {
                     if (graphseries.count > 0) {
                reload(graphseries.at(graphseries.count - 1).x,graphLoader.divider)
            } else {
                reload(0,graphLoader.divider)

             }
        }
    }

    ChartView {
        property double mindate
        property double maxdate
        anchors.fill: parent
        id: chart
        margins.bottom: 0
        margins.top: 0
        margins.left: 0
        margins.right: 0

        legend.labelColor: Colors.black
        legend.borderColor: "transparent"
        legend.font.pixelSize: 24
        legend.markerShape: Legend.MarkerShapeCircle
        legend.color: Colors.black
        plotAreaColor: Colors.whitetrans
        titleColor: Colors.black
        backgroundColor: "transparent"
        antialiasing: true

        DateTimeAxis {
            id: dateAxis
            format: (this.max - this.min) > (86400000) ? "ddd" : "hh:mm"
            tickCount: 8
            labelsAngle: 270
            labelsFont.pixelSize: 24
            color: Colors.grey
            labelsColor: Colors.black
        }

        ValueAxis {
            id: valueAxis
            min: 0
            max: 100
            labelsFont.pixelSize: 24
            color: Colors.grey
            labelsColor: Colors.black
        }

        LineSeries {
            name: graphLoader.sensorpath
            id: graphseries
            width: 3
            color: "red"
            axisX: dateAxis
            axisY: valueAxis
            useOpenGL: graphLoader.sensorpath !== ''

        }
    }
}
