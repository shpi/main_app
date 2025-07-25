import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    property string category
    property string classname
    property string instancename


    Component.onCompleted: {

        inputs.set_outputList('percent')
        inputs.set_typeList('percent')

    }


    color: "transparent"

    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 100

        Text {
            id: title
            text: "Shutter > " + instancename
            color: Colors.black
            font.bold: true
            font.pixelSize:32
            padding: 10
            width: parent.width
            height:70
        }

        Column {
            width: parent.width * 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            id: list
             anchors.top: title.bottom
             spacing: 20
             padding: 10




            ComboBox {
                id: combo_desired_position
                anchors.right: parent.right
                width: 450
                model: inputs.outputList
                textRole: 'path'
                onActivated:  modules.loaded_instances['UI']['Shutter'][instancename].desired_position_path = this.currentText

                Component.onCompleted: {

                    combo_desired_position.currentIndex = getIndex(modules.loaded_instances['UI']['Shutter'][instancename].desired_position_path, inputs.outputList)
                }

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "Desired Position"

                    font.family: localFont.name
                    color: Colors.black
                }
            }

            ComboBox {
                id: combo_actual_position
                anchors.right: parent.right
                width: 450
                model: inputs.typeList
                textRole: 'path'
                onActivated: modules.loaded_instances['UI']['Shutter'][instancename].actual_position_path = this.currentText


                Component.onCompleted: {

                    combo_actual_position.currentIndex = getIndex(modules.loaded_instances['UI']['Shutter'][instancename].actual_position_path, inputs.typeList)
                }


                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: 'Actual Position'
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
                    modules.remove_instance('UI', 'Shutter', instancename)


                }
            }


        }
    }
}
