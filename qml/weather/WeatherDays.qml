import QtQuick 2.0

Item {

    property var days: []


    Text {
        id: weatherdate
        anchors.right: parent.right
        anchors.rightMargin: 10
        text: weather[0].city

}

    Grid {

        columns: 4
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10

        spacing: 10
        id: precast
    }

    Connections {
        id: weatherdaysconn
        target: weather[0]


        onDataChanged: {

            if (!weatherdaysconn.target.hasError()) {


                var component = Qt.createComponent("WeatherDay.qml")

                if (component.status !== Component.Ready) {
                    if (component.status === Component.Error)
                        console.log("Error:" + component.errorString())
                    // or maybe throw
                }

                for (var i = 0; i < weatherdaysconn.target.data['daily'].length; i++) {



                    var weather_icons_arr = []

                    for (var a = 0; a < weatherdaysconn.target.data['daily'][i]['weather'].length; a++) {
                        weather_icons_arr[a] = weatherdaysconn.target.data['daily'][i]['weather'][a]['icon']
                    }

                    if (days[i] !== undefined)
                        days[i].destroy()

                    days[i] = component.createObject(precast, {
                                                         "index": i,
                                                         "weather_icons": weather_icons_arr,
                                                         "average_temp": weatherdaysconn.target.data['daily'][i]['temp']['day'],
                                                         "day": new Date(weatherdaysconn.target.data['daily'][i]['dt'] * 1000)
                                                     })



                    //Wind direction increases clockwise such that a northerly wind is 0°, an easterly wind is 90°, a southerly wind is 180°, and a westerly wind is 270°.
                }
            }
        }
    }
}