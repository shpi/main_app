import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    anchors.fill: parent
Column {
    anchors.fill: parent

    Row {
        spacing: 20

        TextField {
            id: city_tf
            placeholderText: qsTr("City")
            font.pointSize: 14
            selectByMouse: true
        }
        Button {
            text: "Search"

            onClicked: {
                weather.update_cities(city_tf.text)
            }
        }

        Button {
            text: "Update"

            onClicked: {
                weather.update()
            }
        }
    }
    ScrollView {
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        height: 400

        ScrollBar.vertical.policy: ScrollBar.AlwaysOn

        ListView {

            clip: true
            orientation: Qt.Vertical
            flickableDirection: Flickable.VerticalFlick
            boundsBehavior: Flickable.StopAtBounds
            id: cityview
            width: parent.width
            model: weather.cities
            
            delegate: contactDelegate
            focus: true

            Component {
                id: contactDelegate

                Rectangle {
                    property int delindex: index
                    id: wrapper
                    height: 60
                    width: cityview.width
                    color: index % 2 === 0 ? "lightgrey" : "white"
                    Row {
                        spacing: 10
                        height: parent.height

                        RoundButton {
                            radius: height / 2
                            anchors.verticalCenter: parent.verticalCenter
                            visible: wrapper.ListView.isCurrentItem ? true : false
                            text: "\u2713 set"

                            onClicked: {

                                weather.set_lon(lon)
                                weather.set_lat(lat)
                                weather.city = name
                                weather.update()
                            }
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: '<b>' + name + ' ' + stat + '</b>, ' + country
                            font.pointSize: 12
                            MouseArea {
                                anchors.fill: parent
                                onClicked: cityview.currentIndex = wrapper.delindex
                            }
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: 'Latitude: ' + lat + ', Longitude: ' + lon
                            font.pointSize: 8
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: weather
        onCitiesChanged: {
            cityview.update()
        }
    }
}
}
