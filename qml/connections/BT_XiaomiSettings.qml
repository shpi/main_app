import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {
    id: root
    property bool isInstanceActive: modules.loaded_instances['Connections']
                                   && modules.loaded_instances['Connections']['BT_Xiaomi']
                                   && 'Instance' in modules.loaded_instances['Connections']['BT_Xiaomi']
    property int selectedDevice: -1
    property bool isScanning: false

    Flickable {
        id: flickable
        anchors.fill: parent
        contentHeight: btcolumn.implicitHeight

        Column {
            id: btcolumn
            width: parent.width
            spacing: 20
            padding: 10

            Text {
                text: "Bluetooth Xiaomi Sensors"
                color: Colors.black
                font.bold: true
                padding: 10
                font.pixelSize: 32
            }

           Row {
           spacing: 10

            CheckBox {
                id: instanceRadioButton
                height: subtext.height + 10

                Component.onCompleted: checked = isInstanceActive

                onCheckedChanged: {
                    if (!checked) {
                        modules.remove_instance('Connections', 'BT_Xiaomi', 'Instance');
                    } else {
                        modules.add_instance('Connections', 'BT_Xiaomi', 'Instance')
                    }
                }
            } 

                    Text {
                    id: subtext
                    width: 300
                    color: Colors.black
                    text: "Instance enabled"
                    wrapMode: Text.WordWrap
                }



            RoundButton {
                padding: 5
                radius: 20
                width: 300
                text: 'Scan sensors'
                font.pixelSize: 24
                onClicked: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].scan_devices()

                id: scanButton
                enabled: isInstanceActive && !modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].scanning

                Text {
                    text: Icons.arrow
                    rotation: 270
                    font.family: localFont.name
                    anchors.right: parent.right
                    anchors.rightMargin: 30
                    anchors.verticalCenter: parent.verticalCenter
                    font.pixelSize: 32
                }
            }

}


            ListView {
                id: devicesList
                width: parent.width
                 interactive: false
                height: 60 * devicesList.count + 110  // Adjust this height as needed
                clip: true
                orientation: Qt.Vertical
                model: Object.keys(modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices)

                delegate: Rectangle {
                    id: wrapper
                    height: root.selectedDevice == index ? 170 : 60
                    width: devicesList.width
                    border.color: "green"
                    border.width: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['selected'] == 1 ? 1 : 0

                    color: index % 2 === 0 ? "transparent" : Colors.white

                    Column {
                        spacing: 10

                        Row {
                            
                            spacing: 10
                            height: 60

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: modelData
                                font.pixelSize: 24
                                color: Colors.black
                                width: 250
                            }


                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                visible:   modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['selected'] !== 1

                                    text: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData].name !== undefined ? 
          modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['name'] : "(unknown)"

                                font.pixelSize: 24
                                color: Colors.black
                                width: 350
                                wrapMode: Text.WordWrap
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                visible:   modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['selected'] == 1
                                text: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['custom_name'] !== "" ?
          modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['custom_name'] : "(unknown)"

                                font.pixelSize: 24
                                color: Colors.black
                                width: 340
                                wrapMode: Text.WordWrap
                            }

                        
Text {
    anchors.verticalCenter: parent.verticalCenter
    text: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['rssi']
    font.pixelSize: 24
    color: {
        var rssi = modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['rssi'];
        if (rssi >= -60) {
            return "darkgreen"; // Stronger connection
        } else if (rssi >= -67) {
            return "green"; // Strong connection
        } else if (rssi >= -75) {
            return "yellow"; // Weak connection
        } else if (rssi >= -85) {
            return "orange"; // Unusable connection
        } else {
            return "red"; // Default color or for unknown RSSI values
        }
    }
    width: 50
    wrapMode: Text.WordWrap
}


 Text {
                    text: Icons.settings
                    color: Colors.black
                    width: 20
                    font.family: localFont.name
                    anchors.verticalCenter: parent.verticalCenter
                    font.pixelSize: 48
                    visible: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['type'] != 'unknown'
                   
                }






                            // Additional info or icons can go here
                        }

                        // This row will be visible when the item is selected
                        Row {
                            width: parent.width
                            height: 70
                            padding: 10
                            spacing: 10
                            visible: root.selectedDevice == index



                                TextField {
                    id: sensorName
                    text: ""
                    font.pixelSize: 32
                    height: 50
                    width: 500
                    placeholderText: 'Add name'
                    visible: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['selected'] !== 1
                    onActiveFocusChanged: keyboard(this)
                    

    }

    Button {
        id: submitButton
        text: "Add Sensor"
        visible: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['selected'] !== 1 

        onClicked: {
            modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].add_sensor(modelData,sensorName.text)
            sensorName.text = "" // Clear the input field after sending the data
        }
    }


    Button {
        id: deleteButton
        text: "Remove Sensor"
        visible: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['selected'] == 1

        onClicked: {
            modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].delete_sensor(modelData)
            sensorName.text = "" // Clear the input field after sending the data
        }
    }



                            // Additional controls or info can go here
                        }
                    }

                    MouseArea {
                     enabled:  modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices[modelData]['type'] != 'unknown' && root.selectedDevice != index 
                        anchors.fill: parent
                        onClicked: {
                            devicesList.currentIndex = index
                            root.selectedDevice = index
                        }
                    }
                }
            }
        }
    }


    Connections {
        target: modules.loaded_instances['Connections']['BT_Xiaomi']['Instance']

        function onDevicesScanned() {
            devicesList.model = Object.keys(modules.loaded_instances['Connections']['BT_Xiaomi']['Instance'].discovered_devices)
        }
    }
}
