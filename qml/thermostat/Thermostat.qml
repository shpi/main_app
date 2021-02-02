import QtQuick 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {

    property string instancename: modules.modules['Logic']['Thermostat'][0]
    property real max_temp: 32
    property real min_temp: 16

    id: tickswindow
    height: parent.height
    width: height
    anchors.horizontalCenter: parent.horizontalCenter
    clip: true
    color: "transparent"

    Component.onCompleted: rotator.rotation = (Math.abs((modules.loaded_instances['Logic']['Thermostat'][tickswindow.instancename].set_temp /
                                                         ((max_temp - min_temp) / 240) -480) ) )


    ComboBox {
        anchors.left: parent.left
        anchors.leftMargin: 10
        id: thermostatselect
        anchors.top: parent.top
        anchors.topMargin: 5
        font.pixelSize: 40
        height: 52
        width: 300
        model: modules.modules['Logic']['Thermostat']
        onActivated: thermostatselect.model = modules.modules['Logic']['Thermostat']

        onCurrentTextChanged: {
            if (tickswindow.instancename !== this.currentText) {
                tickswindow.instancename = this.currentText
                rotator.rotation = (Math.abs((modules.loaded_instances['Logic']['Thermostat'][tickswindow.instancename].set_temp /
                                              ((max_temp - min_temp) / 240) -480) ) )



            }
        }
    }

    Slider {
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: 150
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: -100
        id: control
        property real radius: 25
        from: 0 // 0 off, 1 away, 2 eco , 3 normal, 4 party
        to: 4
        stepSize: 1
        value: 3
        snapMode: Slider.SnapAlways

        width: 500
        height: radius * 2
        background: Rectangle {

            width: control.width
            height: control.height
            radius: control.radius
            color: "transparent"

            Row {

                spacing: 12
                anchors.fill: parent

                Rectangle {
                    width: control.width / 5 - 10
                    height: control.height
                    clip: true
                    color: "transparent"

                    Rectangle {
                        anchors.left: parent.left
                        width: control.value == 0 ? control.width / 5 - 10 : control.width
                                                    / 5 - 10 + control.radius
                        height: control.height
                        radius: control.radius
                        anchors.verticalCenter: parent.verticalCenter
                        opacity: control.value == 0 ? 1 : 0.2
                        gradient: RadialGradient {
                            GradientStop {
                                position: 0.0
                                color: "#ddd"
                            }
                            GradientStop {
                                position: 0.5
                                color: "#444"
                            }
                        }
                    }
                }

                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: control.width / 5 - 10
                    height: control.height
                    radius: control.value == 1 ? control.radius : 0
                    opacity: control.value == 1 ? 1 : 0.2
                    gradient: RadialGradient {
                        GradientStop {
                            position: 0.0
                            color: "#ddd"
                        }
                        GradientStop {
                            position: 0.5
                            color: "blue"
                        }
                    }
                }

                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: control.width / 5 - 10
                    height: control.height
                    radius: control.value == 2 ? control.radius : 0
                    opacity: control.value == 2 ? 1 : 0.2
                    gradient: RadialGradient {
                        GradientStop {
                            position: 0.0
                            color: "#ddd"
                        }
                        GradientStop {
                            position: 0.5
                            color: "darkgreen"
                        }
                    }
                }

                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: control.width / 5 - 10
                    height: control.height
                    radius: control.value == 3 ? control.radius : 0
                    opacity: control.value == 3 ? 1 : 0.2
                    gradient: RadialGradient {
                        GradientStop {
                            position: 0.0
                            color: "#ddd"
                        }
                        GradientStop {
                            position: 0.5
                            color: "darkorange"
                        }
                    }
                }

                Rectangle {
                    width: control.width / 5 - 10
                    height: control.height
                    clip: true
                    color: "transparent"

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.right: parent.right
                        width: control.value == 4 ? control.width / 5 - 10 : control.width
                                                    / 5 - 10 + control.radius
                        height: control.height
                        radius: control.radius
                        opacity: control.value == 4 ? 1 : 0.2
                        gradient: RadialGradient {
                            GradientStop {
                                position: 0.0
                                color: "#ddd"
                            }
                            GradientStop {
                                position: 0.5
                                color: "red"
                            }
                        }
                    }
                }
            }
        }

        handle: Rectangle {
            x: control.leftPadding + 23 + control.visualPosition * (control.availableWidth * 0.84)
            y: control.topPadding + control.availableHeight / 2 - height / 2
            width: 30
            height: 30
            color: "transparent"
            //border.width: 5
            //border.color: "white"
            opacity: 1
            radius: width / 2

            Text {
                id: thermostatmodus
                text: control.value == 0 ? 'Off' : control.value == 1 ? 'Away' : control.value == 2 ? 'Eco' : control.value == 3 ? 'Auto' : control.value == 4 ? 'Party' : 'Unknown'
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                font.pixelSize: 32
                color: Colors.black
            }
        }
    }

    Text {
        id: temptext
        property real temperatur: 20

        //text: temperatur.toFixed(1) + '°C'
        //text: (32 - ( (rotator.rotation / 15))).toFixed(1) + "°C"
        text: modules.loaded_instances['Logic']['Thermostat'][tickswindow.instancename].set_temp.toFixed(1)  + '°C'
        // (min_temp + (-rotator.rotation + 240) * ((max_temp - min_temp) / 240)).toFixed(1) + '°C'


        color: Colors.black
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: tickswindow.width * 0.10
    }

    RoundButton
    {

        visible: modules.loaded_instances['Logic']['Thermostat'][tickswindow.instancename].schedule_mode > 0
        anchors.right: temptext.left
        anchors.rightMargin: 30
        anchors.verticalCenter: temptext.verticalCenter
        width: height
        font.family: localFont.name
        text: Icons.schedule
        palette.button: Colors.grey
        palette.buttonText: Colors.black
        font.pixelSize: 90
        onClicked: thermostatPopup.open()
    }

    Rectangle {
        anchors.top: tickswindow.top
        height: tickswindow.height
        width: tickswindow.width / 4
        anchors.right: tickswindow.right
        //border.width: 1
        //border.color: "white"
        //opacity: 0.5
        color: "transparent"

        MouseArea {

            property int velocity;
            anchors.fill: parent
            preventStealing: true
            //property int velocity: 0.0
            property int calcrotation: rotator.rotation //needed because animation
            property int xPrev: 0

            onPressed: {

                xPrev = mouse.y
                velocity = 0

            }
            onPositionChanged: {

                velocity = (velocity + mouse.y - xPrev) / 2

                if (Math.abs(velocity) > 20) {
                xPrev = mouse.y

                calcrotation -= (velocity / 12)

                if (calcrotation   > 240)    calcrotation = 240
                else if  (calcrotation   < 0)    calcrotation = 0

                let step = ((max_temp - min_temp) / 240)

                let settemp = Math.round((min_temp + (-calcrotation + 240) * step) * 2)  / 2

                rotator.rotation = Math.abs(settemp / step - 480)

                modules.loaded_instances['Logic']['Thermostat'][tickswindow.instancename].set_temp = settemp


                }


            }


        }
    }

    Rectangle {
        property int fontheight: rotator.height * 0.04

        id: rotator
        height: tickswindow.height * 1.5
        width: height
        anchors.verticalCenter: tickswindow.verticalCenter
        anchors.horizontalCenter: tickswindow.right
        anchors.horizontalCenterOffset: rotator.width * 0.15
        color: "transparent"
        border.width: 1
        border.color: Colors.black
        radius: width / 2
        rotation: 90


        Behavior on rotation {

            PropertyAnimation {}

        }


        Repeater {


            model: 81

            Rectangle {

                anchors.centerIn: parent
                //width: 5
                height: parent.height - 10
                color: "transparent"
                rotation: (index+20) * 3 - 30
                Text {
                    text: (index) % 5 == 0 ? Math.round(min_temp + (((index+20) * 3) - 60)
                                            * ((max_temp - min_temp) / 240)) : ''
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenterOffset: rotator.width * -0.4
                    anchors.horizontalCenterOffset: 0
                    color: Colors.black
                    rotation: 90
                    font.pixelSize: rotator.fontheight
                }

                Rectangle {
                    layer.enabled: true
                    layer.smooth: true
                    color: Qt.rgba(((index) / 80), (1 - 2 * Math.abs(((index) / 80) - 0.5)),1 - ((index) / 80), 1)
                    width: rotator.width * 0.01
                    height: rotator.height * 0.05
                    anchors.left: parent.left
                    //antialiasing: true
                }
            }
        }
    }

    Rectangle {

        anchors.verticalCenter: tickswindow.verticalCenter
        anchors.right: tickswindow.right
        anchors.rightMargin: rotator.width * 0.21
        width: 100
        height: 34
        radius: height / 4
        color: "transparent"
        border.width: 5

        border.color: Colors.black
    }

    Popup {
        property string instancename: tickswindow.instancename != undefined ? tickswindow.instancename : modules.modules['Logic']['Thermostat'][0]

        id: thermostatPopup
        width: parent.width
        height: parent.height
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

        Loader {
            property string instancename: tickswindow.instancename != undefined ? tickswindow.instancename : modules.modules['Logic']['Thermostat'][0]
            asynchronous: true
            anchors.fill: parent
            id: thermostatSchedule
            source: "../thermostat/ThermostatWeek.qml"
        }
    }
}
