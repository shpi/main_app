import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {

    property var icons: []
    property var listnames: []

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
    }

    property string instancename: modules.modules['UI']['ShowValue'][0]

    color: Colors.white

    Column {
        width: parent.width * 0.9
        anchors.horizontalCenter: parent.horizontalCenter
        id: list
        spacing: 20

        Text {

            text: "Value"
            color: Colors.black
            font.bold: true
            anchors.topMargin: 20
        }

        TextField {
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

            onActivated: modules.loaded_instances['UI']['ShowValue'][instancename].value_path
                         = this.currentText

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "VarPath"
                font.family: localFont.name
                color: Colors.black
            }
        }

        ComboBox {
            id: combo_icon
            anchors.right: parent.right
            width: 550
            model: listnames

            onActivated: {
                modules.loaded_instances['UI']['ShowValue'][instancename].icon
                        = icons[combo_icon.currentIndex]
                iconpreview.text = icons[combo_icon.currentIndex]
            }

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Icon"
                font.family: localFont.name
                color: Colors.black
            }

            Text {

                id: iconpreview
                font.family: localFont.name
                font.pixelSize: 120
                anchors.top: parent.bottom
                anchors.topMargin: 10
                anchors.horizontalCenter: parent.horizontalCenter
                color: Colors.black
            }
        }
    }

    Component.onCompleted: {
        listProperty()
        combo_icon.model = listnames
        combo_icon.currentIndex = getIndexofList(
                    modules.loaded_instances['UI']['ShowValue'][instancename].icon,
                    icons)
    }
}