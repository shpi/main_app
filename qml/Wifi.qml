import QtQuick 2.12
import QtQuick.Controls 2.12


import "../fonts/"


Item {
    anchors.fill: parent



    ComboBox {

        id: actualDevice
        anchors.top: parent.top
        anchors.right: parent.right
        width: 200
        model: wifi.devices
        visible: (wifi.devices.length) > 1 ? true : false
    }


    Text {

        anchors.horizontalCenter: parent.horizontalCenter

    text: actualDevice.currentText != '' ? wifi.wpa_status(wifi.devices[actualDevice.currentIndex]) : ''

    }


Column{
    padding: 5
    anchors.fill:parent

    RoundButton {

    padding: 5
    radius: 10
    text: 'SCAN'
    font.pointSize: 20
    onClicked: { busy.running = true
                 wifi.scan_wifi(actualDevice.currentText)

               }
    }



    Text {
    id: inputtitle
    width: parent.width
    text: 'Available Wifi Networks:'
    font.pointSize: 12
    }

       ListView {
            property int selectednetwork: -1
            height: parent.height - inputtitle.height
            width:parent.width
            clip: true
            orientation: Qt.Vertical
            id: inputsview
            onModelChanged: {busy.running = false
                             inputsview.selectednetwork = -1}

            model: wifi.networks

            delegate: inputDelegate

            Component {
                id: inputDelegate

                Rectangle {
                    property int delindex: index
                    id: wrapper

                    height: inputsview.selectednetwork == index ? 160 : 60
                    width: inputsview.width
                    color: index % 2 === 0 ? "lightgrey" : "white"

                    Row {

                        spacing: 10
                        leftPadding: 10
                        height: 60


                        ProgressBar {
                            id: wifiStrength
                            anchors.verticalCenter: parent.verticalCenter
                            from: 0
                            to: 100
                            value: signal

                            padding: 2

                            background: Rectangle {
                                implicitWidth: 100
                                implicitHeight: 20
                                color: "#e6e6e6"
                                radius: 3
                            }
                            contentItem: Item {
                                    implicitWidth: 100
                                    implicitHeight: 16

                                    Rectangle {
                                        width: wifiStrength.visualPosition * parent.width
                                        height: parent.height
                                        radius: 2
                                        color: Qt.rgba((1 - (signal/100)), (signal/100), 0, 1)
                                    }
                                }
                        }


                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: '<b>' + ssid + '</b> ,  ' + frequency
                            font.pointSize: 9

                        }

                        RoundButton {
                        anchors.verticalCenter: parent.verticalCenter
                        width: height
                        text: flags ? Icons.locked : Icons.unlocked
                        font.pointSize: 10
                        font.family: localFont.name
                        palette.buttonText: flags != 'OPEN'  ?  "green" : "red"

                        }
}
                        Row {
                            width: parent.width
                            height: 100
                            padding: 10
                            spacing: 10
                            anchors.bottom: parent.bottom
                            visible: inputsview.selectednetwork == index ? true : false
                            id: wifiform

                            Column {

                                anchors.verticalCenter: parent.verticalCenter

                                height: parent.height

                         TextField {
                         id: wifipasswd
                         width: 300
                         font.pointSize: 10
                         placeholderText: 'password please'
                         text: password != '' ? password : ''


                         }

                         CheckBox {

                                id: bssidcheck
                                checked: false
                                text: qsTr("only this MAC")
                            }
                        }

                         RoundButton {
                             anchors.verticalCenter: parent.verticalCenter
                             text: "Connect"
                             font.pointSize: 15
                             radius: 10
                             onClicked: wifi.write_settings(actualDevice.currentText,flags,bssid,ssid,wifipasswd.text,bssidcheck.checked)
                         }
}


                    MouseArea {         enabled: inputsview.selectednetwork != index ? true : false
                                        anchors.fill: parent
                                        onClicked: {inputsview.currentIndex = index
                                                    inputsview.selectednetwork = index
                                        }}

                }


            }
        }


}
BusyIndicator {
    width: parent.width/3
    height: width

    anchors.centerIn: parent
    id: busy
    running: true
}
}
