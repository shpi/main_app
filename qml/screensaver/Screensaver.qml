import QtQuick 2.15

import "qrc:/fonts"

Item {

     signal refreshRoomInstances (string roomName)



    Rectangle {

        color: "transparent"
        anchors.fill: parent
        anchors.leftMargin: 5
        anchors.rightMargin: 5
        anchors.topMargin: 5
        anchors.bottomMargin: 5

        Text {
            id: moving_text
            x: 0
            y: 0
            text: Qt.formatDateTime(new Date(), "HH:mm") //"yyMMdd")
            color: Colors.black
            font.pixelSize: 90

            Text {
                id: moving_subtext
                anchors.top: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatDateTime(new Date(),
                                        "dddd, dd.MM.yy") //"yyMMdd")
                color: Colors.black
                font.pixelSize: 24
            }
        }



            Flow {

                id: screensaverflow
                spacing: 20
                anchors.bottom: parent.bottom

                property int rowCount: window.width / (150 + spacing)
                property int rowWidth: rowCount * 150 + (rowCount - 1) * spacing
                property int mar: (window.width - rowWidth) / 2

                anchors.right: parent.right
                width: parent.width - mar



                Repeater {
                    id: screensaverRow
                    model: modules.rooms['Home']


                       Connections {
                      target: modules // Replace 'someObject' with the object emitting the signal
                      
                      function onRefreshRoomInstances(roomname) {

                                  console.log('Refresh room instances from ' + roomname);
                                  screensaverRow.model = [];
                                  screensaverRow.model = modules.rooms[roomname];
    } }


                    Rectangle {

                        property var model: modelData.split('/')

                        border.width: 1
                        border.color: Colors.white
                        color: "transparent"
                        width: 150
                        height: 160
                        radius: 10

                        Loader {
                            id: componentLoader
                            source: '../' + model[0].toLowerCase() + "/" + model[1] + ".qml"
                            anchors.fill: parent
                            asynchronous: true
                            property var instancename: model[2]
                            property var iconview: true
                        }
                    }
                }
            }
        }


    Timer {
        property bool direction: true
        property int speed: 3
        interval: 20000
        repeat: true
        running: parent.parent._isCurrentItem
        onTriggered: {

            //moving_text.opacity = 0
            moving_text.x = Math.random() * Math.floor(
                        parent.width - moving_text.width)
            moving_text.y = 50 + Math.random() * Math.floor(
                        (parent.height - 250 - moving_text.height))

            moving_text.text = Qt.formatDateTime(new Date(),
                                                 "HH:mm") //"yyMMdd")
            moving_subtext.text = Qt.formatDateTime(
                        new Date(), "dddd, dd.MM.yy") //"yyMMdd")
        }
    }


}
