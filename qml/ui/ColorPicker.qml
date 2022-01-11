import QtQuick 2.15
import QtGraphicalEffects 1.12 as Effects
import QtQuick.Shapes 1.15 as Shapes
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {


    color: "transparent"

    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['UI']['ColorPicker'][0]
    property var instance: modules.loaded_instances['UI']['ColorPicker'][instancename]
    property real minimal: parent.width > parent.height ? parent.height : parent.width

    function rgbToHsl(r, g, b) {


        r /= 255
        g /= 255
        b /= 255

        var max = Math.max(r, g, b), min = Math.min(r, g, b)
        var h, s, l = (max + min) / 2

        if (max === min) {
            h = s = 0 // achromatic
        } else {
            var d = max - min
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min)

            switch (max) {
            case r:
                h = (g - b) / d + (g < b ? 6 : 0)
                break
            case g:
                h = (b - r) / d + 2
                break
            case b:
                h = (r - g) / d + 4
                break
            }

            // h /= 6;
        }

        rotator.rotation = h * 360
        control.value = l
        //return [ h, s, l ];
    }

    Rectangle {

        border.width: 3
        color: colorpicker.color
        border.color: "white"
        antialiasing: true
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        height: parent.height * 0.8
        width: parent.width * 0.8
        radius: 10

        Text {

        anchors.centerIn: parent
        font.pixelSize:60
        color: Colors.black
        text: Icons.lighton

        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked:  colorpopup.open()
    }

    Connections {
        target: modules.loaded_instances['UI']['ColorPicker'][instancename]
        function onValuesChanged() {

            colorpicker.color.r = instance.red
            colorpicker.color.g = instance.green
            colorpicker.color.b = instance.blue

            rgbToHsl(instance.red, instance.green, instance.blue)
        }
    }

    Popup {

        enter: Transition {

            NumberAnimation {property: "opacity"; from: 0.0; to: 1.0}

        }

        exit: Transition {

            NumberAnimation {property: "opacity"; from: 1.0; to: 0.0}

        }

        height: window.height
        width: window.width
        id: colorpopup

        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        padding: 0
        topInset: 0
        leftInset: 0
        rightInset: 0
        bottomInset: 0

        background: Rectangle {
            color: Colors.white
        }



        RoundButton {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.topMargin: 10
            anchors.leftMargin: 10
            width: height
            text: Icons.close
            palette.button: "darkred"
            palette.buttonText: "white"
            font.pixelSize: 50
            font.family: localFont.name
            onClicked: {
                colorpopup.close()
            }
        }

              Connections {
        target: appearance
        function onJump_stateChanged() {
            if (appearance.jump_state) {
         colorpopup.close()
            }
        }
    }


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

                instance.set((colorpicker.color.r * 100).toFixed(0),
                             (colorpicker.color.g * 100).toFixed(0),
                             (colorpicker.color.b * 100).toFixed(0))
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

                color: Colors.blacktrans

                Text {
                    font.family: localFont.name
                    font.pixelSize: 50
                    color: Colors.black
                    anchors.rightMargin: 15
                    text: Icons.sun
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                }

                Text {
                    font.family: localFont.name
                    font.pixelSize: 50
                    color: Colors.black
                    anchors.leftMargin: 15
                    text: Icons.ssun
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                }

                Rectangle {

                    color: "transparent"
                    clip: true
                    width: control.visualPosition * control.width < control.width
                           - control.radius ? (control.visualPosition * control.width) : (control.visualPosition * control.width) + ((control.visualPosition - 1) / (control.radius / control.width))
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

                visible: false
            }
        }

        Text {
            id: colortext

            text: 'R:' + (colorpicker.color.r * 255).toFixed(
                      0).toString() + ' G:' + (colorpicker.color.g * 255).toFixed(0).toString(
                      ) + ' B:' + (colorpicker.color.b * 255).toFixed(
                      0).toString()
            color: Colors.black
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.horizontalCenterOffset: -80
            font.pixelSize: 50
        }

        Rectangle {

            id: colorpicker
            border.width: 3
            z: 4
            color : Qt.hsla(   (360 + (rotator.rotation % 360)) % 360 / 360,  1, control.value, 1)


            //color: Qt.hsva(rotator.rotation / 360, 1, control.value, 1)
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
            anchors.top: parent.top
            height: parent.height
            width: colorpopup.width / 4
            anchors.right: parent.right



            color: "transparent"

            MouseArea {
                anchors.fill: parent
                preventStealing: true
                property real velocity: 0.0
                property int xPrev: 0
                property int calcrotation: rotator.rotation
                onPressed: {
                    xPrev = mouse.y
                    velocity = 0

                }
                onPositionChanged: {

                    var currVel = (mouse.y - xPrev)

                    velocity = (velocity + currVel) / 2.0
                    var add = (velocity / 10) * (velocity / 10)

                    xPrev = mouse.y
                    if (velocity > 10) {
                            calcrotation -= add
                    } else if (velocity < -10) {
                            calcrotation += add
                    }

                    //colorpicker.color = Qt.hsla(
                    //            (360 + (calcrotation % 360)) % 360 / 360,
                    //            1, control.value, 1)

                    instance.set((colorpicker.color.r * 100).toFixed(0),
                                 (colorpicker.color.g * 100).toFixed(0),
                                 (colorpicker.color.b * 100).toFixed(0))

                    rotator.rotation = calcrotation
                }

            }
        }

        Rectangle {

            id: rotator
            height: window.height + 240
            width: height
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.right
            anchors.horizontalCenterOffset: 110
            color: "#33000000"

            radius: width / 2
            rotation: 90
            Behavior on rotation {
                    PropertyAnimation {}


               
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

                        Rectangle {

                            opacity: 0 + Math.abs(
                                         (((-rotator.rotation + 3330))
                                          - parent.rotation) % 360 - 180) / 40
                            color: "white"
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
}
