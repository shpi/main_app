import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {



    property string instancename: modules.modules['UI']['ColorPicker'][0]

    color: "transparent"

    Component.onCompleted: {

        inputs.set_outputList('percent')


    }

    Column {
        width: parent.width * 0.9
        anchors.horizontalCenter: parent.horizontalCenter
        id: list
        spacing: 10





        ComboBox {
            id: combo_red_path
            anchors.right: parent.right
            width: 550
            model: inputs.outputList
            textRole: 'path'
            Component.onCompleted: {

                combo_red_path.currentIndex = getIndex(
                            modules.loaded_instances['UI']['ColorPicker'][instancename].red_path,
                            inputs.outputList)
            }

            onActivated: modules.loaded_instances['UI']['ColorPicker'][instancename].red_path  = combo_red_path.currentText

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Red Path"
                font.family: localFont.name
                color: Colors.black
            }
        }


        ComboBox {
            id: combo_green_path
            anchors.right: parent.right
            width: 550
            model: inputs.outputList
            textRole: 'path'
            Component.onCompleted: {

                combo_green_path.currentIndex = getIndex(
                            modules.loaded_instances['UI']['ColorPicker'][instancename].green_path,
                            inputs.outputList)
            }

            onActivated: modules.loaded_instances['UI']['ColorPicker'][instancename].green_path  = combo_green_path.currentText

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Green Path"
                font.family: localFont.name
                color: Colors.black
            }
        }


        ComboBox {
            id: combo_blue_path
            anchors.right: parent.right
            width: 550
            model: inputs.outputList
            textRole: 'path'
            Component.onCompleted: {

                combo_blue_path.currentIndex = getIndex(
                            modules.loaded_instances['UI']['ColorPicker'][instancename].blue_path,
                            inputs.outputList)
            }

            onActivated: modules.loaded_instances['UI']['ColorPicker'][instancename].blue_path  = combo_blue_path.currentText

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                text: "Blue Path"
                font.family: localFont.name
                color: Colors.black
            }
        }



        RoundButton {
            text: 'Delete Instance'
            palette.button: "darkred"
            palette.buttonText: "white"
            onClicked: {

                settingsstackView.pop()
                modules.remove_instance('UI', 'ColorPicker', instancename)


            }
        }
    }


}
