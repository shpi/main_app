import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {
    anchors.fill: parent

    Column {
        id:topcol
        anchors.top: parent.top
        spacing: 10
        padding: 10


        Row {
            spacing: 5
            Text {
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "Update Interval in seconds"
            }



            SpinBox {
                value: weather[0].interval

                stepSize: 60
                onValueChanged: weather[0].interval =  this.value
                from: 60
                to: 1000
                font.pointSize: 14

            }



        }

        Row {
            spacing: 5
            Text {
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "OpenWeather API Key"
            }

            TextField {

                font.pointSize: 14
                text: weather[0].api_key

                onEditingFinished: weather[0].api_key = text
            }
        }
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
                    weather[0].update_cities(city_tf.text)
                }
            }

            Button {
                text: "Update"

                onClicked: {
                    weather[0].update()
                }
            }
        }}
        ScrollView {
            anchors.top: topcol.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            height: 300
            ScrollBar.vertical.policy: ScrollBar.AlwaysOn

            ListView {

                clip: true
                orientation: Qt.Vertical
                flickableDirection: Flickable.VerticalFlick
                boundsBehavior: Flickable.StopAtBounds
                id: cityview
                width: parent.width
                model: weather[0].cities

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
                            leftPadding:10

                            RoundButton {
                                radius: height / 2
                                anchors.verticalCenter: parent.verticalCenter
                                visible: wrapper.ListView.isCurrentItem ? true : false
                                text: "\u2713 set"

                                onClicked: {

                                    weather[0].lon = lon
                                    weather[0].lat = lat
                                    weather[0].city = name
                                    weather[0].update()
                                }
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: '<b>' + name + ' ' + stat + '</b>, ' + country
                                font.pointSize: 12
                                color: Colors.black
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: cityview.currentIndex = wrapper.delindex
                                }
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: 'Latitude: ' + lat + ', Longitude: ' + lon
                                font.pointSize: 8
                                color: Colors.black
                            }
                        }
                    }
                }
            }


        Connections {
            target: weather[0]
            onCitiesChanged: {
                cityview.update()
            }
        }
    }
}
