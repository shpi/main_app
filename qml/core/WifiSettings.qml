import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 100


        Text {
            padding: 10
            id: title
            width: parent.width
            text: 'Wifi Status'
            font.bold: true
            font.pixelSize: 32
            color: Colors.black
            anchors.left: parent.left
            height: 70

        }

         Item {
             anchors.right: parent.right
             anchors.top: parent.top
             width: 220
             height: 60

            ComboBox {
                id: actualDevice
                anchors.centerIn:parent
                width: 200
                height: 40
                model: wifi.devices
                font.pixelSize:32
                onPressedChanged: wifi.wpa_status(actualDevice.currentText)

            }
            }



    Column {
        spacing: 20
        padding: 10
        id:list
        anchors.top: title.bottom
        width: parent.width * 0.9


        Row {

            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter


            ProgressBar {
                id: wifiStrength
                anchors.verticalCenter: parent.verticalCenter
                from: 0
                to: 100
                value: wifi.signal

                padding: 2

                background: Rectangle {
                    implicitWidth: 200
                    implicitHeight: 30
                    color: "#e6e6e6"
                    radius: 3
                }
                contentItem: Item {
                    implicitWidth: 200
                    implicitHeight: 16

                    Rectangle {
                        width: wifiStrength.visualPosition * parent.width
                        height: parent.height
                        radius: 2
                        color: Qt.rgba((1 - (wifi.signal / 100)),
                                       (wifi.signal / 100), 0, 1)
                    }

                    Text {
                    anchors.centerIn: parent
                    font.pixelSize: 24
                    text: 'Signal ' +  wifi.signal + '%'
                    color: Colors.black
                    }

                }



            }
        }



       Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 20

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: 'WPA state:'
                font.family: localFont.name
                font.pixelSize: 24
                color: Colors.black
            }
            Text {
                width: 200
                text: wifi.wpa_state
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }
} 


        Row {
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter


            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: 'IP:'
                font.family: localFont.name
                font.pixelSize: 24
                color: Colors.black
            }
            Text {
                width: 200
                text: wifi.wpa_ip
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 20

            Text {

                text: 'SSID:'
                font.family: localFont.name
                font.pixelSize: 24
                color: Colors.black
            }
            Text {
                width: 200
                text: wifi.wpa_ssid
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }

}
/*        Row {
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter

            Text {

                text: 'BSSID:'
                font.family: localFont.name
                font.pixelSize: 24
                color: Colors.black
            }
            Text {
                width: 200
                text:  wifi.wpa_bssid
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            }
        }
*/
        RoundButton {

            padding: 5
            radius: 20
            width: 500
            text: 'scan networks'
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 50
            onClicked: {
                wifi.scan_wifi(actualDevice.currentText)

                settingsstackView.push(   Qt.resolvedUrl('WifiSettingsList.qml'), {
                                                       "device": actualDevice.currentText
                                                   })

            }

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
    }
}}
