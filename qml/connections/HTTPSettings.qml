import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {
        property string instancename

    ListView {

        header: Rectangle {

            width: parent.width
            height: 150
            color: "transparent"
            Column {
            Text {
                padding: 10
                id: inputtitle
                width: parent.width
                text: '<b>Available Variables</b>'
                font.pixelSize: 32
                color: Colors.black
            }

                Row {
                    Label {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "IP"
                        color: Colors.black
                    }

            TextField {
                id: ip_text
                width:450
                Component.onCompleted: ip_text.text = modules.loaded_instances['Connections']['HTTP'][instancename].ip
                onTextChanged: modules.loaded_instances['Connections']['HTTP'][instancename].ip
                               = ip_text.text


            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: ":"
                color: Colors.black
            }

            TextField {
                id: port_text

                width: 100
                Component.onCompleted: port_text.text = modules.loaded_instances['Connections']['HTTP'][instancename].port
                onTextChanged: modules.loaded_instances['Connections']['HTTP'][instancename].port
                               = parseInt(port_text.text)


            }

            RoundButton {

                text: 'Update'
                palette.button: "darkred"
                palette.buttonText: "white"
                font.pixelSize: 32
                font.family: localFont.name
                onClicked: {
                    modules.loaded_instances['Connections']['HTTP'][instancename].update_vars()

                }
                }

                }
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
                        spacing: 250


                        CheckBox {
                            checked: modules.loaded_instances['Connections']['HTTP'][instancename].vars.indexOf(path) !== -1 ? true : false
                            onClicked:
                            {

                                if (this.checked)  modules.loaded_instances['Connections']['HTTP'][instancename].add_var(path)
                                else modules.loaded_instances['Connections']['HTTP'][instancename].delete_var(path)
                            }
                            Text {
                                text: "make available"
                                color: Colors.black
                                anchors.left: parent.right
                                anchors.leftMargin: 15
                            }
                        }







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
