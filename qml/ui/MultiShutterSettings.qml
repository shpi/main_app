import QtQuick 2.12
import QtQuick.Controls 2.12

import "qrc:/fonts"

Rectangle {

    property string category
    property string classname
    property string instancename


    Component.onCompleted: {

        inputs.set_outputList('percent')


    }


    color: "transparent"

    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 10

        Column {
            width: parent.width * 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            id: list
            spacing: 20



            Text {
                text: "Selected Outputs"
                color: Colors.black
                font.bold: true
                anchors.topMargin: 20
            }
            Row {
                width: parent.width
                spacing: 10
            ComboBox
            {
                id: combo_desired_position_path

                width: 450
                model: inputs.outputList
                textRole: 'path'



                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "Desired Position"

                    font.family: localFont.name
                    color: Colors.black
                }
            }

            RoundButton {
                text: 'add'
                palette.button: "darkred"
                palette.buttonText: "white"

                font.pixelSize: 24
                font.family: localFont.name
                onClicked: modules.loaded_instances['UI']['MultiShutter'][instancename].add_path(combo_desired_position_path.currentText)
            }

}
            Repeater {

                model: modules.loaded_instances['UI']['MultiShutter'][instancename].desired_position_path
                Rectangle {
                    color: index % 2 === 0 ? Colors.white : "transparent"
                    height: 50
                    width: parent.width
                    anchors.left: parent.left
                    anchors.leftMargin: 10

                    Text {
                        width: parent.width
                        anchors.verticalCenter: parent.verticalCenter
                        color: Colors.black
                        text: modelData
                    }
                    RoundButton {
                        text: 'remove'
                        palette.button: "darkred"
                        palette.buttonText: "white"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 20
                        font.pixelSize: 24
                        font.family: localFont.name
                        onClicked: modules.loaded_instances['UI']['MultiShutter'][instancename].remove_path(modelData)
                    }
                }
            }



            RoundButton {
                text: 'Delete Instance'
                palette.button: "darkred"
                palette.buttonText: "white"
                onClicked: {

                    settingsstackView.pop()
                    modules.remove_instance('UI', 'MultiShutter', instancename)


                }
            }

        }
    }
}
