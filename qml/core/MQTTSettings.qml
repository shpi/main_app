import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    color: "transparent"

    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 100



            Text {
                id: title
                width: parent.width
                text: 'MQTT Client'
                font.bold: true
                font.pixelSize: 32
                color: Colors.black
                anchors.left: parent.left
                height: 70
                padding: 10
            }




        Column {
            anchors.top: title.bottom
            width: parent.width * 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            id: list
            spacing: 20
            padding: 10

            Flow {
                width: parent.width
                height: implicitHeight

                Text {
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    //anchors.verticalCenter: parent.width < 500 ? undefined : pathtextfield.verticalCenter
                    text: "MQTT MainPath"
                    font.pixelSize: 24
                    color: Colors.black
                    wrapMode: Text.WordWrap
                    width: parent.width < 500 ? parent.width : parent.width * 0.3
                    height: 50
                }

                TextField {
                    id: pathtextfield
                    onActiveFocusChanged: keyboard(this)
                    width: parent.width < 500 ? parent.width : parent.width * 0.7
                    height: 50
                    font.pixelSize: 32
                    text: mqttclient.path
                    onEditingFinished: mqttclient.path = text

                }
            }

            Flow {
                width: parent.width
                height: implicitHeight

                Text {
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    //anchors.verticalCenter: parent.width < 500 ? undefined : pathtextfield.verticalCenter
                    text: "Server"
                    font.pixelSize: 24
                    color: Colors.black
                    wrapMode: Text.WordWrap
                    width: parent.width < 500 ? parent.width : parent.width * 0.3
                    height: 50
                }

                TextField {


                    onActiveFocusChanged: keyboard(this)
                    height: 50
                    width: parent.width < 500 ? parent.width : parent.width * 0.7
                    font.pixelSize: 32
                    text: mqttclient.host
                    onEditingFinished: mqttclient.host = text
                }
            }

            Flow {
                width: parent.width
                height: implicitHeight

                Text {
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    //anchors.verticalCenter: parent.width < 500 ? undefined : pathtextfield.verticalCenter
                    text: "Port"
                    font.pixelSize: 24
                    color: Colors.black
                    wrapMode: Text.WordWrap
                    width: parent.width < 500 ? parent.width : parent.width * 0.3
                    height: 50
                }

                TextField {
                    height: 50

                    onActiveFocusChanged: keyboard(this)
                    width: parent.width < 500 ? parent.width : parent.width * 0.7
                    font.pixelSize: 32
                    text: mqttclient.port
                    onEditingFinished: mqttclient.port = text
                }
            }

            Flow {
                width: parent.width
                height: implicitHeight

                Text {
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    //anchors.verticalCenter: parent.width < 500 ? undefined : pathtextfield.verticalCenter
                    text: "Client enabled"
                    font.pixelSize: 24
                    color: Colors.black
                    wrapMode: Text.WordWrap
                    width: parent.width < 500 ? parent.width : parent.width * 0.3
                    height: 50
                }

                CheckBox {

                    width: parent.width < 500 ? parent.width : parent.width * 0.7
                    Component.onCompleted: this.checked = mqttclient.enabled

                    onCheckStateChanged: {
                        mqttclient.enabled = this.checked ? 1 : 0
                    }
                }
            }
        }
    }
}
