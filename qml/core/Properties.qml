import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    ListView {
        id: property_listview

        height: parent.height
        width: parent.width
        //clip: true
        orientation: Qt.Vertical
        model: properties.get_sortfilter_model

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

        cacheBuffer: 50
        delegate: inputDelegate

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
                height: property_listview.currentIndex == index ? 150 : 80
                Behavior on height { PropertyAnimation {}  }
                width: property_listview.width
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
                        color: property_listview.currentIndex == index ? "green" : Colors.black
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
                        width: property_listview.width
                        property int plogging: logging
                        property int pexposed: exposed
                        property int pinterval: interval
                        property string ppath: path
                        active: property_listview.currentIndex == index
                        asynchronous: true
                        sourceComponent:  expandedDelegate
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {property_listview.currentIndex = index}
                    enabled: property_listview.currentIndex != index ? true : false
                }
            }
        }
    }
}
