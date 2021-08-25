import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    Rectangle {
        id: proptitle
        anchors.top: parent.top
        width: parent.width
        implicitHeight: proptitle_text.implicitHeight
        color: "transparent"

        Text {
            id: proptitle_text
            padding: 5
            width: parent.width
            text: '<b>Active Properties (Variables)</b>'
            font.pixelSize: 20
            color: Colors.black
        }
    }

    ListView {
        id: listview

        model: properties.get_property_navigator_model() //get_properties_model()
        delegate: listitem_delegate

        property var item_height_min: 40

        anchors.top: proptitle.bottom
        anchors.bottom: parent.bottom
        width: parent.width
        clip: true

        orientation: Qt.Vertical
        currentIndex: -1
        cacheBuffer: item_height_min * 4

        header: Rectangle {
            id: go_up_area
            width: parent.width
            height: listview.model.path != '' ? 30 : 0
            color: "transparent"
            //visible: listview.model.path != ''

            Text {
                padding: 10
                id: list_header_icon
                // width: parent.width
                text: '⮬'
                font.family: emoji.name
                font.pixelSize: 25
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                padding: 5
                id: list_header_text
                anchors.left: list_header_icon.right
                text: 'go up'
                font.pixelSize: listview.item_height_min - 3 * padding
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    listview.model.go_up()
                    listview.currentIndex = -1
                }
                // enabled: list_header_text.visible
            }
        }

        Component {
            id: listitem_delegate

            Rectangle {
                property var itemModel: model // read 'model' from the delegate's context
                id: wrapper
                height: listview.currentIndex == index ? listview.item_height_min + expand_loader.height : listview.item_height_min
                Behavior on height { PropertyAnimation {} }
                width: listview.width
                color: listview.currentIndex == index ? "lightsteelblue" : (index % 2 === 0 ? Colors.white : Colors.white2)

                Item {
                    id: title_row

                    width: parent.width
                    height: listview.item_height_min

                    Text {
                        // Icon
                        id: prop_icon
                        leftPadding: listview.model.path == '' || index == 0 ? 5 : 30
                        text: icon
                        font.family: emoji.name
                        font.pixelSize: listview.item_height_min - 10
                        color: Colors.black
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        // Property path
                        id: line_path
                        padding: 5
                        text: expand_loader.active ? "[" + io + "] " + path : (listview.model.path == '' || index == 0 ? path : key)
                        font.pixelSize: listview.item_height_min - 3 * padding
                        font.bold: expand_loader.active || (is_propertydict ? is_propertydict : false)
                        color: Colors.black
                        anchors.left: prop_icon.right
                        anchors.right: expand_loader.active ? line_value.left : undefined
                        anchors.verticalCenter: parent.verticalCenter
                        elide: Text.ElideRight
                    }

                    Text {
                        // Property value or iorole
                        id: line_value
                        horizontalAlignment: Text.AlignRight
                        padding: 5
                        text: is_propertydict ? value_len + " items" : (expand_loader.active ? "" : (cache_human ? cache_human : "<i>None</i>"))
                        visible: !expand_loader.active
                        font.pixelSize: listview.item_height_min - 3 * padding
                        font.bold: cache_human !== undefined
                        color: Colors.black
                        elide: expand_loader.active ? Text.ElideNone : Text.ElideLeft

                        anchors.left: expand_loader.active ? undefined : line_path.right
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        width: expand_loader.active ? implicitWidth : undefined
                    }
                }

                Loader {
                    id: expand_loader

                    anchors.top: title_row.bottom
                    width: listview.width

                    property var model: parent.itemModel // inject 'model' to the loaded item's context

                    active: listview.currentIndex == index
                    asynchronous: true
                    visible: status == Loader.Ready
                    sourceComponent: expanded_delegate
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        if (ptype == "PropertyDict") {
                            // Clicked on a Property containing a PropertyDict
                            listview.model.set_path(raw_property)
                            listview.currentIndex = -1
                        } else {
                            // Clicked on a property
                            listview.currentIndex = index
                        }
                    }
                    enabled: listview.currentIndex != index
                }
            }
        }

        Component {
            id: expanded_delegate

            Column {
                height: implicitHeight
                width: parent.width

                spacing: 2

                Text {
                    // Description, datatype
                    width: parent.width
                    padding: 5
                    text: "<i>" + model.description + "</i> (" + model.datatype + ")"
                    font.pixelSize: 20
                    color: Colors.black
                    wrapMode: Text.Wrap
                }

                Text {
                    // Property value, default
                    width: parent.width
                    padding: 5
                    text: "Value: <b>" + model.cache_human + "</b>" + (model.default_human === undefined ? "" : " Default: <b>" + model.default_human + "</b>")
                    font.pixelSize: 20
                    color: Colors.black
                    wrapMode: Text.Wrap
                }

                Row {
                    id: interval_settings
                    width: parent.width
                    height: implicitHeight

                    visible: model.is_function

                    Text {
                        text: "Automatic value read interval:"
                        color: Colors.black
                        padding: 5
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    RadioButton {
                        checked: model.interval === undefined
                        text: 'Disable'
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: { model.interval = undefined }
                    }

                    RadioButton {
                        checked: model.interval !== undefined
                        text: checked ? 'Enable:' : 'Enable'
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: { model.interval = model.interval_min }
                    }

                    SpinBox {
                        id: interval_spin
                        visible: model.interval !== undefined
                        value: model.interval ? model.interval : 0
                        anchors.verticalCenter: parent.verticalCenter
                        stepSize: 1

                        onValueModified: { model.interval = value }

                        from: model.interval_min ? model.interval_min : 0
                        to: 600
                        font.pixelSize: 32

                        contentItem: TextInput {
                            z: 2
                            text: parent.textFromValue(interval_spin.value, interval_spin.locale) + 's'
                            color: "#000"
                            selectionColor: "#000"
                            selectedTextColor: "#ffffff"
                            horizontalAlignment: Qt.AlignHCenter
                            verticalAlignment: Qt.AlignVCenter
                            readOnly: !parent.editable
                            validator: parent.validator
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                        }
                    }
                }

                CheckBox {
                    checked: false
                    //onClicked: inputs.set_logging(parent.parent.ppath, this.checked)

                    Text {
                        text: "bla1"
                        color: Colors.black
                        anchors.left: parent.right
                        anchors.leftMargin: 15
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                CheckBox {
                    checked: false
                    //onClicked: inputs.set_exposed(parent.parent.ppath, this.checked)
                    Text {
                        text: "bla2"
                        color: Colors.black
                        anchors.left: parent.right
                        anchors.leftMargin: 15
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                CheckBox {
                    checked: true
                    Text {
                        text: "bla3"
                        color: Colors.black
                        anchors.left: parent.right
                        anchors.leftMargin: 15
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }
    }
}
