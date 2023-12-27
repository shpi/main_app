import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    Flickable {
        anchors.fill: parent
        contentHeight: columnLayout.height

        Column {
            id: columnLayout
            width: parent.width

            // First ListView
            ListView {
                id: inputsview
                width: parent.width
                model: inputs.folders
                delegate: pathDelegate
                clip: true

                header: Rectangle {
                    width: parent.width
                    height: 70
                    color: "transparent"

                    Text {
                        padding: 10
                        id: inputpath
                        anchors.left: parent.left
                        width: implicitWidth
                        text: "/" + inputs.currentPath
                        font.pixelSize: 30
                        color: Colors.black
                        height: 70
                    }

                    Text {
                        padding: 10
                        id: inputtitle
                        anchors.right: parent.right
                        width: implicitWidth
                        text: "System Vars"
                        font.bold: true
                        font.pixelSize: 32
                        color: Colors.black
                        height: 70
                    }
                }

                // Calculate height based on number of items
                height: 70 + inputsview.count * 70
                cacheBuffer: 100

                Component.onCompleted: {
                    inputs.set_path("");
                }
            }

            // Second ListView
            ListView {
                id: filesview
                width: parent.width
                model: inputs.files
                delegate: fileDelegate
                clip: true

                // Calculate height based on number of items
                height: filesview.count * 70
                cacheBuffer: 100
            }
        }
    }

    Component {
        id: fileDelegate

        Item {
            width: parent.width
            height: 60

            Rectangle {
                anchors.fill: parent
                color: index % 2 === 0 ? "transparent" : Colors.white
            }

            Text {
                color: Colors.black
                font.pixelSize: 24
                text: modelData
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 35
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 5
                height: 1
                color: "#424246"
            }
        }
    }

    Component {
        id: pathDelegate

        Item {
            width: parent.width
            height: 60

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
                anchors.leftMargin: 20
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 5
                height: 1
                color: "#424246"
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 30
                text: Icons.arrow
                rotation: 270
                font.family: localFont.name
                color: Colors.black
            }

            MouseArea {
                id: mouse
                anchors.fill: parent
                onClicked: inputs.set_path(inputs.currentPath + "/" + modelData) 
            }
        }
    }

    // ... any other components or logic you need ...
}
