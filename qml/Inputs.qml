import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    anchors.fill: parent

Column{
    anchors.fill:parent

    Text {
    id: inputtitle
    width: parent.width
    text: 'Available Inputs'
    font.pointSize: 12
    }

       ListView {

            height: parent.height - inputtitle.height
            width:parent.width
            clip: true
            orientation: Qt.Vertical
            id: inputsview

            model: inputs.inputList
            delegate: inputDelegate

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
                            text: '<b>' + path + '</b> ' + description + ', ' + type + ': ' + value
                            font.pointSize: 8

                        }

                    }
                }
            }
        }


}
}
