import QtQuick 2.12
import QtQuick.Controls 2.12

import "../fonts/"

Item {

    property string category


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
                onClicked: if (category == '') settingsstackView.push(Qt.resolvedUrl('Modules.qml'), {"category" : modelData})
                           else settingsstackView.push(Qt.resolvedUrl('ModulesClasses.qml'), {"category": category, "classname" : modelData })


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
                      text: category != '' ? '<b>' + category + ' Modules </b>' : '<b>Modules</b>'
                      color: Colors.black
                      font.pointSize: 12
                      }
                    }

                model: modules.instances(category,'')
                anchors.fill: parent
                delegate: listDelegate

            }

        }



