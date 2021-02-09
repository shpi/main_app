import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12

//import QtTest 1.15
import "../../fonts/"

Rectangle {

    height: parent.height
    width: height
    radius: 10
    color: Colors.whitetrans
    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['Logic']['Thermostat'][0]



    Dial {
        id: dialTherm
        width: parent.height * 0.8
        height: width

        anchors.centerIn: parent
        property real colortemp: ((value - from) / (to - from))

        background: Rectangle {
            anchors.centerIn: parent
            width: dialTherm.width
            height: width
            color: "transparent"
            radius: width / 2
            border.color: Colors.black
            border.width: dialTherm.enabled ? 2 : 1
            //antialiasing: true
        }

        handle: Rectangle {

            id: handleItem
            anchors.centerIn: parent
            width: 10
            height: 10
            color: Qt.rgba(parent.colortemp,
                           (1 - 2 * Math.abs(parent.colortemp - 0.5)),
                           1 - parent.colortemp, 1)
            border.color: dialTherm.enabled ? "black" : "lightgrey"

            radius: 5
            //antialiasing: true

            transform: [
                Translate {
                    y: -Math.min(
                           dialTherm.background.width,
                           dialTherm.background.height) * 0.45 + handleItem.height / 2
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
        value: modules.loaded_instances['Logic']['Thermostat'][instancename].set_temp
        stepSize: 0.2
        snapMode: Dial.SnapAlways
        onPressedChanged: if (pressed == false) {
                              enabled = false
                              dialLocker.enabled = true
                              view.interactive = true
                          }



        Text {
            id: actualSetTemperature
            text: (modules.loaded_instances['Logic']['Thermostat'][instancename].actual_temp + modules.loaded_instances['Logic']['Thermostat'][instancename].offset).toFixed(1) + "°"
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: -5
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 30
            color: Colors.black



        }


        Text{
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenterOffset: 30
            font.pixelSize: 40
            font.family: localFont.name
            text: Icons.fire
            color: modules.loaded_instances['Logic']['Thermostat'][instancename].heating_state > 0 ? "orange" : "grey"


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
                        position: 0.75
                        color: "#00ff00"
                    }
                    GradientStop {
                        position: 0.5
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
    }

   /* MouseArea {
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
    } */

    MouseArea {
        anchors.fill: parent
        onClicked: view.currentIndex = (view.count - 2)
        //onClicked: popupWeather.open()
    }
}
