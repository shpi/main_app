import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    color: "transparent"
    anchors.fill: parent

    Column {
        padding: 5
        spacing: 10
        anchors.fill: parent

        Text {
            visible: git.updates_remote === 0
            text: "You're up to date!"
            anchors.horizontalCenter: parent.horizontalCenter
            color: "green"
            font.pixelSize: 24
        }

        Text {
            visible: git.updates_remote > 0
            text: "New version available (" + git.updates_remote + ")"
            anchors.horizontalCenter: parent.horizontalCenter
            color: "red"
            font.pixelSize: 24
        }

        Row {
            visible: git.updates_remote > 0
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 20

            Text {
                visible: git.updates_remote > 0
                anchors.verticalCenter: parent.verticalCenter
                text: 'Version:'
                font.bold: true
                font.family: localFont.name
                font.pixelSize: 24
                color: Colors.black
            }
            Text {
                visible: git.updates_remote > 0
                text: git.update_shex + ', '
                      + new Date(git.update_timestamp * 1000).toLocaleDateString()
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Row {
            visible: git.updates_remote > 0
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 20

            Text {
                visible: git.updates_remote > 0
                anchors.verticalCenter: parent.verticalCenter
                text: 'Description:'
                font.bold: true
                font.family: localFont.name
                font.pixelSize: 24
                color: Colors.black
            }
            Text {
                visible: git.updates_remote > 0
                wrapMode: Text.WordWrap
                width: parent.width / 2
                text: git.update_description
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 20

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: 'Installed version:'
                font.family: localFont.name
                font.pixelSize: 24
                font.bold: true
                color: Colors.black
            }
            Text {

                text: git.current_version_hex + ', '
                      + new Date(git.current_version_date * 1000).toLocaleDateString()
                wrapMode: Text.WordWrap
                width: parent.width / 2
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }
        }


        /*
    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: 'Branch:'
            font.family: localFont.name
            font.pixelSize: 24
            color: Colors.black
        }
        Text {
            width: 200
            text: git.actual_branch

            font.pixelSize: 20
            color: Colors.black
            anchors.verticalCenter: parent.verticalCenter
        }


    } */
        Popup {
            property string text2: ''
            id: messageDialog
            width: parent.width * 0.9
            height: parent.height * 0.7
            parent: Overlay.overlay
            x: Math.round((parent.width - width) / 2)
            y: Math.round((parent.height - height) / 2)
            padding: 10
            topInset: 0
            leftInset: 0
            rightInset: 0
            bottomInset: 0

            enter: Transition {

                NumberAnimation {property: "opacity"; from: 0.0; to: 1.0}

            }

            exit: Transition {

                NumberAnimation {property: "opacity"; from: 1.0; to: 0.0}

            }

            background: Rectangle {
                color: Colors.white
                radius: 20
                border.width: 1
                border.color: Colors.black
            }

            ScrollView {
                id: scrollview
                anchors.fill: parent
                anchors.bottom: parent.bottom
                Text {
                    anchors.centerIn: parent
                    text: messageDialog.text2
                    color: Colors.black
                    font.pixelSize: 20
                }

                RoundButton {

                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 5
                    anchors.right: parent.right
                    anchors.rightMargin: 5
                    text: "OK"
                    palette.button: "darkgreen"
                    palette.buttonText: "white"
                    font.pixelSize: 40
                    font.family: localFont.name
                    onClicked: messageDialog.close()
                }
            }
        }

        DelayButton {
            text: "update " + Icons.doublearrow
            delay: 2500
            width: 300
            height: 80
            font.pixelSize: 50
            onActivated: {
                messageDialog.text2 = git.merge()
                messageDialog.open()
                git.update()
            }
            anchors.horizontalCenter: parent.horizontalCenter
            visible: git.updates_remote > 0 && git.updates_local === 0

            background: Rectangle {
                color: "green"
                radius: 20
                opacity: 0.3
                border.width: 2
            }
        }

        DelayButton {
            text: "reboot " + Icons.reset
            delay: 2500
            width: 300
            height: 80
            font.pixelSize: 50
            onActivated: git.reboot()
            anchors.horizontalCenter: parent.horizontalCenter

            background: Rectangle {
                color: "red"
                radius: 20
                opacity: 0.3
                border.width: 2
            }
        }
    }
}
