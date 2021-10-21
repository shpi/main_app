import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {



    property string instancename: modules.modules['UI']['ColorPicker'][0]

    color: "transparent"

    Component.onCompleted: {

        inputs.set_outputList('percent')


    }


    Text {
        id: title
        anchors.left: parent.left
        text: 'ColorPicker > ' + instancename
        color: Colors.black
        font.bold: true
        font.pixelSize: 32
        height: 70
        padding: 10
    }

    Column {
        width: parent.width * 0.9
        anchors.horizontalCenter: parent.horizontalCenter
        id: list
        spacing: 20
        padding: 10
         anchors.top: title.bottom



        Flow {
            width: parent.width
            height: implicitHeight

            Text {
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: "Red"
                font.pixelSize: 24
                color: Colors.black
                wrapMode: Text.WordWrap
                width: parent.width < 500 ? parent.width : parent.width * 0.2
                height: 50
            }


        ComboBox {
            id: combo_red_path
            width: parent.width < 500 ? parent.width : parent.width * 0.8
            height: 50
            model: inputs.outputList
            textRole: 'path'
            Component.onCompleted: {

                combo_red_path.currentIndex = getIndex(
                            modules.loaded_instances['UI']['ColorPicker'][instancename].red_path,
                            inputs.outputList)
            }

            onActivated: modules.loaded_instances['UI']['ColorPicker'][instancename].red_path  = combo_red_path.currentText


        }}

        Flow {
            width: parent.width
            height: implicitHeight

            Text {
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: "Red"
                font.pixelSize: 24
                color: Colors.black
                wrapMode: Text.WordWrap
                width: parent.width < 500 ? parent.width : parent.width * 0.2
                height: 50
            }

        ComboBox {
            id: combo_green_path
            width: parent.width < 500 ? parent.width : parent.width * 0.8
            height: 50
            model: inputs.outputList
            textRole: 'path'
            Component.onCompleted: {

                combo_green_path.currentIndex = getIndex(
                            modules.loaded_instances['UI']['ColorPicker'][instancename].green_path,
                            inputs.outputList)
            }

            onActivated: modules.loaded_instances['UI']['ColorPicker'][instancename].green_path  = combo_green_path.currentText


        }}

        Flow {
            width: parent.width
            height: implicitHeight

            Text {
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: "Blue"
                font.pixelSize: 24
                color: Colors.black
                wrapMode: Text.WordWrap
                width: parent.width < 500 ? parent.width : parent.width * 0.2
                height: 50
            }
        ComboBox {
            id: combo_blue_path
            width: parent.width < 500 ? parent.width : parent.width * 0.8
            height: 50
            model: inputs.outputList
            textRole: 'path'
            Component.onCompleted: {

                combo_blue_path.currentIndex = getIndex(
                            modules.loaded_instances['UI']['ColorPicker'][instancename].blue_path,
                            inputs.outputList)
            }

            onActivated: modules.loaded_instances['UI']['ColorPicker'][instancename].blue_path  = combo_blue_path.currentText


        }}



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
