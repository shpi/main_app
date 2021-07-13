import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/fonts"

Item {
    id: root
    property var days: []

    signal message

    function reload() {

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
                                                 "average_temp": weatherdaysconn.target.data['daily'][i]['temp']['day'].toFixed(1),
                                                 "day": new Date(weatherdaysconn.target.data['daily'][i]['dt'] * 1000)
                                             })

            //Wind direction increases clockwise such that a northerly wind is 0°, an easterly wind is 90°, a southerly wind is 180°, and a westerly wind is 270°.
        }
    }

    ComboBox {
        anchors.right: parent.right
        anchors.rightMargin: 10
        id: weatherselect
        anchors.top: parent.top
        anchors.topMargin: 5
        font.pixelSize: 40
        height: 52
        width: 300
        model: modules.modules['Info']['Weather']
        onActivated: weatherselect.model = modules.modules['Info']['Weather']

        onCurrentTextChanged: {
            if (swipeView.instancename !== this.currentText) {
                swipeView.instancename = this.currentText
                reload()
                root.message()
            }
        }
    }

    Text {
        id: weatherdate
        anchors.left: parent.left
        anchors.leftMargin: 10
        text: modules.loaded_instances['Info']['Weather'][swipeView.instancename].city
        color: Colors.black

        visible: false
    }


    Rectangle {

    Flow {

        spacing: 10
        id: precast


        property int rowCount: parent.width / (160 + spacing)
                property int rowWidth: rowCount * 160 + (rowCount - 1) * spacing
                property int mar: (parent.width - rowWidth) / 2

                anchors {
                    fill: parent
                    leftMargin: mar
                    rightMargin: mar
                }

    }

    width: parent.width
    color: "transparent"

    height: parent.height - weatherselect.height - 5
    //columns: 4
    anchors.horizontalCenter:  parent.horizontalCenter
    anchors.verticalCenter:  parent.verticalCenter
    anchors.verticalCenterOffset: weatherselect.height + 5

    }

    Connections {
        id: weatherdaysconn
        target: modules.loaded_instances['Info']['Weather'][swipeView.instancename]

        function onDataChanged() {



            if (!weatherdaysconn.target.hasError()) {
                reload()
            }
        }
    }
}
