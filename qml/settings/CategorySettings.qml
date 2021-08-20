import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    id: root
    property string categoryname: ''

    ListView {
        id: categoryview
        header: Rectangle {
            width: parent.width
            height: 50
            color: "transparent"
            Text {
                padding: 10
                width: parent.width
                text: root.categoryname === '' ? '<b>Available Categories</b>' : '<b>Category: '
                                             + categoryname + '</b>'
                color: Colors.black
                font.pixelSize: 32
            }
        }

        model: root.categoryname === '' ? modules.categories_list : modules.categories_dict[categoryname]
        anchors.fill: parent
        delegate: listDelegate

        footer: Column {
            spacing: 20
            width: parent.width

            Row {
                anchors.bottomMargin: 20
                spacing: 20
                height: 100
                anchors.horizontalCenter: parent.horizontalCenter

                TextField {
                    id: roomname_text

                    anchors.verticalCenter: parent.verticalCenter
                    font.pixelSize: 32
                    height: 50
                    width: 600
                    placeholderText: 'Add new category'
                    visible: root.categoryname !== '' ? false : true
                    onActiveFocusChanged: keyboard(this)
                }

                ComboBox {
                    id: combo_value_path
                    anchors.verticalCenter: parent.verticalCenter
                    height: 50
                    width: 600
                    model: modules.all_instances()
                    visible: root.categoryname !== '' ? true : false
                }

                RoundButton {
                    anchors.verticalCenter: parent.verticalCenter
                    radius: 20
                    height: 50
                    padding: 10
                    text: '<b>Add</b>'
                    font.pixelSize: 32

                    onClicked: {
                        var roomarr
                        if (root.roomname === '') {

                            roomarr = modules.categories_list
                            roomarr.push(roomname_text.text)
                            modules.categories_list = roomarr
                            roomview.model = modules.categories_list
                            roomview.forceLayout()
                        } else {

                            modules.add_to_room(roomname, combo_value_path.currentText)
                            roomview.model = modules.rooms[roomname]
                            roomview.forceLayout()
                        }
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
                    font.pixelSize: 60
                    text: root.roomname === '' ? Icons.arrow : Icons.trash
                    rotation: root.roomname === '' ? 270 : 0
                    font.family: localFont.name
                    color: Colors.black

                    MouseArea {

                        anchors.fill: parent
                        onClicked: if (roomname !== '') {
                                       var roomarr
                                       //roomarr = modules.rooms[roomname]
                                       //roomarr.splice(parent.parent.index, 1)
                                       modules.del_from_room(roomname,modelData )
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
                                                              'RoomManager.qml'), {
                                                              "roomname": modelData
                                                          })
                    enabled: roomname === '' ? true : false
                }
            }
        }
    }
}
