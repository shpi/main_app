import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

    property string category
    property string classname

    StackView.onActivated: {

        instantview.model = modules.instances(category, classname)
        instantview.forceLayout()
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
                color: "transparent"
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
                onClicked: settingsstackView.push(
                               Qt.resolvedUrl(
                                   category.toLowerCase(
                                       ) + '/' + classname + 'Settings.qml'), {
                                   "instancename": modelData
                               })
            }





        }
    }

    ListView {
        anchors.fill: parent
        anchors.horizontalCenter: parent.horizontalCenter

        id: instantview




        header: Rectangle {

            width: parent.width
            height: 50
            color: "transparent"
            Text {
                padding: 10
                width: parent.width
                text: '<b>' + category + ' > ' + classname + '</b>'
                color: Colors.black
                font.pixelSize: 32
            }
        }

        model: modules.instances(category, classname)
        width: parent.width
        delegate: listDelegate

        footer: Row {
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter

            TextField {

                id: instancename
                font.pixelSize: 32
                height: 50
                width: 400
                placeholderText: 'Add new instance'
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
                    modules.add_instance(category, classname, instancename.text)
                    instantview.model = modules.instances(category, classname)
                    instantview.forceLayout()
                    
                }
            }
        }
    }




}
