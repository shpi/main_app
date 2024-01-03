import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Flickable {

    property var icons: []
    property var listnames: []
    property int selectedIconIndex: -1 // Property to track the selected icon index
    property string instancename: modules.modules['UI']['ShowValue'][0]
    contentHeight: list.implicitHeight + 100



 function updateGridViewHeight() {
        gridView.height = Math.ceil(icons.length / Math.floor(gridView.width / gridView.cellWidth)) * gridView.cellHeight + 70;
    }

    function getIndexofList(path, mmodel) {

        for (var i = 0; i < mmodel.length; i++) {

            if (path === mmodel[i]) {
                return i
            }
        }
        return 0
    }

    function listProperty() {

        var component = Qt.createComponent("../../fonts/Icons.qml")
        var obj = component.createObject()

        listnames = []

        icons = []

        for (var prop in obj) {

            if (typeof (obj[prop]) == 'string' && prop !== 'objectName') {
                // console.log(prop + ' ' +  obj[prop]);
                listnames.push(prop)
                icons.push(obj[prop])
            }
        }

      updateGridViewHeight();

    }





        Text {
            id: title
            anchors.left: parent.left
            text: 'ShowValue > ' + instancename
            color: Colors.black
            font.bold: true
            font.pixelSize: 32
            height: 70
            padding: 10
        }

    Column {
        width: parent.width * 0.95
        anchors.horizontalCenter: parent.horizontalCenter
        id: list
         anchors.top: title.bottom
         spacing: 20
         padding: 10

        Text {

            text: modules.loaded_instances['UI']['ShowValue'][instancename].value
            color: Colors.black
            font.bold: true
            anchors.topMargin: 10
            anchors.right: parent.right
        }

        TextField {
            onActiveFocusChanged: keyboard(this)
            id: divider_text
            anchors.right: parent.right
            width: 550
            Component.onCompleted: divider_text.text = modules.loaded_instances['UI']['ShowValue'][instancename].divider
            onTextChanged: modules.loaded_instances['UI']['ShowValue'][instancename].divider
                           = divider_text.text

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Divider"
                color: Colors.black
            }
        }

        ComboBox {
            id: combo_value_path
            anchors.right: parent.right
            width: 550
            model: inputs.inputList
            textRole: 'path'
            Component.onCompleted: {

                combo_value_path.currentIndex = getIndex(
                            modules.loaded_instances['UI']['ShowValue'][instancename].value_path,
                            inputs.inputList)
            }

            onActivated: modules.loaded_instances['UI']['ShowValue'][instancename].value_path  = combo_value_path.currentText

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "VarPath"
                font.family: localFont.name
                color: Colors.black
            }
        }

        SpinBox {
            id:precbox
            anchors.right: parent.right
            stepSize: 1

            onValueModified: modules.loaded_instances['UI']['ShowValue'][instancename].precision = this.value
            from: 0
            to: 4

            Component.onCompleted: { precbox.value = modules.loaded_instances['UI']['ShowValue'][instancename].precision
                                   }


            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Precision"
                color: Colors.black
            }
        }



GridView {
    id: gridView
    width: parent.width
    height: 0
    interactive: false     
    cellWidth: 120
    cellHeight: 100

header: Rectangle {
                    width: parent.width
                    height: 70
                    color: "transparent"

                    Text {
                        padding: 10
                        anchors.right: parent.right
                        width: implicitWidth
                        text: "Icon"
                        font.pixelSize: 30
                        color: Colors.black
                        height: 70
                    }
                 }


    model: ListModel {
        id: gridModel
        Component.onCompleted: {
            for (var i = 0; i < icons.length; ++i) {
                append({"name": listnames[i], "icon": icons[i]})
            }
        }
    }


  delegate: Item {
            width: gridView.cellWidth
            height: gridView.cellHeight

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    selectedIconIndex = index // Update the selected index
                    // Update your instance's icon value here
                    modules.loaded_instances['UI']['ShowValue'][instancename].icon = model.icon
                }
            }

            Column {
                anchors.fill: parent
                spacing: 5

                Text {
                    text: icon
                    font.family: localFont.name
                    font.pixelSize: 55
                    color: selectedIconIndex === index ? "red" : Colors.black // Highlight selected icon
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    text: name
                    font.pixelSize: 16
                    color: selectedIconIndex === index ? "red" : Colors.black // Highlight selected text
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }
    }





        RoundButton {
            text: 'Delete Instance'
            palette.button: "darkred"
            palette.buttonText: "white"
            onClicked: {

                settingsstackView.pop()
                modules.remove_instance('UI', 'ShowValue', instancename)


            }
        }
    }

    Component.onCompleted: {
        listProperty()
        selectedIconIndex  = getIndexofList(
                    modules.loaded_instances['UI']['ShowValue'][instancename].icon,
                    icons)
    }
}

