import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

Flickable {
    anchors.fill: parent
    contentHeight: inputsview_folder.height + inputsview.height

    ListView {
        interactive: false
        anchors.top: parent.top
        id: inputsview_folder
        width: parent.width
        model: inputs.folders
        height: (inputsview_folder.count * 80) + 70
        cacheBuffer: 100
        Component.onCompleted: inputs.set_path("")

        delegate: Item {
            width: parent.width
            height: 80

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
                onClicked: {
                    var newPath = inputs.currentPath !== "" ? inputs.currentPath + "/" : "";
                    newPath += modelData;
                    inputs.set_searchlist(newPath);
                    inputsview.height = inputsview.count * 100 + 150;
                    inputs.set_path(newPath);
                }
            }
        }

        header: Rectangle {
            width: parent.width
            height: 70
            color: "transparent"

            Text {
                padding: 10
                id: inputpath
                anchors.left: parent.left
                text: "/" + inputs.currentPath
                font.pixelSize: 30
                color: Colors.black
            }

            Text {
                padding: 10
                id: inputtitle
                anchors.right: parent.right
                text: "System Props"
                font.bold: true
                font.pixelSize: 32
                color: Colors.black
            }
        }
    }

    ListView {
        interactive: false
        id: inputsview
        anchors.top: inputsview_folder.bottom
        width: parent.width
        model: inputs.searchList
        visible: inputs.files.length > 0
        cacheBuffer: 100

        delegate: Rectangle {
            property var pvalue: value
            property int plogging: logging
            property int pexposed: exposed
            property int pinterval: interval
            property string ppath: path
            property int pmax: max !== undefined ? parseInt(max) : 100
            property int pmin: min !== undefined ? parseInt(min) : 0
            property int pstep: step !== undefined ? parseInt(step) : 1


            width: inputsview.width
            height: inputsview.currentIndex == index ? 200 : 100
            Behavior on height { PropertyAnimation {} }
            color: index % 2 === 1 ? Colors.white : "transparent"

            Rectangle {
            color: "transparent"
            anchors.right: parent.right
            anchors.top: parent.top
            width: 300
            height: 90
            
            Loader {
                anchors.centerIn: parent

                sourceComponent: {
                    if (output === false) {
                        switch (type) {
                            case "percent_int": return gaugebar;
                            case "percent_float": return gaugebar;
                            default: return rawtext;
                        }
                    } else {
                        switch (type) {
                            case "boolean": return boolswitch;
                            case "thread": return boolswitch;
                            case "enum": return rawtext; //enumcombo;
                            case "percent_int": return intslider;
                            case "percent_float": return intslider;
                            default: 
                                      if (min !== undefined && max !== undefined && step !== undefined)
                                      {return intslider}
                                      else  {return rawtext;}
                        }
                    }
                }

                // Components (enumcombo, intslider, boolswitch, gaugebar, rawtext)

            Component {
            id: rawtext
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                padding: 5
                text: pvalue
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
                width: ((parent.width - 2) / 100) * parseInt(pvalue)
                color: Qt.rgba(1, 0.5, 0, 0.7)
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                text: pvalue + '%'
                font.pixelSize: 24
                color: Colors.black
            }
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

                                    checked: parseInt(pvalue) == 1 ? true : false
                                    width: 200
                                    onToggled: inputs.set(path,this.checked === true ? 1 : 0)
                                }
                            }










            
                            Component {
                                id: intslider                         
                                Slider {
                                id: control
                                 anchors.centerIn: parent
                                width: 180

                                 Text {
                                 text: pmin
                                 anchors.right: parent.left
                                 color:Colors.black
                                 anchors.verticalCenter: parent.verticalCenter
                                 }

                               Text {
                                text: pmax
                                anchors.verticalCenter: parent.verticalCenter
                                color: Colors.black
                                anchors.left: parent.right
                                }



                                 background: Rectangle {
        x: control.leftPadding
        y: control.topPadding + control.availableHeight / 2 - height / 2
        implicitWidth: 180
        implicitHeight: 6
        width: control.availableWidth
        height: implicitHeight
        radius: 2
        color: "#bdbebf"

        Rectangle {
            width: control.visualPosition * parent.width
            height: parent.height
            color: "#21be2b"
            radius: 2
        }
    }

    handle: Rectangle {
        x: control.leftPadding + control.visualPosition * (control.availableWidth - width)
        y: control.topPadding + control.availableHeight / 2 - height / 2
        implicitWidth: 26
        implicitHeight: 26
        radius: 13
        color: control.pressed ? "#f0f0f0" : "#f6f6f6"
        border.color: "#bdbebf"
    }

                                    from: pmin
                                    value: parseInt(pvalue)
                                    to: pmax
                                    onMoved: inputs.set(path,this.value)




                                }
}
                            


            

            }
            }

            Column {
                padding: 10
                spacing: 10
                height: 150

                Text {
                    text: '<b>' + path + '</b>'
                    font.pixelSize: 24
                    color: inputsview.currentIndex == index ? "green" : Colors.black
                }

                Text {
                    text: description
                    font.pixelSize: 24
                    color: Colors.black
                }

                 Text {
                    text: 'Datatype: ' + type
                    font.pixelSize: 20
                    color: Colors.black
                    visible: inputsview.currentIndex == index
                }



                Rectangle {
                    height: 70
                    color: "transparent"
                    width: inputsview.width
                    visible: inputsview.currentIndex == index

                    Row {
                        anchors.fill: parent
                        spacing: 150

                        CheckBox {
                            checked: plogging
                            onClicked: inputs.set_logging(ppath, this.checked)
                            Text {
                                text: "logging"
                                color: Colors.black
                                anchors.left: parent.right
                                anchors.leftMargin: 15
                            }
                        }

                        CheckBox {
                            checked: pexposed
                            onClicked: inputs.set_exposed(ppath, this.checked)
                            Text {
                                text: "exposed"
                                color: Colors.black
                                anchors.left: parent.right
                                anchors.leftMargin: 15
                            }
                        }

                        SpinBox {
                            id: spinbox
                            visible: pinterval > 0
                            value: pinterval
                            stepSize: 5
                            onValueModified: inputs.set_interval(ppath, value)
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
                }

                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: inputsview.currentIndex = index
                    enabled: inputsview.currentIndex != index
                }
            }
        }
    }

}
