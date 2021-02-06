import QtQuick 2.12

import "../../fonts/"

Item {

    Rectangle {

        color: "transparent"
        anchors.fill: parent

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

        Rectangle {

            width: parent.width
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20
            height: 130
            color: "transparent"

            Row {

                height: parent.height
                spacing: 30
                anchors.horizontalCenter: parent.horizontalCenter


                Repeater {
                    id: screensaverRow
                    model: modules.rooms['Screensaver']
                    height: parent.height


                    Rectangle {

                        property var model: modelData.split('/')

                        border.width: 1
                        border.color: Colors.white
                        color: "transparent"
                        height: parent.height
                        width: 100
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

    Connections {
                id: screensaverconn
                target: modules

                function onRoomsChanged() {


                    console.log(modules.rooms['Screensaver'])

                }

}}
