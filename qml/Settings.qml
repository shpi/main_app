import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

    ListModel {
        id: pageModel
        ListElement {
            title: "System Variables"
            page: "core/InputsSettings.qml"
        }
        ListElement {
            title: "Modules"
            page: "Modules.qml"
        }

        ListElement {
            title: "Rooms / Categories"
            page: "RoomManager.qml"
        }


        ListElement {
            title: "Screensaver Pictures"
            page: "Pictures.qml"
        }


    }

    Component {
        id: listDelegate

        Item {
            width: parent.width
            height: 80

            Rectangle {
                anchors.fill: parent
                color: index % 2 === 0 ? "transparent" : Colors.white
            }

            Text {
                id: textitem
                color: Colors.black
                font.pixelSize: 32
                text: title
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 30
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 10
                height: 1
                color: "#424246"
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 20
                text: Icons.arrow
                rotation: 270
                font.family: localFont.name
                color: Colors.black
            }

            MouseArea {
                id: mouse
                anchors.fill: parent
                onClicked: settingsstackView.push(Qt.resolvedUrl(page))
            }
        }
    }

    ListView {

        header: Rectangle {

            width: parent.width
            height: 50
            color: "transparent"
            Text {
                padding: 10
                width: parent.width
                text: '<b>Settings</b>'
                color: Colors.black
                font.pixelSize: 32
            }
        }

        model: pageModel
        anchors.fill: parent
        delegate: listDelegate
    }
}
