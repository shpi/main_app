import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15

import "qrc:/fonts"

Item {
    id: root
    anchors.fill: parent
    property int xAxiscount: 7
    property int yAxiscount: 7
    property real xAxisDiff
    property real yAxisDiff
    property date mindate: new Date(0)
    property date maxdate: new Date(0)
    property real minValue: -10
    property real maxValue: 25
    property var daytempspath: []
    property var mintempspath: []
    property var maxtempspath: []
     property var rainpath: []
    property var weekday: ["Sun", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat"]
    property real scaleY: chart.height / (Math.abs(
                                              root.minValue - root.maxValue))

    function reload() {

        root.maxValue = -20
        root.minValue = 200

        for (var i = 0; i < weatherconn.target.data['daily'].length; i++) {

            if (daytempspath.length > 7) {

                daytempspath = []
                mintempspath = []
                maxtempspath = []
                rainpath = [] //splice(0, 1)
            }



            if (i === 0)
                root.mindate = new Date(weatherconn.target.data['daily'][i]['dt'] * 1000)

            root.maxdate = new Date(weatherconn.target.data['daily'][i]['dt'] * 1000)

            if (weatherconn.target.data['daily'][i]['temp']['max'] > root.maxValue)
                root.maxValue = weatherconn.target.data['daily'][i]['temp']['max']

            if (weatherconn.target.data['daily'][i]['temp']['min'] < root.minValue)
                root.minValue = weatherconn.target.data['daily'][i]['temp']['min']
        }

        root.minValue = root.minValue - 3
        root.maxValue = root.maxValue + 3

        root.scaleY = chart.height / (Math.abs(root.minValue - root.maxValue))

        for (i = 0; i < weatherconn.target.data['daily'].length; i++) {

            if (0 === i)

            rainpath.push(
                        Qt.point(
                        new Date(weatherconn.target.data['daily'][i]['dt'] - (root.mindate / 1000)),
                        chart.height))

            daytempspath.push(
                        Qt.point(
                            new Date(weatherconn.target.data['daily'][i]['dt']
                                     - (root.mindate / 1000)),
                            chart.height - (weatherconn.target.data['daily'][i]['temp']['day']
                                            - root.minValue) * root.scaleY))

            mintempspath.push(
                        Qt.point(
                            new Date(weatherconn.target.data['daily'][i]['dt']
                                     - (root.mindate / 1000)),
                            chart.height - (weatherconn.target.data['daily'][i]['temp']['min']
                                            - root.minValue) * root.scaleY))

            maxtempspath.push(
                        Qt.point(
                            new Date(weatherconn.target.data['daily'][i]['dt']
                                     - (root.mindate / 1000)),
                            chart.height - (weatherconn.target.data['daily'][i]['temp']['max']
                                            - root.minValue) * root.scaleY))

            if (weatherconn.target.data['daily'][i]['rain'] !== undefined)
                rainpath.push(
                            Qt.point(
                            new Date(weatherconn.target.data['daily'][i]['dt'] - (root.mindate / 1000)),
                            chart.height - (weatherconn.target.data['daily'][i]['rain'] * 20)))
            else
                rainpath.push(
                            Qt.point(
                            new Date(weatherconn.target.data['daily'][i]['dt'] - (root.mindate / 1000)),
                            chart.height))


            if (weatherconn.target.data['daily'].length -1 === i)

            rainpath.push(
                        Qt.point(
                        new Date(weatherconn.target.data['daily'][i]['dt'] - (root.mindate / 1000)),
                        chart.height))



            /*

            humiditySeries.append(
                        new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                        weatherconn.target.data['daily'][i]['humidity'])


*/
            //Wind direction increases clockwise such that a northerly wind is 0°, an easterly wind is 90°, a southerly wind is 180°, and a westerly wind is 270°.
        }


        yAxisDiff = (root.maxValue - root.minValue) / yAxiscount
        xAxisDiff = (root.maxdate - root.mindate) / xAxiscount

        daytempsshape.scale.width = chart.width / ((root.maxdate - root.mindate) / 1000)
        mintempsshape.scale.width = daytempsshape.scale.width
        maxtempsshape.scale.width = daytempsshape.scale.width
        rainshape.scale.width = daytempsshape.scale.width
        daytemps.path = daytempspath
        mintemps.path = mintempspath
        maxtemps.path = maxtempspath
        rainline.path = rainpath
    }

    Shape {

        id: chart
        smooth: true
        width: root.width * 0.75
        height: root.height * 0.75
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: -parent.height / 18
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: 20
        asynchronous: true

        ShapePath {
            id: rainshape
            startX: 0
            startY: chart.height
            fillColor: "#880000FF"
            capStyle: ShapePath.FlatCap
            strokeWidth: 1
            strokeColor: "darkblue"

            PathPolyline {
                id: rainline
                path: rainpath
            }
        }


        ShapePath {
            id: daytempsshape
            startX: 0
            startY: 0
            fillColor: "transparent"
            capStyle: ShapePath.FlatCap
            strokeWidth: 5
            strokeColor: Colors.black

            PathPolyline {
                id: daytemps
                path: daytempspath
            }
        }

        ShapePath {
            id: mintempsshape
            startX: 0
            startY: 0
            fillColor: "transparent"
            capStyle: ShapePath.FlatCap
            strokeWidth: 3
            strokeColor: "lightblue"

            PathPolyline {
                id: mintemps
                path: mintempspath
            }
        }

        ShapePath {
            id: maxtempsshape
            startX: 0
            startY: 0
            fillColor: "transparent"
            capStyle: ShapePath.FlatCap
            strokeWidth: 3
            strokeColor: "red"

            PathPolyline {
                id: maxtemps
                path: maxtempspath
            }
        }

        Repeater {
            id: xAxis
            anchors.fill: chart
            model: xAxiscount

            Rectangle {
                anchors.top: parent.top
                width: 1
                height: parent.height - dateText.height

                color: Colors.black
                x: (index + 0.5) * (chart.width / xAxiscount)

                Text {
                    id: dateText
                    rotation: 270
                    text: root.weekday[new Date(root.mindate.getTime(
                                                    ) + (xAxisDiff * (index + 0.5))).getDay(
                                           )]
                    color: Colors.black
                    font.pixelSize: 20
                    anchors.top: parent.bottom
                    anchors.topMargin: 30
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }

        Repeater {
            id: yAxis
            anchors.fill: chart
            model: yAxiscount

            Rectangle {
                anchors.right: parent.right
                height: 1
                width: parent.width
                color: Colors.black
                y: ((yAxiscount - index) - 0.5) * (chart.height / yAxiscount)

                Text {
                    id: scaleText
                    text: (root.minValue + (yAxisDiff * (index + 0.5))).toFixed(
                              1) + "°"
                    color: Colors.black
                    font.pixelSize: 20
                    anchors.rightMargin: 15
                    anchors.right: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }
    }

    Connections {
        id: weatherconn
        target: modules.loaded_instances['Info']['Weather'][swipeView.instancename]
        function onDataChanged() {
            if (!weatherconn.target.hasError())
                reload()
        }
    }
}
