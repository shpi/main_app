import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    Rectangle {
        id: modulestitle
        anchors.top: parent.top
        width: parent.width
        implicitHeight: modulestitle_text.implicitHeight
        color: "transparent"

        Text {
            id: modulestitle_text
            padding: 5
            width: parent.width
            text: '<b>Active Modules</b>'
            font.pixelSize: 16
            color: Colors.black
        }
    }

    ListView {
        id: listview

        model: modules.instances_list
        delegate: listitem_delegate

        anchors.top: modulestitle.bottom
        anchors.bottom: parent.bottom
        width: parent.width
        clip: true

        property var item_height_min: 50
        spacing: 10
        orientation: Qt.Vertical
        currentIndex: -1
        cacheBuffer: item_height_min * 4

        Component {
            id: listitem_delegate

            Rectangle {
                id: wrapper

                width: parent.width
                // height: listview.item_height_min
                height: implicitHeight

                color: Colors.white
                border.color: Colors.black
                border.width: 1

                Row {
                    id: row1
                    anchors.top: parent.top
                    anchors.margins: 20
                    width: parent.width
                    height: implicitHeight

                    Text {
                        id: classname_text
                        anchors.leftMargin: 30

                        text: classname
                        font.pixelSize: 20
                        color: Colors.black
                    }

                    Text {
                        id: instancename_text
                        anchors.leftMargin: 20

                        text: instancename ? instancename : ""
                        visible: instancename !== undefined
                        font.pixelSize: 20
                        font.italic: true
                        color: Colors.black
                    }
                }

                Row {
                    id: row2
                    anchors.top: row1.top
                    anchors.margins: 20
                    width: parent.width
                    height: implicitHeight

                    Text {
                        id: description_text
                        anchors.leftMargin: 30

                        text: description
                        font.pixelSize: 20
                        color: Colors.black
                    }
                }
//            MouseArea {
//                id: mouse
//                anchors.fill: parent
//                onClicked: if (category == '')
//                               settingsstackView.push(Qt.resolvedUrl(
//                                                          'Modules.qml'), {
//                                                          "category": modelData
//                                                      })
//                           else
//                               settingsstackView.push(
//                                           Qt.resolvedUrl(
//                                               'ModulesClasses.qml'), {
//                                               "category": category,
//                                               "classname": modelData
//                                           })
//            }
            }
        }
    }
}