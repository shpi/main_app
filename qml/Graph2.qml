import QtQuick 2.12
import QtCharts 2.15
import QtQuick.Controls 2.12

import "../fonts/"

Item {

    property string sensorpathold: ''
    property var line

    property bool timerallowed: true
    id: graph
    anchors.fill: parent

     function reload(start) {

        var points;


         if (graph.sensorpathold !== graphLoader.sensorpath) {

             chart.removeAllSeries();
             graph.sensorpathold = graphLoader.sensorpath
             //graphseries.removePoints(0, graphseries.count)
             start = 0
             line = chart.createSeries(ChartView.SeriesTypeLine, graphLoader.sensorpath, dateAxis,valueAxis);
             line.useOpenGL = true
             line.width = 3
             line.color = "red"

         }


            points = inputs.get_points(graphLoader.sensorpath, start, graphLoader.divider)

            if (points.length > 0) {

                timerallowed = false

                line.visible = false


                for (var i = 0; i < points.length; i++) {
                    line.append(points[i].x,points[i].y)
                }

                dateAxis.min = new Date(line.at(0).x)
                dateAxis.max = new Date(line.at(line.count - 1).x)


                line.visible = true
                timerallowed = true

            }



    }

    Timer {

        interval: graphLoader.interval > 0 ? (graphLoader.interval * 1000) : 100
        repeat: true
        running: graphLoader.sensorpath !== '' && timerallowed ? true : false
        onTriggered: {

                     if (line && line.count > 0) {
                        reload(line.at(line.count - 1).x)}
                     else { reload(0) }
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


    }
}
