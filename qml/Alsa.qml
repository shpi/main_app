import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    anchors.fill: parent

Column{
    anchors.fill:parent


    Text {
        id:audioheader
    padding: 10
    text: "Audio Settings"
    color: "white"
    font.bold: true

    }


       ListView {

            height: parent.height - audioheader.height
            width:parent.width
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
                    height: 60

                    width: inputsview.width
                    color: index % 2 === 0 ? "darkgrey" : "transparent"
                    Row {
                        spacing: 10
                        height: parent.height
                        anchors.right: parent.right
                        anchors.rightMargin: 10

                         Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: description + ' '
                            font.pointSize: 8
                            color: "white"

                        }

                         //(output === '1' ? '' : value)

                         Loader {
                             anchors.verticalCenter: parent.verticalCenter

                                      sourceComponent: if (output === '0') switch(type) {
                                         case "percent_int": return gaugebar
                                         default: return plaintext
                                     } else return undefined

                            Component {
                                id: plaintext
                                      Text {
                                         anchors.verticalCenter: parent.verticalCenter
                                         text: sensorvalue
                                         font.pointSize: 8
                                         color: "white"

                                     }
                            }

                            Component {
                                id: gaugebar
                                      Rectangle {
                                         anchors.verticalCenter: parent.verticalCenter
                                         width: 300
                                         height: 30
                                         color: "darkgrey"
                                         border.color: "white"



                                     Rectangle {
                                     anchors.verticalCenter: parent.verticalCenter
                                     height: parent.height - 2
                                     anchors.left: parent.left
                                     anchors.leftMargin: 1
                                     width: ((parent.width - 2) / 100) * sensorvalue
                                     color: Qt.rgba(1,0.5,0,0.7)
                                     }


                                     Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: sensorvalue + '%'
                                        font.pointSize: 8
                                        color: "white"

                                    }


                                     }
                            }

                         }




                         Loader {
                             anchors.verticalCenter: parent.verticalCenter

                                      sourceComponent: if (output === '1') switch(type) {
                                         case "boolean": return boolswitch
                                         case "enum": return enumcombo
                                         case "integer": return intslider
                                         default: return textfield
                                     } else return undefined

                         Component {
                         id: textfield

                         TextField {
                         anchors.verticalCenter: parent.verticalCenter
                         //visible: output == '1' ? 1 : 0
                         font.pointSize: 8
                         width: 300
                         color: "white"
                         placeholderText: (output == '1' ? value.toString() : '')
                         onEditingFinished: inputs.set(path,this.text)
                         }
                         }

                         Component {
                         id: boolswitch
                         Switch {
                         checked: sensorvalue === 1 ? true : false
                         anchors.verticalCenter: parent.verticalCenter
                         //visible: output == '1' ? 1 : 0
                         width: 300
                         onToggled: inputs.set(path, this.checked === true ? 1 : 0)
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
                             onCurrentIndexChanged: inputs.set(path, this.currentIndex)


                         }

                         }

                         Component {
                         id: intslider
                         Slider {
                             from: inputs.data[path]['min']
                             value:  sensorvalue
                             width: 300
                             to: inputs.data[path]['max']
                             stepSize:inputs.data[path]['step'] === 0 ? 1 : inputs.data[path]['step']
                             onMoved: inputs.set(path, this.value)
                         }}

                    }
                }
            }
        }


}
}
}