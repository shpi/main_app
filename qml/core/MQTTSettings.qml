import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    color: "transparent"



    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 10

          Rectangle {
            id: title
            width: parent.width
            height: 50
            color: "transparent"

            Text {
                padding: 10
                id: inputtitle
                width: parent.width
                text: '<b>MQTT Client</b>'
                font.pixelSize: 32
                color: Colors.black
            }
        }

        Column {
            anchors.top: title.bottom
            width: parent.width * 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            id: list
            spacing: 20





            TextField {
            anchors.right: parent.right
            onActiveFocusChanged: keyboard(this)
            width: 400
            font.pixelSize: 32
            text: mqttclient.path
            onEditingFinished: mqttclient.path = text

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "MQTT Client Path"
             }

             }



        TextField {
            anchors.right: parent.right
            onActiveFocusChanged: keyboard(this)
            width: 400
            font.pixelSize: 32
            text: mqttclient.host
            onEditingFinished: mqttclient.host = text

            Label {
                anchors.right: parent.left
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "Server"
             }

             }


        TextField {
            anchors.right: parent.right
            onActiveFocusChanged: keyboard(this)
            width: 400
            font.pixelSize: 32
            text: mqttclient.port
            onEditingFinished: mqttclient.port = text

            Label {
                
                anchors.right: parent.left
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                color: Colors.black
                text: "Port"
             }

             }





         
                Text {


                    wrapMode: Text.WordWrap
                    width: 300
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    color: Colors.black
                    text: 'Client enabled'

                    
               CheckBox {

                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.right
                
                Component.onCompleted: this.checked = mqttclient.enabled

                onCheckStateChanged: {
                    mqttclient.enabled = this.checked ? 1 : 0
                }
            }
}

                }
            }

}
