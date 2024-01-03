import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    ListView {
        cacheBuffer: 20
        anchors.fill: parent
        clip: true
        orientation: Qt.Vertical
        id: inputsview

        model: inputs.searchList
        delegate: inputDelegate

        header: Rectangle {
            width: parent.width
            height: 70
            color: "transparent"

            Text {
                id: title
                width: parent.width
                text: 'Audio Settings'
                font.bold: true
                font.pixelSize: 32
                color: Colors.black
                anchors.left: parent.left
                height: 70
                padding: 10
            }
        }

        Component {
            id: inputDelegate

            Rectangle {
                property int delindex: index

                id: wrapper
                height: 110
                width: inputsview.width
                color: index % 2 === 0 ? Colors.white : "transparent"

                Row {
                    spacing: 10
                    width: parent.width
                    height: parent.height

                    Text {
                        horizontalAlignment: Text.AlignHCenter
                        anchors.verticalCenter: parent.verticalCenter
                        text: description + ' '
                        font.pixelSize: 24
                        color: Colors.black
                        wrapMode: Text.WordWrap
                        width: parent.width - 220
                    }

                    Loader {
                        anchors.verticalCenter: parent.verticalCenter
                        asynchronous: true
                        sourceComponent: 

        if (output === false) {
            switch (type) {
                case "percent_int": return gaugebar;
                case "percent_float": return gaugebar;
                default: return plaintext;
            }
        } else {
            switch (type) {
                case "boolean": return boolswitch;
                case "thread": return boolswitch;
                case "enum": return enumcombo;
                case "integer": return intslider;
                default: return textfield;
            }
        }
    


                          Component {
                                id: plaintext

                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: value
                                    width: 200
                                    font.pixelSize: 24
                                    color: Colors.black
                                }
                            }

                            Component {
                                id: gaugebar

                                Rectangle {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 200
                                    height: 30
                                    color: "darkgrey"
                                    border.color: Colors.black

                                    Rectangle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        height: parent.height - 2
                                        anchors.left: parent.left
                                        anchors.leftMargin: 1
                                        width: ((parent.width - 2) / 100) * value
                                        color: Qt.rgba(1, 0.5, 0, 0.7)
                                    }

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: value + '%'
                                        font.pixelSize: 24
                                        color: Colors.black
                                    }
                                }
                            }
                        


                            Component {
                                id: textfield

                                TextField {
                                    onActiveFocusChanged: keyboard(this)
                                    anchors.verticalCenter: parent.verticalCenter
                                    font.pixelSize: 24
                                    width: 200
                                    color: Colors.black
                                    placeholderText: (output == '1' ? value.toString(
                                                                          ) : '')
                                    onEditingFinished: inputs.set(path, this.text)
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

                                    checked: value === 1 ? true : false
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 200
                                    onToggled: inputs.set(
                                                   path,
                                                   this.checked === true ? 1 : 0)
                                }
                            }

                            Component {
                                id: enumcombo

                                ComboBox {
                                    currentIndex: parseInt(value)
                                    width: 200
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    model: available
                                    onActivated: inputs.set(path,
                                                            this.currentIndex)
                                }
                            }

                            Component {
                                id: intslider

                                Slider {
                                    from: min
                                    value: value
                                    width: 200
                                    to: max
                                    stepSize: step === 0 ? 1 : step
                                    onPressedChanged: if (!this.pressed)
                                                          inputs.set(path,this.value)
                                }
                            }












                    }
                }
            }
        }
    }




}
