import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    property string category
    property string classname
    property string instancename




    color: "transparent"



    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 100



        Text {
            id: title
            anchors.left: parent.left
            text: 'PieChart > ' + instancename
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
             anchors.top: title.bottom
             spacing: 20
             padding: 10



            Flow {
                width: parent.width
                height: implicitHeight

                Text {
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    text: "Value"
                    font.pixelSize: 24
                    color: Colors.black
                    wrapMode: Text.WordWrap
                    width: parent.width < 500 ? parent.width : parent.width * 0.2
                    height: 50
                }

            ComboBox
            {
                id: combo_desired_position_path
                width: parent.width < 500 ? parent.width : parent.width * 0.8
                height: 50
                model: inputs.inputList
                textRole: 'path'

            }

            RoundButton {
                text: 'add'
                palette.button: "darkred"
                palette.buttonText: "white"
                font.pixelSize: 24
                font.family: localFont.name
                onClicked: modules.loaded_instances['UI']['PieChart'][instancename].add_path(combo_desired_position_path.currentText)
            }

}
            Repeater {

                model: modules.loaded_instances['UI']['PieChart'][instancename].value_path
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
                        onClicked: modules.loaded_instances['UI']['PieChart'][instancename].remove_path(modelData)
                    }
                }
            }



            RoundButton {
                text: 'Delete Instance'
                palette.button: "darkred"
                palette.buttonText: "white"
                onClicked: {

                    settingsstackView.pop()
                    modules.remove_instance('UI', 'PieChart', instancename)


                }
            }

        }
    }
}
