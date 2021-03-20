import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

    property string category
    property string classname
    property string instancename

    Component.onCompleted: {

        inputs.set_outputList('boolean')
        inputs.set_typeList('temperature')
    }

    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 10




    Column {

        id: list
        width:parent.width * 0.9
        anchors.horizontalCenter: parent.horizontalCenter


        spacing: 20

        Text {
            text: "Thermostat Settings"
            color: Colors.black
            font.bold: true
            anchors.topMargin: 20
        }


        ComboBox {
            id: combo_temperature1
            anchors.right: parent.right
            width: 550
            model: inputs.typeList
            textRole: 'path'
            onActivated:  modules.loaded_instances['Logic']['Thermostat'][instancename].temp_path = this.currentText

            Component.onCompleted: {

                combo_temperature1.currentIndex = getIndex(modules.loaded_instances['Logic']['Thermostat'][instancename].temp_path, inputs.typeList)
            }

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Room Temp."

                font.family: localFont.name
                color: Colors.black
            }
        }


        ComboBox {
            id: combo_heatingcontact
            anchors.right: parent.right
            width: 550
            model: inputs.outputList
            textRole: 'path'
            onActivated:  modules.loaded_instances['Logic']['Thermostat'][instancename].heating_contact_path = this.currentText

            Component.onCompleted: {

                combo_heatingcontact.currentIndex = getIndex(modules.loaded_instances['Logic']['Thermostat'][instancename].heating_contact_path, inputs.outputList)
            }

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Heating Contact"

                font.family: localFont.name
                color: Colors.black
            }
        }


        Row {
            spacing: 10
            anchors.horizontalCenter: parent.horizontalCenter
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "Temperature hysteresis"
                color: Colors.black
            }

            SpinBox {

                id: tempoffset
                from: -100 * 100
                value: 10
                to: 100 * 100
                stepSize: 10
                font.pixelSize: 32
                property int decimals: 2
                property real realValue: value / 1000

                Component.onCompleted: tempoffset.value = modules.loaded_instances['Logic']['Thermostat'][instancename].hysteresis

                onValueChanged: modules.loaded_instances['Logic']['Thermostat'][instancename].hysteresis
                                = this.value

                validator: DoubleValidator {
                    bottom: Math.min(tempoffset.from, tempoffset.to)
                    top: Math.max(tempoffset.from, tempoffset.to)
                }

                textFromValue: function (value, locale) {
                    return Number(value / 100).toLocaleString(
                                locale, 'f', tempoffset.decimals) + "°"
                }

                valueFromText: function (text, locale) {
                    return Number.fromLocaleString(locale, text) * 1000
                }
            }
        }



        Row {
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter

            RoundButton {

                width: height
                font.family: localFont.name
                text: Icons.schedule
                palette.button: "lightgrey"
                palette.buttonText: Colors.black
                font.pixelSize: 50
                enabled: false
            }

            Frame {
                id: scheduleframe
                property int currentScheduleMode: modules.loaded_instances['Logic']['Thermostat'][instancename].schedule_mode


                Grid {
                    columns: 2
                    spacing: 2
                    RadioButton {
                        id: scheduleMode0
                        checked: scheduleframe.currentScheduleMode == 0
                        onClicked: modules.loaded_instances['Logic']['Thermostat'][instancename].schedule_mode = 0
                        text: qsTr("No schedule")

                            contentItem: Text {
                                text: parent.text
                                color: Colors.black
                                 leftPadding: parent.indicator.width + parent.spacing
                                verticalAlignment: Text.AlignVCenter
                            }
                    }
                    RadioButton {
                        id: scheduleMode1
                        checked: scheduleframe.currentScheduleMode ==  1
                        onClicked: modules.loaded_instances['Logic']['Thermostat'][instancename].schedule_mode = 1
                        text: qsTr("Daily")
                        contentItem: Text {
                            text: parent.text
                            color: Colors.black
                            leftPadding: parent.indicator.width + parent.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    RadioButton {
                        id: scheduleMode2
                        checked: scheduleframe.currentScheduleMode == 2
                        onClicked: modules.loaded_instances['Logic']['Thermostat'][instancename].schedule_mode =  2
                        text: qsTr("Workday / Weekend")
                        contentItem: Text {
                            text: parent.text
                            color: Colors.black
                             leftPadding: parent.indicator.width + parent.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    RadioButton {
                        id: scheduleMode7
                        checked: scheduleframe.currentScheduleMode == 7
                        onClicked: modules.loaded_instances['Logic']['Thermostat'][instancename].schedule_mode =  7
                        text: qsTr("Weekly")
                        contentItem: Text {
                            text: parent.text
                            color: Colors.black
                             leftPadding: parent.indicator.width + parent.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }


        RoundButton {
            text: 'Delete Instance'
            palette.button: "darkred"
            palette.buttonText: "white"
            onClicked: {

                settingsstackView.pop()
                modules.remove_instance('Logic', 'Thermostat', instancename)


            }
        }
    }
}
}
