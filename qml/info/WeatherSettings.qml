import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Flickable {

    id: flickable
    property string category
    property string classname
    property string instancename

    Column {

        anchors.fill: parent
        id: topcol
        spacing: 10
        padding: 10

        Text {

            text: '<b>' + classname + ' > ' + instancename + '</b>'
            color: Colors.black
            font.pixelSize: 32
        }

        Row {
            spacing: 5
            Text {
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "Update Interval in seconds"
            }

            SpinBox {
                value: modules.loaded_instances['Info']['Weather'][instancename].interval
                stepSize: 60
                onValueChanged: modules.loaded_instances['Info']['Weather'][instancename].interval
                                = this.value
                from: 600
                to: 10000
                font.pixelSize: 32
            }
        }

        Row {
            spacing: 5
            Text {
                color: Colors.black
                text: "OWM API Key"
            }

            TextField {
                width:400
                font.pixelSize: 32
                text: modules.loaded_instances['Info']['Weather'][instancename].api_key
                onEditingFinished: modules.loaded_instances['Info']['Weather'][instancename].api_key
                                   = text
            }
        }
        Row {
            spacing: 20

            TextField {
                width: 400
                id: city_tf
                text: modules.loaded_instances['Info']['Weather'][instancename].city
                placeholderText: qsTr("City")
                font.pixelSize: 32
                selectByMouse: true
            }
            Button {
                text: "Search"

                onClicked: {
                    modules.loaded_instances['Info']['Weather'][instancename].update_cities(
                                city_tf.text)
                }
            }
        }

        RoundButton {
            text: 'Delete Instance'
            palette.button: "darkred"
            palette.buttonText: "white"
            onClicked: {

                settingsstackView.pop()
                modules.remove_instance('Info', 'Weather', instancename)

                if (modules.modules['Info']['Weather'].length === 0)
                    weatherrepeater.model = 0
            }
        }

        ListView {
            width: parent.width - 20

            //clip: true
            id: cityview

            model: modules.loaded_instances['Info']['Weather'][instancename].cities

            delegate: contactDelegate

            Component {
                id: contactDelegate

                Rectangle {
                    property int delindex: index
                    id: wrapper
                    height: 100
                    width: cityview.width

                    color: index % 2 === 0 ? "transparent" : Colors.white

                    Column {
                        width: parent.width
                        height: 80
                        spacing: 0
                        Row {
                            spacing: 10
                            height: 70
                            leftPadding: 10

                            RoundButton {
                                radius: height / 2
                                anchors.verticalCenter: parent.verticalCenter
                                visible: wrapper.ListView.isCurrentItem ? true : false
                                text: "\u2713 set"

                                onClicked: {

                                    modules.loaded_instances['Info']['Weather'][instancename].lon
                                            = lon
                                    modules.loaded_instances['Info']['Weather'][instancename].lat
                                            = lat
                                    modules.loaded_instances['Info']['Weather'][instancename].city
                                            = name
                                    modules.loaded_instances['Info']['Weather'][instancename].update()
                                }
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: '<b>' + name + ' ' + stat + '</b>, ' + country

                                font.pixelSize: 32
                                color: Colors.black
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: cityview.currentIndex = wrapper.delindex
                                }
                            }
                        }

                        Text {

                            text: 'Latitude: ' + lat + ', Longitude: ' + lon
                            font.pixelSize: 24
                            color: Colors.black
                        }
                    }
                }
            }
        }

        Connections {
            target: modules.loaded_instances['Info']['Weather'][instancename]
            function onCitiesChanged() {
                cityview.update()
                cityview.height = cityview.count * 100
                flickable.contentHeight = 200 + cityview.count * 100
            }
        }
    }
}
