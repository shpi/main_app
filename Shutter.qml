import QtQuick 2.0
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import "fonts/"

// kalibrierfahrt 0 - 100 %

// Modus Binär, Hochlaufzeit / Runterlaufzeit
Item {
    anchors.fill: parent

    Text {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
        text: Icons.sunrise
        font.family: localFont.name
        font.pointSize: 30
    }

    Text {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 10
        font.pointSize: 30
        font.family: localFont.name
        text: Icons.sunset
    }

    Slider {
        id: control
        from: 0
        to: 100
        value: 50
        orientation: Qt.Vertical
        height: parent.height * 0.8
        width: 300
        anchors.centerIn: parent
        stepSize: 5
        Text {
            text: parent.value + "%"
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.left
            font.pointSize: 30
            anchors.rightMargin: 20
            color: "black"
        }

        background: Rectangle {

            border.width: 2
            border.color: "black"
            width: 300
            height: parent.height

            LinearGradient {
                anchors.fill: parent
                start: Qt.point(0, 0)
                end: Qt.point(0, control.visualPosition * parent.height)
                gradient: Gradient {
                    GradientStop {
                        position: 0.0
                        color: "#DDD"
                    }
                    GradientStop {
                        position: 1.0
                        color: "#555"
                    }
                }
            }

            Column {
                spacing: 30
                anchors.top: parent.top
                anchors.fill: parent
                Repeater {
                    model: 10
                    Rectangle {
                        width: parent.parent.width
                        height: 1
                        color: "grey"
                    }
                }
            }

            Rectangle {

                anchors.bottom: parent.bottom
                height: parent.height - (control.visualPosition * parent.height)
                width: parent.width

                LinearGradient {
                    anchors.fill: parent
                    start: Qt.point(0, 1)
                    end: Qt.point(0, 5 + control.visualPosition * parent.height)
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
                }
            }
        }

        handle: Rectangle {

            y: control.topPadding + control.visualPosition * (control.availableHeight - height)
            width: parent.width * 1.1
            anchors.horizontalCenter: parent.horizontalCenter
            height: parent.height * 0.15
            radius: 13
            color: control.pressed ? "#f0f0f0" : "#f6f6f6"
            border.color: "#bdbebf"
            Text {
                font.family: localFont.name
                text: Icons.shutter
                anchors.centerIn: parent
                font.pointSize: 35
            }
        }
    }

    Text {
        anchors.verticalCenter: parent.verticalCenter
        anchors.bottomMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 10
        font.pointSize: 30
        text: Icons.timer
        font.family: localFont.name
    }
}
