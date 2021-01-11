import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {

    Component.onCompleted: inputs.set_searchList('alsa')

    Column {
        anchors.fill: parent

        Text {
            id: audioheader
            padding: 10
            text: "Audio Settings"
            color: Colors.black
            font.bold: true
        }

        ListView {

            height: parent.height - audioheader.height
            width: parent.width
            clip: true
            orientation: Qt.Vertical
            id: inputsview

            model: inputs.searchList
            delegate: inputDelegate

            Component {
                id: inputDelegate

                Rectangle {
                    property int delindex: index
                    property int sensorvalue: value
                    id: wrapper
                    height: 70

                    width: inputsview.width
                    color: index % 2 === 0 ? Colors.white : "transparent"
                    Row {
                        spacing: 10
                        height: parent.height
                        anchors.right: parent.right
                        anchors.rightMargin: 10

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: description + ' '
                            font.pixelSize: 24
                            color: Colors.black
                        }

                        //(output === '1' ? '' : value)
                        Loader {
                            anchors.verticalCenter: parent.verticalCenter

                            sourceComponent: if (output === '0')
                                                 switch (type) {
                                                 case "percent_int":
                                                     return gaugebar
                                                 default:
                                                     return plaintext
                                                 }
                                             else
                                                 return undefined

                            Component {
                                id: plaintext
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: sensorvalue
                                    font.pixelSize: 24
                                    color: Colors.black
                                }
                            }

                            Component {
                                id: gaugebar
                                Rectangle {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 300
                                    height: 30
                                    color: "darkgrey"
                                    border.color: Colors.black

                                    Rectangle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        height: parent.height - 2
                                        anchors.left: parent.left
                                        anchors.leftMargin: 1
                                        width: ((parent.width - 2) / 100) * sensorvalue
                                        color: Qt.rgba(1, 0.5, 0, 0.7)
                                    }

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: sensorvalue + '%'
                                        font.pixelSize: 24
                                        color: Colors.black
                                    }
                                }
                            }
                        }

                        Loader {
                            anchors.verticalCenter: parent.verticalCenter

                            sourceComponent: if (output === '1')
                                                 switch (type) {
                                                 case "boolean":
                                                     return boolswitch
                                                 case "enum":
                                                     return enumcombo
                                                 case "integer":
                                                     return intslider
                                                 default:
                                                     return textfield
                                                 }
                                             else
                                                 return undefined

                            Component {
                                id: textfield

                                TextField {
                                    anchors.verticalCenter: parent.verticalCenter
                                    //visible: output == '1' ? 1 : 0
                                    font.pixelSize: 24
                                    width: 300
                                    color: Colors.black
                                    placeholderText: (output == '1' ? value.toString(
                                                                          ) : '')
                                    onEditingFinished: inputs.set(path,
                                                                  this.text)
                                }
                            }

                            Component {
                                id: boolswitch
                                Switch {

                                    id: switchcontrol
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    indicator: Rectangle {
                                        anchors.horizontalCenter: parent.horizontalCenter

                                        anchors.verticalCenter: switchcontrol.verticalCenter
                                        implicitWidth: 96
                                        implicitHeight: 26
                                        x: parent.leftPadding
                                        y: parent.height / 2 - height / 2
                                        radius: 26
                                        color: parent.checked ? "#17a81a" : "#cccccc"
                                        border.color: parent.checked ? "#17a81a" : "#cccccc"

                                        Rectangle {

                                            anchors.verticalCenter: parent.verticalCenter
                                            x: switchcontrol.checked ? parent.width - width : 0
                                            width: 35
                                            height: 35
                                            radius: 17
                                            color: switchcontrol.down ? "#cccccc" : "#ffffff"
                                            border.color: switchcontrol.checked ? (switchcontrol.down ? "#17a81a" : "#21be2b") : "#999999"
                                        }
                                    }

                                    checked: sensorvalue === 1 ? true : false
                                    anchors.verticalCenter: parent.verticalCenter
                                    //visible: output == '1' ? 1 : 0
                                    width: 300
                                    onToggled: inputs.set(
                                                   path,
                                                   this.checked === true ? 1 : 0)
                                }
                            }

                            Component {
                                id: enumcombo
                                ComboBox {
                                    currentIndex: parseInt(value)
                                    //visible: output == '1' ? 1 : 0
                                    width: 300
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    model: inputs.data[path]['available']
                                    onActivated: inputs.set(path,
                                                            this.currentIndex)
                                }
                            }

                            Component {
                                id: intslider
                                Slider {
                                    from: inputs.data[path]['min']
                                    value: sensorvalue
                                    width: 300
                                    to: inputs.data[path]['max']
                                    stepSize: inputs.data[path]['step']
                                              === 0 ? 1 : inputs.data[path]['step']
                                    onMoved: inputs.set(path, this.value)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
