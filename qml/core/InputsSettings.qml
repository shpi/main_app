import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/fonts"

Item {
    Flickable {
        anchors.fill: parent
        contentHeight:  inputsview_folder.height + inputsview.height

            // First ListView (Folders)
            ListView {
                interactive: false
                anchors.top: parent.top
                id: inputsview_folder
                width: parent.width
                model: inputs.folders
                delegate: pathDelegate

                header: Rectangle {
                    width: parent.width
                    height: 70
                    color: "transparent"

                    Text {
                        padding: 10
                        id: inputpath
                        anchors.left: parent.left
                        width: implicitWidth
                        text: "/" + inputs.currentPath
                        font.pixelSize: 30
                        color: Colors.black
                    }

                    Text {
                        padding: 10
                        id: inputtitle
                        anchors.right: parent.right
                        width: implicitWidth
                        text: "System Vars"
                        font.bold: true
                        font.pixelSize: 32
                        color: Colors.black
                    }
                }

                height: (70 + (inputsview_folder.count  * 100))
                cacheBuffer: 100

                Component.onCompleted: {
                    inputs.set_path("");
                }
            }

            // Second ListView (Available Variables)
            ListView {
                interactive: false
                id: inputsview
                anchors.top: inputsview_folder.bottom
                width: parent.width
                model: inputs.searchList
                delegate: inputDelegate
                visible: inputs.files.length > 0
                height: (200 + (inputsview.count * 80))
                cacheBuffer: 100
            }
        }
    

    Component {
        id: fileDelegate

        Item {
            width: parent.width
            height: 60

            Rectangle {
                anchors.fill: parent
                color: index % 2 === 0 ? "transparent" : Colors.white
            }

            Text {
                color: Colors.black
                font.pixelSize: 24
                text: modelData
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 35
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 5
                height: 1
                color: "#424246"
            }
        }
    }


    Component {
        id: pathDelegate
        Item {
            width: parent.width
            height: 100
            Rectangle {
                anchors.fill: parent
                color: index % 2 === 0 ? "transparent" : Colors.white
            }
            Text {
                id: textitem
                color: Colors.black
                font.pixelSize: 32
                text: modelData
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 20
            }
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 5
                height: 1
                color: "#424246"
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 30
                text: Icons.arrow
                rotation: 270
                font.family: localFont.name
                color: Colors.black
            }
            MouseArea {
                id: mouse
                anchors.fill: parent
                onClicked: {   var newPath = "";

                               if (inputs.currentPath !== "") {
                               newPath = inputs.currentPath + "/";
                               }
                               newPath += modelData;

                               inputs.set_searchlist(newPath);
                               inputs.set_path(newPath);
                           }
            }
        }
    }






   Component {
        id: expandedDelegate



        Row {

            anchors.fill:parent
            spacing: 150
            CheckBox {
                checked: parent.parent.plogging
                onClicked: inputs.set_logging(parent.parent.ppath, this.checked)

                Text {
                    text: "logging"
                    color: Colors.black
                    anchors.left: parent.right
                    anchors.leftMargin: 15
                }
            }

            CheckBox {
                checked: parent.parent.pexposed
                onClicked: inputs.set_exposed(parent.parent.ppath, this.checked)
                Text {
                    text: "exposed"
                    color: Colors.black
                    anchors.left: parent.right
                    anchors.leftMargin: 15
                }
            }

            SpinBox {
                id: spinbox
                visible: parent.parent.pinterval > 0 ? true : false
                value: parent.parent.pinterval
                stepSize: 5

                onValueModified:  inputs.set_interval(parent.parent.ppath, value)
                Text {
                    text: "Interval"
                    color: Colors.black
                    anchors.left: parent.right
                    anchors.leftMargin: 15
                }

                from: 1
                to: 600
                font.pixelSize: 32

                contentItem: TextInput {
                    z: 2
                    text: spinbox.textFromValue(
                              spinbox.value, spinbox.locale) + 's'
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



        }



        Component {
            id: inputDelegate

            Rectangle {

                id: wrapper
                height: inputsview.currentIndex == index ? 150 : 80
                Behavior on height { PropertyAnimation {}  }
                width: inputsview.width
                color: index % 2 === 0 ? Colors.white : "transparent"


                Text {
                    padding: 5
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    text: value
                    font.pixelSize: 24
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



                    /* TextField {
                      onActiveFocusChanged: keyboard(this)
                         anchors.verticalCenter: parent.verticalCenter
                         visible: output == '1' ? 1 : 0
                         font.pixelSize: 24
                         placeholderText: (output == '1' ? value.toString() : '')
                         onEditingFinished: inputs.set(path,this.text)
                         }
                         */
                    Loader {
                    height: 70
                    width: inputsview.width
                    property int plogging: logging
                    property int pexposed: exposed
                    property int pinterval: interval
                    property string ppath: path
                    active: inputsview.currentIndex == index
                    asynchronous: true
                    sourceComponent:  expandedDelegate

                    }

                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {inputsview.currentIndex = index}
                    enabled: inputsview.currentIndex != index ? true : false
                }
            }
        }








    // Add other components or logic as needed
}
