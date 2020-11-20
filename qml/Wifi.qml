import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    anchors.fill: parent

Column{
    anchors.fill:parent

    Text {
    id: inputtitle
    width: parent.width
    text: 'Available WifiNetworks'
    font.pointSize: 12
    }

       ListView {

            height: parent.height - inputtitle.height
            width:parent.width
            clip: true
            orientation: Qt.Vertical
            id: inputsview

            model: wifi.networks
            delegate: inputDelegate

            Component {
                id: inputDelegate

                Rectangle {
                    property int delindex: index
                    id: wrapper
                    height: 60
                    width: inputsview.width
                    color: index % 2 === 0 ? "lightgrey" : "white"
                    Row {

                        spacing: 10
                        height: parent.height

                         Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: '<b>' + ssid + '</b> ' + flags + ',  ' + frequency
                            font.pointSize: 8

                        }

                         ProgressBar {
                             id: wifiStrength
                             anchors.verticalCenter: parent.verticalCenter
                             from: 0
                             to: 100
                             value: signal

                             padding: 2

                             background: Rectangle {
                                 implicitWidth: 200
                                 implicitHeight: 20
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
                                         color: "#17a81a"
                                     }
                                 }
                         }

                         TextField {
                         anchors.verticalCenter: parent.verticalCenter
                         visible: false
                         font.pointSize: 8
                         placeholderText: 'password please'
                         onEditingFinished: inputs.set(path,this.text)


                         }

                    }
                }
            }
        }


}
}
