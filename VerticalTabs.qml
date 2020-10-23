import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12

import "fonts/"

Item {
    anchors.fill: parent

    TabBar {
        anchors.top: parent.top
        anchors.left: parent.left
        width: parent.width * 0.4
        id: tabBar
        height: parent.height

        currentIndex: swipeView.currentIndex

        TabButton {

            anchors.top: parent.top
            height: parent.height / 3
            id: firstButton
            text: Icons.fire
            font.family: localFont.name
            font.pointSize: 30
            anchors.right: parent.right
        }
        TabButton {
            height: parent.height / 3
            id: secondButton

            text: Icons.settings
            font.family: localFont.name
            font.pointSize: 30
            anchors.top: firstButton.bottom
            anchors.right: parent.right
        }
        TabButton {
            height: parent.height / 3
            text: Icons.clock
            font.family: localFont.name
            font.pointSize: 30
            anchors.top: secondButton.bottom
            anchors.right: parent.right
        }
    }

    SwipeView {
        id: swipeView
        anchors.right: parent.right
        anchors.top: parent.top
        height: parent.height
        width: parent.width - (tabBar.width / 3)
        currentIndex: tabBar.currentIndex
        orientation: Qt.Vertical

        Item {

            Dial {
                id: dialTherm
                width: parent.width * 0.8
                height: parent.height * 0.8
                anchors.centerIn: parent

                enabled: false
                from: 15.0
                to: 32.0
                stepSize: 0.1
                snapMode: Dial.SnapAlways
                onPressedChanged: if (pressed == false) {
                                      enabled = false
                                      dialLocker.enabled = true
                                      view.interactive = true
                                  }

                Text {
                    id: actualSetTemperature
                    text: parent.value.toFixed(1) + "°"
                    anchors.top: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 30
                }

                Text {
                    id: actualTemperature
                    text: parent.value.toFixed(1) + "°"
                    anchors.bottom: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 40
                }

                Shape {
                    id: thermostatrange
                    width: parent.height * 1.2
                    height: parent.height * 1.2
                    anchors.centerIn: parent
                    layer.enabled: true
                    layer.smooth: true
                    layer.samples: 4

                    ShapePath {
                        strokeWidth: 0
                        strokeColor: "transparent"
                        fillGradient: ConicalGradient {

                            centerX: (thermostatrange.width / 2)
                            centerY: (thermostatrange.height / 2)
                            angle: -120
                            GradientStop {
                                position: 1
                                color: "#0000ff"
                            }
                            GradientStop {
                                position: 0
                                color: "#ff0000"
                            }
                        }

                        PathAngleArc {
                            id: outer
                            centerX: (thermostatrange.width / 2)
                            centerY: (thermostatrange.height / 2)
                            radiusX: (thermostatrange.width / 2)
                            radiusY: (thermostatrange.width / 2)
                            startAngle: -230
                            sweepAngle: dialTherm.angle + 140
                        }
                        PathAngleArc {
                            moveToStart: false
                            centerX: outer.centerX
                            centerY: outer.centerY
                            radiusX: (thermostatrange.width / 2) * 0.83
                            radiusY: (thermostatrange.width / 2) * 0.83
                            startAngle: outer.startAngle + outer.sweepAngle
                            sweepAngle: -outer.sweepAngle
                        }
                    }
                }

                InnerShadow {
                    anchors.fill: thermostatrange
                    radius: 8.0
                    samples: 16
                    horizontalOffset: -3
                    verticalOffset: 3
                    color: "#b0000000"
                    source: thermostatrange
                }
            }

            MouseArea {
                id: dialLocker
                anchors.fill: parent
                onDoubleClicked: {
                    dialTherm.enabled = true
                    enabled = false
                    view.interactive = false
                }
                onPressAndHold: {
                    dialTherm.enabled = true
                    enabled = false
                    view.interactive = false
                }
            }


            RoundButton {
            id: cooling
            text: Icons.freeze
            font.pointSize: 60
            font.family: localFont.name
            palette.buttonText:  "blue"
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.bottomMargin: 20
            anchors.leftMargin: 20

            }


            RoundButton {
            id: heating
            text: Icons.fire

            font.pointSize: 60
            font.family: localFont.name
            palette.buttonText:  "orange"
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.bottomMargin: 20
            anchors.rightMargin: 20

            }

            RoundButton {
            id: fan
            text: Icons.fan

            font.pointSize: 60
            font.family: localFont.name
            palette.buttonText:  "blue"
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.topMargin: 20
            anchors.rightMargin: 20

            }


        }

        Item {

            Rectangle {

                anchors.fill: parent
                Loader {

                    anchors.fill: parent

                    source: "ThermostatSettings.qml"
                }

            }
        }

        Item {
            Flickable {
                id: flickable
                anchors.fill: parent
                contentHeight: parent.height * 1.7
                Behavior on contentY { NumberAnimation {} }
                Loader {
                    anchors.fill: parent
                    source: "ThermostatWeek.qml"
                }
            }
        }
    }
}
