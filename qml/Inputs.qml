import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    anchors.fill: parent


       ListView {
           anchors.fill:parent
            clip: true
            orientation: Qt.Vertical
            id: inputsview
            width: parent.width
            model: inputs.inputList
            delegate: inputDelegate
            focus: true

            Component {
                id: inputDelegate

                Rectangle {
                    property int delindex: index
                    id: wrapper
                    height: 60
                    width: inputsview.width
                    color: index % 2 === 0 ? "lightgrey" : "white"
                    Row {
                        spacing: 10
                        height: parent.height

                         Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: '<b>' + path + ' ' + description + '</b>, ' + type
                            font.pointSize: 12

                        }

                    }
                }
            }
        }

    Connections {
        target: inputs
        onInputsChanged: {
            inputsView.update()
        }
    }

}
