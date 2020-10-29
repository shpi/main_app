import QtQuick 2.0
import QtCharts 2.15
import QtQuick.Controls 2.15


Rectangle {
    anchors.fill: parent

    ChartView {
        property date mindate
        property date maxdate
        anchors.fill: parent
        id: chart

        DateTimeAxis {
            id: dateAxis
            format: "ddd"
            tickCount: 8
            min: chart.mindate
            max: chart.maxdate
            labelsAngle: 270
            labelsFont.pointSize: 8
        }

        ValueAxis {
            id: degreeAxis
            min: -20
            max: 40
        }

        ValueAxis {
            id: pressureAxis
            min: 0
            max: 1400
        }

        ValueAxis {
            id: humidityAxis
            min: 0
            max: 100
        }

        AreaSeries {

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
            id: daytemps
            width: 25
            opacity: 0.5
            color: "black"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        LineSeries {
            id: feeltemps
            width: 2
            opacity: 0.5
            color: "lightgrey"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        LineSeries {
            id: mintemps
            width: 5
            color: "blue"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        LineSeries {
            id: maxtemps
            width: 5
            color: "red"
            axisX: dateAxis
            axisY: degreeAxis
            useOpenGL: true
        }

        AreaSeries {
            color: "blue"
            opacity: 0.5
            useOpenGL: true
            axisYRight: ValueAxis {
                min: 0
                max: 5
            }
            axisX: dateAxis
            upperSeries: LineSeries {
                id: dailyrain
                useOpenGL: true
            }
        }
    }

    Connections {
        target: weather

        function onDataChanged() {
            if (!weather.hasError()) {

                for (var i = 0; i < weather.data['daily'].length; i++) {

                    if (daytemps.count > 7) {
                        daytemps.remove(0)
                        mintemps.remove(0)
                        maxtemps.remove(0)
                        feeltemps.remove(0)
                        dailyrain.remove(0)
                        humiditySeries.remove(0)
                    }

                    if (i === 0)
                        chart.mindate = new Date(weather.data['daily'][i]['dt'] * 1000)

                    chart.maxdate = new Date(weather.data['daily'][i]['dt'] * 1000)
                    daytemps.append(
                                new Date(weather.data['daily'][i]['dt'] * 1000),
                                weather.data['daily'][i]['temp']['day'])
                    mintemps.append(
                                new Date(weather.data['daily'][i]['dt'] * 1000),
                                weather.data['daily'][i]['temp']['min'])
                    maxtemps.append(
                                new Date(weather.data['daily'][i]['dt'] * 1000),
                                weather.data['daily'][i]['temp']['max'])
                    feeltemps.append(
                                new Date(weather.data['daily'][i]['dt'] * 1000),
                                weather.data['daily'][i]['feels_like']['day'])
                    humiditySeries.append(
                                new Date(weather.data['daily'][i]['dt'] * 1000),
                                weather.data['daily'][i]['humidity'])

                    if (weather.data['daily'][i]['rain'] !== undefined)
                        dailyrain.append(
                                    new Date(weather.data['daily'][i]['dt'] * 1000),
                                    weather.data['daily'][i]['rain'])
                    else
                        dailyrain.append(
                                    new Date(weather.data['daily'][i]['dt'] * 1000),
                                    0)

                    //Wind direction increases clockwise such that a northerly wind is 0°, an easterly wind is 90°, a southerly wind is 180°, and a westerly wind is 270°.
                }
            }
        }
    }
}
