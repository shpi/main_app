import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {

    id: root

    property string device

    ListView {
        property int selectednetwork: -1
        height: parent.height
        width: parent.width
        clip: true
        //cacheBuffer: 100
        orientation: Qt.Vertical
        id: inputsview
        onModelChanged: {
            busy.running = false
            inputsview.selectednetwork = -1
        }

        model: wifi.networks



        delegate: inputDelegate

        Component {
            id: inputDelegate

            Rectangle {
                property int delindex: index
                id: wrapper

                height: inputsview.selectednetwork == index ? 170 : 60
                width: inputsview.width
                color: index % 2 === 0 ? "transparent" : Colors.white
                Column {
                    spacing: 10

                    Row {
                        leftPadding: 10
                        spacing: 10
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
                                    color: Qt.rgba((1 - (signal / 100)),
                                                   (signal / 100), 0, 1)
                                }
                            }
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: '<b>' + ssid + '</b> ,  ' + frequency + ' (' + bssid + ')'
                            font.pixelSize: 24
                            color: Colors.black
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            width: height
                            text: flags ? Icons.locked : Icons.unlocked
                            font.pixelSize: 32
                            font.family: localFont.name
                            color: flags != 'OPEN' ? "green" : "red"
                        }
                    }
                    Row {
                        width: parent.width
                        height: 70
                        padding: 10
                        spacing: 10

                        visible: inputsview.selectednetwork == index ? true : false
                        id: wifiform

                        TextField {
                            onActiveFocusChanged: keyboard(this)
                            id: wifipasswd
                            width: 300
                            font.pixelSize: 32
                            placeholderText: 'password please'
                            text: password != '' ? password : ''
                        }

                        CheckBox {

                            id: bssidcheck
                            checked: false
                            text: qsTr("only this BSSID")

                            contentItem: Text {
                                text: parent.text
                                color: Colors.black
                                leftPadding: parent.indicator.width + parent.spacing
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        RoundButton {
                            visible: inputsview.selectednetwork == index ? true : false

                            text: "connect"
                            font.pixelSize: 32
                            radius: 10
                            onClicked: {
                                settingsstackView.pop()
                                inputsview.selectednetwork = -1
                                wifi.write_settings(root.device, flags, bssid,
                                                    ssid, wifipasswd.text,
                                                    bssidcheck.checked)
                            }
                        }
                    }
                }

                MouseArea {
                    enabled: inputsview.selectednetwork != index ? true : false
                    anchors.fill: parent
                    onClicked: {
                        inputsview.currentIndex = index
                        inputsview.selectednetwork = index
                    }
                }
            }
        }
    }

    BusyIndicator {
            width: parent.width / 3
            height: width

            palette.dark: "#1E90FF"
            anchors.centerIn: parent
            id: busy
            running: true
        }
}
