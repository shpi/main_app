import QtQuick 2.12
import QtQuick.Controls 2.12

import "../fonts/"

Item {

    id: root
    property string roomname: ''

    ListView {

        id: roomview
        header: Rectangle {

            width: parent.width
            height: 50
            color: "transparent"
            Text {
                padding: 10
                width: parent.width
                text: root.roomname === '' ? '<b>Available Rooms</b>' : '<b>Room: '
                                             + roomname + '</b>'
                color: Colors.black
                font.pointSize: 12
            }
        }

        model: root.roomname === '' ? modules.available_rooms : modules.rooms[roomname]
        anchors.fill: parent
        delegate: listDelegate

        footer: Column {

            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10

            Row {

                height: 50
                spacing: 10
                anchors.horizontalCenter: parent.horizontalCenter

                TextField {

                    id: roomname_text
                    font.pointSize: 14
                    height: 50
                    width: 600
                    placeholderText: 'Add new room'

                    visible: root.roomname !== '' ? false : true
                }

                ComboBox {
                    id: combo_value_path
                    height: 50
                    width: 600
                    model: modules.all_instances()

                    visible: root.roomname !== '' ? true : false
                }

                RoundButton {
                    anchors.verticalCenter: parent.verticalCenter
                    radius: 20
                    height: 50
                    padding: 10
                    text: '<b>Add</b>'
                    font.pixelSize: 30

                    onClicked: {
                        var roomarr
                        if (root.roomname === '') {

                            roomarr = modules.available_rooms
                            roomarr.push(roomname_text.text)
                            modules.available_rooms = roomarr
                            roomview.model = modules.available_rooms
                            roomview.forceLayout()
                        } else {

                            roomarr = modules.rooms[roomname]
                            roomarr.push(combo_value_path.currentText)
                            modules.set_rooms(roomname, roomarr)
                            roomview.model = modules.rooms[roomname]
                            roomview.forceLayout()
                        }
                    }
                }
            }

            RoundButton {

                text: 'Delete Room'
                onClicked: {
                    modules.delete_room(roomname)
                    settingsstackView.pop()
                }

                visible: root.roomname !== ''
                         && roomview.count == 0 ? true : false
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
                    text: root.roomname === '' ? Icons.arrow : Icons.trash
                    rotation: root.roomname === '' ? 270 : 0
                    font.family: localFont.name
                    color: Colors.black

                    MouseArea {

                        anchors.fill: parent
                        onClicked: if (roomname !== '') {
                                       var roomarr
                                       roomarr = modules.rooms[roomname]
                                       roomarr.splice(parent.parent.index, 1)
                                       modules.set_rooms(roomname, roomarr)
                                       parent.parent.parent.model = modules.rooms[roomname]
                                       roomview.forceLayout()
                                   }
                        enabled: roomname === '' ? false : true
                    }
                }

                MouseArea {
                    id: mouse
                    anchors.fill: parent
                    onClicked: if (roomname == '')
                                   settingsstackView.push(Qt.resolvedUrl(
                                                              'Rooms.qml'), {
                                                              "roomname": modelData
                                                          })
                    enabled: roomname === '' ? true : false
                }
            }
        }
    }
}
