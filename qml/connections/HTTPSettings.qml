import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {
        property string instancename

    ListView {

        header: Rectangle {

            width: parent.width
            height: 50
            color: "transparent"

            Text {
                padding: 10
                id: inputtitle
                width: parent.width
                text: '<b>Available Variables</b>'
                font.pixelSize: 32
                color: Colors.black
            }
        }

        height: parent.height
        width: parent.width
        clip: true
        orientation: Qt.Vertical
        id: inputsview

        model: modules.loaded_instances['Connections']['HTTP'][instancename].inputList
        delegate: inputDelegate

        Component {
            id: inputDelegate

            Rectangle {
                property int delindex: index
                id: wrapper
                height: inputsview.currentIndex == index ? 150 : 80
                Behavior on height {
                    PropertyAnimation {}
                }
                width: inputsview.width
                color: index % 2 === 0 ? Colors.white : "transparent"

                Text {
                    padding: 5
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    text: value
                    font.pixelSize: 32
                    color: Colors.black
                }

                Column {
                    padding: 5
                    spacing: 10
                    height: parent.height

                    Text {

                        text: '<b>' + path + '</b> ' // + description + ', ' + type + ': ' + (output == '1' ? '' : value)
                        font.pixelSize: 24
                        color: inputsview.currentIndex == index ? "green" : Colors.black
                    }

                    Text {

                        text: description + ' (' + type + ')'
                        font.pixelSize: 24
                        color: Colors.black
                    }

                    Row {

                        visible: inputsview.currentIndex == index ? true : false
                        spacing: 150




                            Text {
                                text: "Interval: " + interval
                                color: Colors.black

                            }


                    }



                }

                MouseArea {

                    anchors.fill: parent
                    onClicked: inputsview.currentIndex = index
                    enabled: inputsview.currentIndex != index ? true : false
                }
            }
        }
    }
}
