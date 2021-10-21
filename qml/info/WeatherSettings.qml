import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

    property string category
    property string classname
    property string instancename


Flickable {

    id: flickable
    anchors.fill: parent
    contentHeight: weathercolumn.implicitHeight + cityview.height + 200


    Text {
        id: title
        anchors.left: parent.left
        text: 'Weather > ' + instancename
        color: Colors.black
        font.bold: true
        font.pixelSize: 32
        height: 70
        padding: 10
    }



    Column {
        anchors.top: title.bottom
        id: weathercolumn
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20
        padding: 10
        width:parent.width * 0.9


        Flow {
            width: parent.width
            height: implicitHeight

            Text {
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: "Update Interval"
                font.pixelSize: 24
                color: Colors.black
                wrapMode: Text.WordWrap
                width: parent.width < 500 ? parent.width : parent.width * 0.3
                height: 50
            }

            SpinBox {
                value: modules.loaded_instances['Info']['Weather'][instancename].interval
                stepSize: 60
                width: parent.width < 500 ? parent.width : parent.width * 0.7
                onValueChanged: modules.loaded_instances['Info']['Weather'][instancename].interval
                                = this.value
                from: 600
                to: 10000
                font.pixelSize: 32
                textFromValue: function (value, locale) {
                    return Number(value) + "s"
                }

                valueFromText: function (text, locale) {
                    return Number.fromLocaleString(locale, text)
                }
            }
        }

        Flow {
            width: parent.width
            height: implicitHeight

            Text {
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: "OWM API Key"
                font.pixelSize: 24
                color: Colors.black
                wrapMode: Text.WordWrap
                width: parent.width < 500 ? parent.width : parent.width * 0.3
                height: 50
            }
            TextField {
                onActiveFocusChanged: keyboard(this)
                width: parent.width < 500 ? parent.width : parent.width * 0.7
                height: 50
                font.pixelSize: 32
                text: modules.loaded_instances['Info']['Weather'][instancename].api_key
                onEditingFinished: modules.loaded_instances['Info']['Weather'][instancename].api_key
                                   = text
            }
        }

        Flow {
            width: parent.width
            height: implicitHeight

            TextField {

                onActiveFocusChanged: keyboard(this)
                width: parent.width < 500 ? parent.width : parent.width * 0.7
                height: 50
                id: city_tf
                text: modules.loaded_instances['Info']['Weather'][instancename].city
                placeholderText: qsTr("City")
                font.pixelSize: 32
            }
            RoundButton {
                width: parent.width < 500 ? parent.width : parent.width * 0.3
                height: 50
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

                        //leftPadding: 10
                        RadioButton {
                            //radius: height / 2
                            anchors.verticalCenter: parent.verticalCenter
                            visible: wrapper.ListView.isCurrentItem ? true : false
                            text: "\u2713 set"
                            font.pixelSize: 40

                            onClicked: {

                                modules.loaded_instances['Info']['Weather'][instancename].lon = lon
                                modules.loaded_instances['Info']['Weather'][instancename].lat = lat
                                modules.loaded_instances['Info']['Weather'][instancename].city
                                        = name
                                modules.loaded_instances['Info']['Weather'][instancename].start_update()
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
        font.pixelSize: 32
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
}
