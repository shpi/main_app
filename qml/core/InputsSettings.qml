import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {


       ListView {


           header: Rectangle {

                 width: parent.width
                 height:50
                 color: "transparent"


                 Text {
                 padding: 10
                 id: inputtitle
                 width: parent.width
                 text: '<b>Available Variables</b>'
                 font.pointSize: 12
                 color: Colors.black
                 }
               }



            height: parent.height
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
                       font.pointSize: 11
                       color: Colors.black
                   }

                    Column {
                        padding: 5
                        spacing: 10
                        height: parent.height

                         Text {

                            text: '<b>' + path + '</b> ' // + description + ', ' + type + ': ' + (output == '1' ? '' : value)
                            font.pointSize: 10
                            color: inputsview.currentIndex == index ? "green" :  Colors.black

                        }



                         Text {

                            text: description + ' (' + type + ')'
                            font.pointSize: 9
                            color: Colors.black

                        }


                         Row {

                             visible: inputsview.currentIndex == index ? true : false
                             spacing: 150
                             CheckBox {
                                     checked: true

                                      Text {text: "logging"
                                           color: Colors.black
                                           anchors.left: parent.right
                                           anchors.leftMargin: 15

                                           }

                                 }

                             CheckBox {
                                     checked: true

                                      Text {text: "exposed"
                                           color: Colors.black
                                           anchors.left: parent.right
                                           anchors.leftMargin: 15
                                           }
                                 }

                             SpinBox {
                                 id:spinbox
                                 visible: interval > 0 ? true : false
                                 value: interval
                                 stepSize: 5
                                  Text {text: "Interval"
                                     color: Colors.black
                                     anchors.left: parent.right
                                     anchors.leftMargin: 15
                                     }
                                 //onValueChanged: weather[0].interval =  this.value
                                 from: 1
                                 to: 600
                                 font.pointSize: 9


                                 contentItem: TextInput {
                                       z: 2
                                       text: spinbox.textFromValue(spinbox.value, spinbox.locale) + 's'
                                       color: "#000"
                                       selectionColor: "#000"
                                       selectedTextColor: "#ffffff"
                                       horizontalAlignment: Qt.AlignHCenter
                                       verticalAlignment: Qt.AlignVCenter
                                       readOnly: !spinbox.editable
                                       validator: spinbox.validator
                                       inputMethodHints: Qt.ImhFormattedNumbersOnly
                                   }



                                 }

                         }





                         /* TextField {
                         anchors.verticalCenter: parent.verticalCenter
                         visible: output == '1' ? 1 : 0
                         font.pointSize: 8
                         placeholderText: (output == '1' ? value.toString() : '')
                         onEditingFinished: inputs.set(path,this.text)
                         }
                         */
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

