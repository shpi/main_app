import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Flickable {

    id: flickable
    property string category
    property string classname
    property string instancename
    contentHeight: weathercolumn.implicitHeight + cityview.height + 100



    Text {
        id: header
        padding: 10
        anchors.left:parent.left
        text: '<b>Weather > ' + instancename + '</b>'
        color: Colors.black
        font.bold: true
    }

    Column {
        anchors.top: header.bottom
        id: weathercolumn
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20



        SpinBox {
            value: modules.loaded_instances['Info']['Weather'][instancename].interval
            stepSize: 60
            onValueChanged: modules.loaded_instances['Info']['Weather'][instancename].interval
                            = this.value
            from: 600
            to: 10000
            font.pixelSize: 32
            anchors.right: parent.right

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "Update Interval in seconds"
            }
        }

        TextField {
            anchors.right: parent.right
            onActiveFocusChanged: keyboard(this)
            width: 400
            font.pixelSize: 32
            text: modules.loaded_instances['Info']['Weather'][instancename].api_key
            onEditingFinished: modules.loaded_instances['Info']['Weather'][instancename].api_key
                               = text

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "OWM Key"
            }
        }

        TextField {
            anchors.right: parent.right
            onActiveFocusChanged: keyboard(this)
            width: 400
            id: city_tf
            text: modules.loaded_instances['Info']['Weather'][instancename].city
            placeholderText: qsTr("City")
            font.pixelSize: 32

            RoundButton {
                anchors.right: parent.left
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                text: "Search"

                onClicked: {
                    modules.loaded_instances['Info']['Weather'][instancename].update_cities(
                                city_tf.text)
                }
            }
        }
    }
        ListView {

            id: cityview

            anchors.top: weathercolumn.bottom
            anchors.topMargin: 20

            model: modules.loaded_instances['Info']['Weather'][instancename].cities

            delegate: contactDelegate

            width: flickable.width

            onCountChanged: cityview.height = cityview.count * 100

            clip: true

            Component {
                id: contactDelegate

                Rectangle {
                    property int delindex: index
                    id: wrapper
                    height: 100


                    color: index % 2 === 0 ? "transparent" : Colors.white

                    Column {

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
                                font.pixelSize: 40

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

        RoundButton {
            anchors.top: cityview.bottom
            anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            text: 'Delete Instance'
            palette.button: "darkred"
            palette.buttonText: "white"
            font.pixelSize: 40
            onClicked: {

                settingsstackView.pop()
                modules.remove_instance('Info', 'Weather', instancename)

                if (modules.modules['Info']['Weather'].length === 0)
                    weatherrepeater.model = 0
            }
        }

        Connections {
            target: modules.loaded_instances['Info']['Weather'][instancename]
            function onCitiesChanged() {
                cityview.update()

            }
        }
    }

