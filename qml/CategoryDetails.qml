import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.12

import "qrc:/fonts"

Item {
    id: root

    property string categoryname

    GridView {
        id: categoriesview
        model: modules.categories_dict[categoryname]

        height: parent.height
        width: cellWidth * 3

        anchors.horizontalCenter: parent.horizontalCenter

        cellWidth: 260; cellHeight: 170

        header: Rectangle {
            id: header

            width: parent.width
            height: 100
            color: Colors.whitetrans

            RoundButton {
                id: backButton
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 10
                rotation: 90
                font.family: localFont.name
                font.pixelSize: 50
                text: Icons.arrow
                onClicked: categoriesstackView.pop()
                palette.button: 'lightgrey'
                palette.buttonText: "#555"
                width: height
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: backButton.right
                anchors.leftMargin: 10
                text: root.categoryname
                color: Colors.black
                font.bold: true
                font.pixelSize: 40
            }
        }

        delegate: listDelegate

        Component {
            id: listDelegate

            Rectangle {
                property var class_instancename: modelData.split('/')  // classname + optional instancename

                border.width:  1
                border.color: Colors.white
                color: "transparent"
                width: categoriesview.cellWidth - 5
                height: categoriesview.cellHeight - 5
                radius: 10
                /*
                Loader {
                    id: componentLoader
                    source: "modules/" + class_instancename[0] + ".qml"
                    anchors.fill: parent
                    asynchronous: true
                    property var instancename: class_instancename.length === 2 ? class_instancename[1] : ""
                    property var iconview: true
                }
                */
                Text {
                    id: textitem
                    color: Colors.black
                    font.pixelSize: 24
                    text: modelData //class_instancename[0]
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                }


                /* layer.enabled: true
                            layer.effect: DropShadow {
                                transparentBorder: true
                                horizontalOffset: 3
                                verticalOffset: 3
                                radius: 4.0
                                color: Colors.white
                            }
               */
            }
        }
    }
}
