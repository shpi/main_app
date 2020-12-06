import QtQuick 2.12
import QtQuick.Controls 2.12

import "../fonts/"

Item {


    ListModel {
        id: pageModel
        ListElement {
            title: "System Variables"
            page: "Inputs.qml"
        }
        ListElement {
            title: "HTTP Server"
            page: "content/SliderPage.qml"
        }
        ListElement {
            title: "MQTT Client"
            page: "content/ProgressBarPage.qml"
        }

    }


    Component {
        id: listDelegate

        Item {
            width: parent.width
            height: 80

            Rectangle {
                anchors.fill: parent
                color: "#11ffffff"
                visible: mouse.pressed
            }

            Text {
                id: textitem
                color: "white"
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
                color: "white"
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
                      height:50
                      color:  "transparent"
                      Text {
                      padding: 10
                      width: parent.width
                      text: '<b>Settings</b>'
                      color: "white"
                      font.pointSize: 12
                      }
                    }

                model: pageModel
                anchors.fill: parent
                delegate: listDelegate

            }
        }



