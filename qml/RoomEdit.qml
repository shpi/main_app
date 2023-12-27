import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    id: root
    property string roomname

    ListView {
        id: roomview
        model: modules.rooms[roomname]
        anchors.fill: parent
        delegate: listDelegate

        header: Rectangle {
            width: parent.width
            height: 50
            color: "transparent"
            Text {
                padding: 10
                width: parent.width
                text: '<b>Room: ' + roomname + '</b>'
                color: Colors.black
                font.pixelSize: 32
            }
        }

        footer: Column {
            spacing: 20
            width: parent.width

            Row {
                anchors.bottomMargin: 20
                spacing: 20
                height: 100
                anchors.horizontalCenter: parent.horizontalCenter

                ComboBox {
                    anchors.verticalCenter: parent.verticalCenter
                    id: combo_value_path
                    height: 50
                    width: 600
                    model: modules.all_instances()
                    visible: true
                }

                RoundButton {
                    anchors.verticalCenter: parent.verticalCenter
                    radius: 20
                    height: 50
                    padding: 10
                    text: '<b>Add</b>'
                    font.pixelSize: 32

                    onClicked: {
                        modules.add_to_room(roomname, combo_value_path.currentText)
                        roomview.model = modules.rooms[roomname]
                        roomview.forceLayout()
                    }
                }
            }

            RoundButton {
                text: 'Delete Room'
                palette.button: "darkred"
                palette.buttonText: "white"
                font.pixelSize: 32
                font.family: localFont.name
                anchors.horizontalCenter: parent.horizontalCenter

                onClicked: {
                    modules.delete_room(roomname)
                    roomview.forceLayout()
                    roomview.model =  modules.rooms[roomname]
                    settingsstackView.pop()
                }

                visible: roomview.count == 0 ? true : false
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
                    font.pixelSize: 60
                    text: Icons.trash
                    rotation: 0
                    font.family: localFont.name
                    color: Colors.black

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            modules.del_from_room(roomname, modelData)
                            roomview.model = modules.rooms[roomname]
                        }
                        enabled: true
                    }
                }
            }
        }
    }
}
