import QtQuick 2.12
import QtCharts 2.3
import QtQuick.Controls 2.12

import "../../fonts/"

Item {
    id: weathergraph
    anchors.fill: parent

    function reload() {

        for (var i = 0; i < weatherconn.target.data['daily'].length; i++) {

            if (daytemps.count > 7) {
                daytemps.remove(0)
                mintemps.remove(0)
                maxtemps.remove(0)
                feeltemps.remove(0)
                dailyrain.remove(0)
                humiditySeries.remove(0)
            }

            if (i === 0)
                chart.mindate = new Date(weatherconn.target.data['daily'][i]['dt'] * 1000)

            chart.maxdate = new Date(weatherconn.target.data['daily'][i]['dt'] * 1000)
            daytemps.append(
                        new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                        weatherconn.target.data['daily'][i]['temp']['day'])
            mintemps.append(
                        new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                        weatherconn.target.data['daily'][i]['temp']['min'])
            maxtemps.append(
                        new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                        weatherconn.target.data['daily'][i]['temp']['max'])
            feeltemps.append(
                        new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                        weatherconn.target.data['daily'][i]['feels_like']['day'])
            humiditySeries.append(
                        new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                        weatherconn.target.data['daily'][i]['humidity'])

            if (weatherconn.target.data['daily'][i]['rain'] !== undefined)
                dailyrain.append(
                            new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                            weatherconn.target.data['daily'][i]['rain'])
            else
                dailyrain.append(
                            new Date(weatherconn.target.data['daily'][i]['dt'] * 1000),
                            0)

            //Wind direction increases clockwise such that a northerly wind is 0°, an easterly wind is 90°, a southerly wind is 180°, and a westerly wind is 270°.
        }
    }

    ChartView {
        property date mindate
        property date maxdate
        anchors.fill: parent
        id: chart
        margins.bottom: 0
        margins.top: 0
        margins.left: 0
        margins.right: 0

        //theme: appearance.night ? ChartView.ChartThemeDark : ChartView.ChartThemeLight
        legend.labelColor: Colors.black
        legend.borderColor: "transparent"
        legend.font.pixelSize: 24
        legend.markerShape: Legend.MarkerShapeCircle
        legend.color: Colors.black
        plotAreaColor: Colors.whitetrans
        titleColor: Colors.black
        backgroundColor: "transparent"

        DateTimeAxis {
            id: dateAxis
            format: "ddd"
            tickCount: 8
            min: chart.mindate
            max: chart.maxdate
            labelsAngle: 270
            labelsFont.pixelSize: 24
            color: Colors.black
            labelsColor: Colors.black
        }

        ValueAxis {
            id: degreeAxis
            min: -20
            max: 40
            labelsFont.pixelSize: 24
            color: Colors.black
            labelsColor: Colors.black
        }

        ValueAxis {
            id: pressureAxis
            min: 0
            max: 1400
            labelsFont.pixelSize: 24
            color: Colors.black
            labelsColor: Colors.black
        }

        ValueAxis {
            id: humidityAxis
            min: 0
            max: 100
            labelsFont.pixelSize: 24
            color: Colors.black
            labelsColor: Colors.black
        }

        AreaSeries {
            name: "Humidity"
            color: "blue"
            opacity: 0.3
            axisY: humidityAxis
            axisX: dateAxis
            useOpenGL: true
            upperSeries: LineSeries {
                id: humiditySeries
                useOpenGL: true
            }
        }

        LineSeries {
            name: "Avg. Temp"
            id: daytemps
            width: 25
            opacity: 0.5
            color: "black"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        LineSeries {
            name: "Feel Temp"
            id: feeltemps
            width: 2
            opacity: 0.5
            color: "lightgrey"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        LineSeries {
            name: "Min. Temp"
            id: mintemps
            width: 5
            color: "blue"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        LineSeries {
            name: "Max. Temp"
            id: maxtemps
            width: 5
            color: "red"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        AreaSeries {
            name: "Rain"
            color: "blue"
            opacity: 0.5
            useOpenGL: true
            axisYRight: ValueAxis {
                min: 0
                max: 5
                labelsFont.pixelSize: 24
                labelsColor: Colors.black
            }
            axisX: dateAxis
            upperSeries: LineSeries {
                id: dailyrain
                useOpenGL: true
            }
        }
    }

    Connections {
        id: weatherconn
        target: modules.loaded_instances['Info']['Weather'][swipeView.instancename]
        onDataChanged: {
            if (!weatherconn.target.hasError())
                reload()
        }
    }
}
