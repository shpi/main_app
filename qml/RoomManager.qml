import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"


Item {
    id: root

    ListView {
        id: roomview
        model: modules.available_rooms
        anchors.fill: parent
        delegate: listDelegate

        header: Rectangle {
            width: parent.width
            height: 50
            color: "transparent"
            Text {
                padding: 10
                width: parent.width
                text: '<b>Available Rooms</b>'
                color: Colors.black
                font.pixelSize: 32
            }
        }

        footer: Column {
            spacing: 20
            width: parent.width

            Row {
                padding: 20
                spacing: 20
                height: 120
                anchors.horizontalCenter: parent.horizontalCenter

                TextField {
                    anchors.verticalCenter: parent.verticalCenter
                    id: roomname_text
                    font.pixelSize: 32
                    height: 50
                    width: 600
                    placeholderText: 'Add new room'
                    visible: true
                    onActiveFocusChanged: keyboard(this)
                }

                RoundButton {
                    anchors.verticalCenter: parent.verticalCenter
                    radius: 20
                    height: 50
                    padding: 10
                    text: '<b>Add</b>'
                    font.pixelSize: 32

                    onClicked: {
                        var roomarr = modules.available_rooms
                        roomarr.push(roomname_text.text)
                        modules.available_rooms = roomarr
                        roomview.model = modules.available_rooms
                        roomview.forceLayout()
                    }
                }
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
                    rotation: 270 
                    font.family: localFont.name
                    color: Colors.black

                    }



                MouseArea {


                    id: mouse
                    anchors.fill: parent
                    onClicked: 
                                   settingsstackView.push(Qt.resolvedUrl(
                                                              'RoomEdit.qml'), {
                                                              "roomname": modelData
                                                          })
                    enabled: true
                }
             
            }
        }
    }
}
