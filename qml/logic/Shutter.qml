import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.12
import "qrc:/fonts"

Rectangle {
    id: shutterFrame
    height: parent.height
    width: height * 0.7
    radius: 10
    color: Colors.whitetrans
    clip: true
    property string instancename: parent.instancename !== undefined ? parent.instancename : modules.modules['Logic']['Shutter'][0]
    property bool iconview: parent.iconview !== undefined ? parent.iconview : false

    Rectangle {

        property bool iconview2: shutterFrame.iconview

        id: shutterObject


        Behavior on height { PropertyAnimation {}  }



        height: parent.height * 0.75
        width: height * 0.7
        border.width: 1
        border.color: Colors.black
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        RoundButton {


        height: control.height / 2.1
        width: 70
        onClicked:  modules.loaded_instances['Logic']['Shutter'][instancename].set_desired_position(100)
        text:  Icons.arrow
        visible: shutterObject.iconview2 ? false : true
        anchors.top: control.top
        anchors.left: control.right
        anchors.leftMargin: 20
        font.pixelSize: 60
        rotation: 180


        }


        RoundButton {


        height: control.height / 2.1
        width: 70
        onClicked:  modules.loaded_instances['Logic']['Shutter'][instancename].set_desired_position(0)
        text:  Icons.arrow
        visible: shutterObject.iconview2 ? false : true
        anchors.bottom: control.bottom
        anchors.left: control.right
        anchors.leftMargin: 20
        font.pixelSize: 60
        }

        Slider {
            id: control
            from: 0
            to: 100
            value: pressed == false ? modules.loaded_instances['Logic']['Shutter'][instancename].actual_position : modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
            orientation: Qt.Vertical
            height: parent.height - 2
            width: parent.width - 2
            anchors.centerIn: parent

            Behavior on value { NumberAnimation {} }

            enabled: shutterObject.iconview2 ? false : true

            stepSize: 5
            onPressedChanged: if (this.pressed === false)
                                  modules.loaded_instances['Logic']['Shutter'][instancename].set_desired_position(
                                              this.value)

            Text {
                text: modules.loaded_instances['Logic']['Shutter'][instancename].actual_position
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.horizontalCenterOffset: -parent.width * 0.07
                anchors.verticalCenterOffset: parent.value > 50 ? parent.height
                                                                  * 0.2 : -parent.height * 0.2
                font.pixelSize: parent.height * 0.29
                visible: modules.loaded_instances['Logic']['Shutter'][instancename].actual_position !== -1

                color: Colors.black
                Text {
                    text: "%"
                    font.pixelSize: parent.parent.height * 0.14
                    anchors.left: parent.right
                    anchors.bottom: parent.bottom
                    color: Colors.black
                }
            }

            Text {
                width: control.width
                text: shutterObject.iconview2 ? "??" : "Unknown position, will be calibrated on first move."
                wrapMode: Text.Wrap
                horizontalAlignment: Text.AlignHCenter
                color: "red"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                visible: modules.loaded_instances['Logic']['Shutter'][instancename].actual_position === -1
                anchors.verticalCenterOffset: parent.value > 50 ? parent.height
                                                                  * 0.3 : -parent.height * 0.3
                fontSizeMode: Text.Fit


            }

            background: Rectangle {

                width: control.width
                height: control.height
                border.width: 1
                border.color: Colors.grey

                color: appearance.night === 1 ? "#333" : "#ddd"

                Column {
                    spacing: parent.height / 10
                    anchors.top: parent.top
                    anchors.fill: parent
                    Repeater {
                        model: 10
                        Rectangle {
                            width: parent.parent.width
                            height: 1
                            color: Colors.grey
                        }
                    }
                }

                Rectangle {


                    anchors.bottom: parent.bottom
                    height: parent.height - (control.visualPosition * parent.height)
                    width: control.width
                    border.width: 1
                    border.color: Colors.grey
                    color: appearance.night === 1 ? "#117" : "#99f"



                    /* LinearGradient {
                    anchors.fill: parent
                    start: Qt.point(0, 1)
                    end: Qt.point(0, 100)
                    gradient: Gradient {
                        GradientStop {
                            position: 0.0
                            color: "#002"
                        }
                        GradientStop {
                            position: 1.0
                            color: "#55f"
                        }
                    }
                } */
                }
            }

            Rectangle {
                z: parent.handle.z - 0.01
                visible: modules.loaded_instances['Logic']['Shutter'][instancename].actual_position
                         !== modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
                         && parent.pressed == false ? true : false

                width: parent.width * 1.1
                height: parent.height * 0.15
                radius: height / 2
                opacity: 0.5
                color: Colors.black

                y: control.height
                   - ((modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
                       / 100) * control.height) - height / 2

                anchors.horizontalCenter: parent.horizontalCenter
            }



            handle: Rectangle {

                //y: control.topPadding + control.visualPosition * (control.availableHeight - height)
                y: (control.visualPosition * control.height) - height / 2
                width: parent.width * 1.1
                anchors.horizontalCenter: parent.horizontalCenter
                height: parent.height * 0.15
                radius: height / 2
                color: control.pressed ? "#f0f0f0" : "#f6f6f6"
                border.color: "#bdbebf"
                Text {
                    id: handleIcon
                    font.family: localFont.name

                    text: {
                        modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
                                === modules.loaded_instances['Logic']['Shutter'][instancename].actual_position ? Icons.shutter : Icons.arrow
                    }
                    rotation: modules.loaded_instances['Logic']['Shutter'][instancename].desired_position > modules.loaded_instances['Logic']['Shutter'][instancename].actual_position ? 180 : 0
                    anchors.centerIn: parent
                    font.pixelSize: parent.height
                    opacity: 1
                }
            }
        }
    }







    MouseArea {
        anchors.fill: parent
        onClicked: { popupShutter.open(); shutterObject.parent = shutterPopup;  shutterObject.iconview2 = false; }
        enabled: iconview
    }

    Popup {
        id: popupShutter

        enter: Transition {

            NumberAnimation {property: "opacity"; from: 0.0; to: 1.0}
            NumberAnimation {property: "scale"; from: 0.5; to: 1.0}

        }

        exit: Transition {

            NumberAnimation {property: "opacity"; from: 1.0; to: 0.0}

        }

        height: window.height
        width: window.width

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


        Rectangle {
        anchors.fill: parent
        color: "transparent"
        id: shutterPopup
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
            onClicked:  { shutterObject.iconview2 = true; shutterObject.parent = shutterFrame; popupShutter.close() }

        }


          Connections {
        target: appearance
        function onJump_stateChanged() {
            if (appearance.jump_state) {
shutterObject.iconview2 = true; shutterObject.parent = shutterFrame; popupShutter.close() 
            }
        }
    }




    }











}
