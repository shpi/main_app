import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import "../../fonts/"

Rectangle {



    id: shutterFrame
    height: parent.height
    width: height * 0.7
    radius: 10
    color: Colors.whitetrans
    //clip: true
    property bool iconview: false

    property string name: modules.modules['UI']['MultiShutter'][0]



    Rectangle {

        property bool iconview2: shutterFrame.iconview

        id: shutterObject


        height: parent.height * 0.75
        width: height * 0.7
        border.width: 1
        border.color: Colors.black

        anchors.horizontalCenter: parent.horizontalCenter

        anchors.verticalCenter: parent.verticalCenter

        Text {
        anchors.top: parent.top
        anchors.right: parent.left
        text: modules.loaded_instances['UI']['MultiShutter'][name].success.toString()
        color: "green"
        anchors.rightMargin: 2
        font.pixelSize: shutterObject.iconview2 ? 30 : 50
        }


        Text {

        anchors.bottom: parent.bottom
        anchors.right: parent.left
        anchors.rightMargin: 2
        text: modules.loaded_instances['UI']['MultiShutter'][name].failed.toString()
        color: "red"
        font.pixelSize:  shutterObject.iconview2 ? 30 : 50
        }


        Slider {

            enabled: shutterObject.iconview2 ? false : true

            id: control
            from: 0
            to: 100
            value: modules.loaded_instances['UI']['MultiShutter'][name].desired_position
            orientation: Qt.Vertical
            height: parent.height - 2
            width: parent.width - 2
            anchors.centerIn: parent

            stepSize: 5
            onPressedChanged: if (this.pressed === false)
                                  modules.loaded_instances['UI']['MultiShutter'][name].set_position(
                                              this.value)

            Text {
                text: modules.loaded_instances['UI']['MultiShutter'][name].desired_position
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.horizontalCenterOffset: -parent.width * 0.07
                anchors.verticalCenterOffset: parent.value > 50 ? parent.height
                                                                  * 0.2 : -parent.height * 0.2
                font.pixelSize: parent.height * 0.29
                color: Colors.black
                Text {
                    text: "%"
                    font.pixelSize: parent.parent.height * 0.14
                    anchors.left: parent.right
                    anchors.bottom: parent.bottom
                    color: Colors.black
                }
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
                    text:  Icons.shutter
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



    }





}