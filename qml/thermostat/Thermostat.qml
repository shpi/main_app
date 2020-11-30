import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12
//import QtTest 1.15

import "../../fonts/"

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
            font.pointSize: 25
            anchors.right: parent.right
        }
        TabButton {
            height: parent.height / 3
            id: secondButton

            text: Icons.settings
            font.family: localFont.name
            font.pointSize: 25
            anchors.top: firstButton.bottom
            anchors.right: parent.right
        }
        TabButton {
            height: parent.height / 3
            text: Icons.schedule
            font.family: localFont.name
            font.pointSize: 25
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
                property real colortemp: ((value - from) / (to - from))

                background: Rectangle {
                     x:  dialTherm.width / 2 -  width / 2
                     y:  dialTherm.height / 2 - height / 2
                     width: Math.max(64, Math.min( dialTherm.width,  dialTherm.height))
                     height: width
                     color: dialTherm.enabled ? "transparent" : "#eee"
                     radius: width / 2
                     border.color:  dialTherm.enabled ? "black" : "lightgrey"
                     border.width: 2
                     antialiasing: true
                                      }


                handle: Rectangle {

                       id: handleItem
                       x: dialTherm.background.x + dialTherm.background.width / 2 - width / 2
                       y: dialTherm.background.y + dialTherm.background.height / 2 - height / 2
                       width: 20
                       height: 20
                       color: Qt.rgba(parent.colortemp, (1 - 2 * Math.abs(parent.colortemp - 0.5)), 1-parent.colortemp, 1)

                       border.color: dialTherm.enabled ? "black" : "lightgrey"

                       radius: 10
                       antialiasing: true

                       transform: [
                           Translate {
                               y: -Math.min(dialTherm.background.width, dialTherm.background.height) * 0.45 + handleItem.height / 2
                           },
                           Rotation {
                               angle: dialTherm.angle
                               origin.x: handleItem.width / 2
                               origin.y: handleItem.height / 2
                           }
                       ]
                   }

                enabled: false
                from: 15.0
                to: 32.0
                stepSize: 0.2
                snapMode: Dial.SnapAlways
                onPressedChanged: if (pressed == false) {
                                      enabled = false
                                      dialLocker.enabled = true
                                      view.interactive = true
                                  }

                Text {
                visible: !parent.enabled
                anchors.centerIn:parent
                anchors.verticalCenterOffset: 100

                font.pointSize: 9
                color: "green"
                text: "Press and hold to unlock"
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
                                position: 0.7
                                color: "#00ff00"
                            }
                            GradientStop {
                                position: 0.4
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


  /*          TestCase {
                      name: "Dial Unlock"
                      when: dialLocker.pressed
                      id: test1

                      function test_touch() {
                          var touch = touchEvent(area);
                          touch.release();
                          touch.commit();

                      }}
*/
            RoundButton {
            width: height
            id: cooling
            text: Icons.freeze
            font.pointSize: 35
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
            width: height
            font.pointSize: 35
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
            width: height
            font.pointSize: 35
            font.family: localFont.name
            palette.buttonText:  "black"
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
                clip: true
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
