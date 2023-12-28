import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    property bool isInstanceActive: modules.loaded_instances['Connections']
                                   && modules.loaded_instances['Connections']['BT_MJ_HT_V1']
                                   && 'Instance' in modules.loaded_instances['Connections']['BT_MJ_HT_V1']

    Flickable {
        anchors.fill: parent
        contentHeight: btcolumn.implicitHeight

        Column {
            id: btcolumn
            anchors.fill: parent
            spacing: 20
            padding: 10

            Text {
                text: "Bluetooth Xiaomi MJ HT Sensors"
                color: Colors.black
                font.bold: true
                padding: 10
                font.pixelSize: 32
            }

            CheckBox {
                anchors.leftMargin: 20
                id: instanceRadioButton
                height: subtext.height + 10

                Text {
                    id: subtext
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 40
                    color: Colors.black
                    text: "Instance enabled"
                    wrapMode: Text.WordWrap
                    
                }

                Component.onCompleted: checked = isInstanceActive

                onCheckedChanged: {
                    if (!checked) {
                        modules.remove_instance('Connections', 'BT_MJ_HT_V1', 'Instance');
                    } else {
                        modules.add_instance('Connections', 'BT_MJ_HT_V1', 'Instance')
                    }
                }
            }

            RoundButton {
                padding: 5
                radius: 20
                width: 500
                text: 'Scan sensors'
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 50
                onClicked: modules.loaded_instances['Connections']['BT_MJ_HT_V1']['Instance'].scan_devices()

                Text {
                    text: Icons.arrow
                    rotation: 270
                    font.family: localFont.name
                    anchors.right: parent.right
                    anchors.rightMargin: 30
                    anchors.verticalCenter: parent.verticalCenter
                    font.pixelSize: 50
                }
            }

            Repeater {
                model: isInstanceActive ?  Object.keys(modules.loaded_instances['Connections']['BT_MJ_HT_V1']['Instance'].discovered_devices) : []
                delegate: Text {
                    visible: isInstanceActive
                    text: modelData + ": " + modules.loaded_instances['Connections']['BT_MJ_HT_V1']['Instance'].discovered_devices[modelData]
                }
            }
        }
    }
}
