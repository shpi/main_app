import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {

    Component.onCompleted: {

        inputs.set_outputList('boolean')
    }
    anchors.fill: parent

    color: Colors.white

    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 10

        // Operationsmodus, Ausgänge,  Autmatisch hochfahren uhrzeit, Autmatisch runterfahren uhrzeit
        Column {
            width: parent.width * 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            id: list
            spacing: 20

            Text {

                text: "Working Mode"
                color: Colors.black
                font.bold: true
                anchors.topMargin: 20
            }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                RadioButton {
                    checked: shutter2.mode === 'boolean' ? true : false
                    onReleased: if (this.checked)
                                    shutter2.mode = 'boolean'
                    text: qsTr("boolean")
                    contentItem: Text {
                        text: parent.text
                        color: Colors.black
                        leftPadding: parent.indicator.width + parent.spacing
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                RadioButton {
                    checked: shutter2.mode === 'percent' ? true : false
                    onReleased: if (this.checked)
                                    shutter2.mode = 'percent'

                    text: qsTr("percent")
                    contentItem: Text {
                        text: parent.text
                        color: Colors.black
                        leftPadding: parent.indicator.width + parent.spacing
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }

            Text {
                text: "Controlled Outputs"
                color: Colors.black
                font.bold: true
                anchors.topMargin: 20
            }

            ComboBox {
                id: combo_boolean_up
                anchors.right: parent.right
                width: 550
                model: inputs.outputList
                textRole: 'path'
                onActivated: shutter2.relay_up = this.currentText

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: Icons.arrow
                    rotation: 180
                    font.family: localFont.name
                    color: Colors.black
                }
            }

            ComboBox {
                id: combo_boolean_down
                anchors.right: parent.right
                width: 550
                model: inputs.outputList
                textRole: 'path'
                onActivated: shutter2.relay_down = this.currentText

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: Icons.arrow
                    font.family: localFont.name
                    color: Colors.black
                }
            }

            SpinBox {

                id: up_time
                from: 0
                value: 100
                to: 300 * 100
                stepSize: 10
                font.pixelSize: 32
                property int decimals: 2
                property real realValue: value / 100
                anchors.right: parent.right

                validator: DoubleValidator {
                    bottom: Math.min(up_time.from, up_time.to)
                    top: Math.max(up_time.from, up_time.to)
                }

                textFromValue: function (value, locale) {
                    return Number(value / 100).toLocaleString(
                                locale, 'f', up_time.decimals) + "s"
                }

                valueFromText: function (text, locale) {
                    return Number.fromLocaleString(locale, text) * 100
                }

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "UP running time"
                    color: Colors.black
                }
            }

            SpinBox {

                id: down_time
                from: 0
                value: 100
                to: 300 * 100
                stepSize: 10
                font.pixelSize: 32
                property int decimals: 2
                property real realValue: value / 100
                anchors.right: parent.right

                validator: DoubleValidator {
                    bottom: Math.min(down_time.from, down_time.to)
                    top: Math.max(down_time.from, down_time.to)
                }

                textFromValue: function (value, locale) {
                    return Number(value / 100).toLocaleString(
                                locale, 'f', down_time.decimals) + "s"
                }

                valueFromText: function (text, locale) {
                    return Number.fromLocaleString(locale, text) * 100
                }

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "DOWN running time"
                    color: Colors.black
                }
            }

            Text {
                text: "Calibration"
                color: Colors.black
                font.bold: true
                anchors.topMargin: 20
            }

            Row {
                spacing: 20
                anchors.horizontalCenter: parent.horizontalCenter

                Button {
                    property bool running: false
                    id: control
                    text: (control.running === false) ? qsTr(
                                                            "Move down") : qsTr(
                                                            "stop")
                    onClicked: {
                        control.running = !control.running
                        if (control.running) {
                            controlup.running = !control.running

                            time.startTime = new Date().getTime()
                            timer.running = true
                        } else {
                            timer.running = false
                            shutter2.actual_position = 0
                            //time.text = ((new Date().getTime() - time.startTime) / 1000).toFixed(1) + "s"
                        }
                    }
                    font.pixelSize: 50

                    contentItem: Text {
                        text: control.text
                        font: control.font

                        color: control.running ? "red" : "black"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }

                    background: Rectangle {
                        implicitWidth: 200
                        implicitHeight: 60
                        opacity: enabled ? 1 : 0.3
                        border.color: control.running ? "red" : "darkgrey"
                        border.width: 1
                        radius: 5
                        gradient: Gradient {
                            GradientStop {
                                position: 0
                                color: control.pressed ? "#ccc" : "#eee"
                            }
                            GradientStop {
                                position: 1
                                color: control.pressed ? "#aaa" : "#ccc"
                            }
                        }
                    }
                }

                Button {
                    property bool running: false
                    id: controlup
                    text: (controlup.running === false) ? qsTr(
                                                              "Move up") : qsTr(
                                                              "stop")
                    onClicked: {
                        controlup.running = !controlup.running
                        if (controlup.running) {
                            control.running = !controlup.running
                            time.startTime = new Date().getTime()
                            timer.running = true
                        } else {
                            timer.running = false
                            shutter2.actual_position = 100
                            //time.text = ((new Date().getTime() - time.startTime) / 1000).toFixed(1) + "s"
                        }
                    }
                    font.pixelSize: 50

                    contentItem: Text {
                        text: controlup.text
                        font: controlup.font

                        color: controlup.running ? "red" : "black"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }

                    background: Rectangle {
                        implicitWidth: 200
                        implicitHeight: 60
                        opacity: enabled ? 1 : 0.3
                        border.color: controlup.running ? "red" : "darkgrey"
                        border.width: 1
                        radius: 5
                        gradient: Gradient {
                            GradientStop {
                                position: 0
                                color: controlup.pressed ? "#ccc" : "#eee"
                            }
                            GradientStop {
                                position: 1
                                color: controlup.pressed ? "#aaa" : "#ccc"
                            }
                        }
                    }
                }
            }

            Text {
                id: time
                font.pixelSize: 30
                color: Colors.black
                text: time.startTime != 0 ? new Date().getTime(
                                                ) - time.startTime + " ms" : 0
                anchors.horizontalCenter: parent.horizontalCenter
                property double startTime: 0
            }

            Timer {
                id: timer
                interval: 200
                running: false
                repeat: true
                onTriggered: time.text = ((new Date().getTime(
                                               ) - time.startTime) / 1000).toFixed(
                                 1) + "s"
            }
        }
    }
}