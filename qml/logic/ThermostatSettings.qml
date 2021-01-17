import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

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


        spacing: 10


        Row {
            spacing: 10
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "Temperature offset"
                color: Colors.black
            }

            SpinBox {

                id: tempoffset
                from: -100 * 100
                value: 10
                to: 100 * 100
                stepSize: 10
                font.pixelSize: 50
                property int decimals: 2
                property real realValue: value / 100

                validator: DoubleValidator {
                    bottom: Math.min(tempoffset.from, tempoffset.to)
                    top: Math.max(tempoffset.from, tempoffset.to)
                }

                textFromValue: function (value, locale) {
                    return Number(value / 100).toLocaleString(
                                locale, 'f', tempoffset.decimals) + "°"
                }

                valueFromText: function (text, locale) {
                    return Number.fromLocaleString(locale, text) * 100
                }
            }
        }

        Row {
            spacing: 10
            Text {
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "Temperature hysteresis"
            }
            SpinBox {

                id: hysterese
                from: 0
                value: 10
                to: 100 * 100
                stepSize: 10

                font.pixelSize: 50
                property int decimals: 2
                property real realValue: value / 100

                validator: DoubleValidator {
                    bottom: Math.min(hysterese.from, hysterese.to)
                    top: Math.max(hysterese.from, hysterese.to)
                }

                textFromValue: function (value, locale) {
                    return Number(value / 100).toLocaleString(
                                locale, 'f', hysterese.decimals) + "°"
                }

                valueFromText: function (text, locale) {
                    return Number.fromLocaleString(locale, text) * 100
                }
            }
        }

        Row {
            spacing: 20

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

                Grid {
                    columns: 2
                    spacing: 2
                    RadioButton {
                        checked: true
                        text: qsTr("No schedule")

                            contentItem: Text {
                                text: parent.text
                                color: Colors.black
                                 leftPadding: parent.indicator.width + parent.spacing
                                verticalAlignment: Text.AlignVCenter
                            }
                    }
                    RadioButton {
                        text: qsTr("Daily")
                        contentItem: Text {
                            text: parent.text
                            color: Colors.black
                            leftPadding: parent.indicator.width + parent.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    RadioButton {
                        text: qsTr("Weekday / Weekend")
                        contentItem: Text {
                            text: parent.text
                            color: Colors.black
                             leftPadding: parent.indicator.width + parent.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    RadioButton {
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
    }
}
}
