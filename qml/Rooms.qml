import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

    StackView {
        id: roomstackView
        anchors.fill: parent
        initialItem: roomStart

        Component {

            id: roomStart

    ListView {

        id: roomview


        model: modules.available_rooms

        delegate: listDelegate

        footer: Rectangle { 
                  height: 50 
                  color: "transparent" }


        Component {
            id: listDelegate

            Item {
                width: parent.width
                height: 120

                Rectangle {
                    anchors.fill: parent
                    color: index % 2 === 0 ? "transparent" : Colors.whitetrans
                }

                Text {
                    id: textitem
                    color: Colors.black
                    font.pixelSize: 40
                    text: modelData
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
                    rotation:  270
                    font.family: localFont.name
                    color: Colors.black


                }

                MouseArea {
                    id: mouse
                    anchors.fill: parent
                    onClicked: roomstackView.push(
                                   Qt.resolvedUrl('Room.qml'), {
                                       "roomname": modelData
                                   })
                }


            }
        }
    }
}
}}
