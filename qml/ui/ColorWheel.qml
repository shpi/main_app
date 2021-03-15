import Qt.labs.folderlistmodel 2.12
import QtQuick 2.12
import QtGraphicalEffects 1.12 as Effects
import QtQuick.Shapes 1.12 as Shapes
import QtQuick.Controls 2.12

import "qrc:/fonts"


Rectangle {

    property int i: 0
    clip: true

    property real max_temp: 32
    property real min_temp: 16

    property real factor: (max_temp - min_temp) / 240

    id: tickswindow
    height: parent.height
    width: height
    anchors.horizontalCenter: parent.horizontalCenter

    color: "transparent"

    Slider {
        id: control

        property real radius: 32
        from: 0
        to: 1
        value: 0.5
        onMoved: {
            colorpicker.color = Qt.hsla(
                        (360 + (rotator.rotation % 360)) % 360 / 360, 1,
                        control.value, 1)
        }
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        width: 500
        height: radius * 2
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: -100
        background: Rectangle {
            x: control.leftPadding
            y: control.topPadding + control.availableHeight / 2 - height / 2

            width: control.width + control.radius
            height: control.height
            radius: control.radius
            color: "#33ffffff"

            Text {
                font.family: localFont.name
                font.pixelSize: 50
                color: "white"
                anchors.rightMargin: 15
                text: Icons.sun
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
            }

            Text {
                font.family: localFont.name
                font.pixelSize: 50
                color: "white"
                anchors.leftMargin: 15
                text: Icons.ssun
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
            }

            Rectangle {

                color: "transparent"
                clip: true
                width: control.visualPosition * control.width < control.width
                       - control.radius ? (control.visualPosition
                                           * control.width) : (control.visualPosition
                                                               * control.width)
                                          + ((control.visualPosition - 1)
                                             / (control.radius / control.width))
                                          * control.radius + control.radius

                height: control.height
                Rectangle {

                    anchors.left: parent.left
                    anchors.top: parent.top
                    width: parent.width < control.radius
                           * 2 ? control.radius * 3 : (control.visualPosition
                                                       * control.width) + control.radius
                    height: parent.height
                    color: "#aaffffff"
                    radius: control.radius
                }
            }
        }

        handle: Rectangle {

            /*
               x: control.leftPadding + control.visualPosition * (control.availableWidth - width/2)
               y: control.topPadding + control.availableHeight / 2 - height / 2
               width: control.radius * 2
               height: control.height
               color:"transparent"
               border.color:"white"
               border.width: 1
               radius: control.radius */
            visible: false
        }
    }

    Rectangle {

        width: 550
        height: 80
        color: "#88000000"
        radius: 40
        anchors.left: parent.left
        anchors.leftMargin: -40
        anchors.top: parent.top
        anchors.topMargin: 20

        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 20
            font.pixelSize: 50
            color: "white"
            text: "Living Room"
        }
    }

    Text {
        id: temptext
        property real temperatur: 20

        //text: temperatur.toFixed(1) + '°C'
        //text: (32 - ( (rotator.rotation / 15))).toFixed(1) + "°C"
        text: 'R:' + (colorpicker.color.r * 255).toFixed(
                  0).toString() + ' G:' + (colorpicker.color.g * 255).toFixed(0).toString(
                  ) + ' B:' + (colorpicker.color.b * 255).toFixed(0).toString()
        color: "white"
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: -80
        font.pixelSize: 50
    }

    Rectangle {

        id: colorpicker
        border.width: 3
        z: 4
        color: Qt.hsva(rotator.rotation / 360, 1, 1, 1)
        border.color: "white"

        antialiasing: true
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: 240
        height: 30
        width: 100
        radius: 10
    }

    Rectangle {
        anchors.top: tickswindow.top
        height: tickswindow.height
        width: tickswindow.width / 5
        anchors.right: tickswindow.right
        //border.width: 1
        //border.color: "white"
        //opacity: 0.5
        color: "transparent"

        MouseArea {
            anchors.fill: parent
            preventStealing: true
            property real velocity: 0.0
            property int xStart: 0
            property int xPrev: 0
            property bool tracing: false
            onPressed: {
                xStart = mouse.y
                xPrev = mouse.y
                velocity = 0
                tracing = true
            }
            onPositionChanged: {
                if (!tracing)
                    return
                var currVel = (mouse.y - xPrev)

                velocity = (velocity + currVel) / 2.0
                var add = (velocity / 10) * (velocity / 10)

                xPrev = mouse.y
                if (velocity > 10) {
                    if (rotator.rotation - add < 0)
                        rotator.rotation = rotator.rotation - add
                    else
                        rotator.rotation -= add
                } else if (velocity < -10) {
                    if (rotator.rotation + add > 360)
                        rotator.rotation = rotator.rotation + add
                    else
                        rotator.rotation += add
                }

                colorpicker.color = Qt.hsla(
                            (360 + (rotator.rotation % 360)) % 360 / 360, 1,
                            control.value, 1)
            }
            onReleased: {
                tracing = false
            }
        }
    }

    Rectangle {

        id: rotator
        height: tickswindow.height + 240
        width: height
        anchors.verticalCenter: tickswindow.verticalCenter
        anchors.horizontalCenter: tickswindow.right
        anchors.horizontalCenterOffset: 110
        color: "#33000000"

        radius: width / 2
        rotation: 90
        Behavior on rotation {
            PropertyAnimation {

                onRunningChanged: colorpicker.color = Qt.hsla(
                                      (360 + (rotator.rotation % 360)) % 360 / 360,
                                      1, control.value, 1)
            }
        }

        Item {
            id: ticks
            anchors.fill: parent

            Repeater {

                model: 120

                Rectangle {
                    anchors.centerIn: parent
                    width: 5
                    height: parent.height - 40
                    color: "transparent"
                    rotation: index * 3 - 27

                    //border.width: 1
                    //border.color: "white"
                    Rectangle {

                        opacity: 0 + Math.abs(
                                     (((-rotator.rotation + 3330))
                                      - parent.rotation) % 360 - 180) / 40
                        color: "white"
                        //color: Qt.rgba(((index-20)/80), (1 - 2 * Math.abs(((index-20)/80) - 0.5)), 1-((index-20)/80), 1)
                        width: 5
                        height: 40
                        anchors.left: parent.left
                        antialiasing: true
                    }
                }
            }
        }

        Shapes.Shape {
            id: colorwheel
            width: parent.height
            height: parent.height
            anchors.centerIn: parent
            anchors.fill: parent
            layer.enabled: true
            layer.smooth: true
            layer.samples: 4

            Shapes.ShapePath {

                strokeWidth: 0
                strokeColor: "transparent"

                fillGradient: Shapes.ConicalGradient {

                    centerX: (colorwheel.width / 2)
                    centerY: (colorwheel.height / 2)

                    angle: 180
                    GradientStop {
                        position: 0.000
                        color: Qt.rgba(1, 0, 0, 1)
                    }
                    GradientStop {
                        position: 0.167
                        color: Qt.rgba(1, 1, 0, 1)
                    }
                    GradientStop {
                        position: 0.333
                        color: Qt.rgba(0, 1, 0, 1)
                    }
                    GradientStop {
                        position: 0.500
                        color: Qt.rgba(0, 1, 1, 1)
                    }
                    GradientStop {
                        position: 0.667
                        color: Qt.rgba(0, 0, 1, 1)
                    }
                    GradientStop {
                        position: 0.833
                        color: Qt.rgba(1, 0, 1, 1)
                    }
                    GradientStop {
                        position: 1.000
                        color: Qt.rgba(1, 0, 0, 1)
                    }
                }

                PathAngleArc {
                    id: outer
                    centerX: (colorwheel.width / 2)
                    centerY: (colorwheel.height / 2)
                    radiusX: (colorwheel.width / 2.5)
                    radiusY: (colorwheel.width / 2.5)
                    startAngle: 0
                    sweepAngle: 360
                }
                PathAngleArc {
                    moveToStart: false
                    centerX: outer.centerX
                    centerY: outer.centerY
                    radiusX: (colorwheel.width / 3)
                    radiusY: (colorwheel.width / 3)
                    startAngle: 0
                    sweepAngle: -360
                }
            }
        }
    }
}
