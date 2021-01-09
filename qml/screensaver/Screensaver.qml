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
            font.pointSize: 40

            Text {
                id: moving_subtext
                anchors.top: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatDateTime(new Date(),
                                        "dddd, dd.MM.yy") //"yyMMdd")
                color: Colors.black
                font.pointSize: 10
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
                id: screensaverRow
            }
        }

        Connections {
            id: screensaverconn
            target: modules

            onRoomsChanged: {

                var is

                for (i = screensaverRow.children.length; i > 0; i--) {

                    screensaverRow.children[i - 1].destroy()
                }

                var component

                for (var i = 0; i < modules.rooms['Screensaver'].length; i++) {

                    var module
                    module = modules.rooms['Screensaver'][i].split('/')

                    component = Qt.createComponent(
                                "../" + module[0].toLowerCase(
                                    ) + "/" + module[1] + ".qml")

                    if (component.status !== Component.Ready) {
                        if (component.status === Component.Error)
                            console.log("Error:" + component.errorString())
                    }

                    component.createObject(screensaverRow, {
                                               "width": "100",
                                               "name": module[2]
                                           })
                }
            }
        }

        Component.onCompleted: {

            var component
            var i

            for (i = screensaverRow.children.length; i > 0; i--) {

                screensaverRow.children[i - 1].destroy()
            }

            for (i = 0; i < modules.rooms['Screensaver'].length; i++) {

                var module
                module = modules.rooms['Screensaver'][i].split('/')

                component = Qt.createComponent("../" + module[0].toLowerCase(
                                                   ) + "/" + module[1] + ".qml")

                if (component.status !== Component.Ready) {
                    if (component.status === Component.Error)
                        console.log("Error:" + component.errorString())
                }

                component.createObject(screensaverRow, {
                                           "width": "100",
                                           "name": module[2]
                                       })
            }
        }
    }

    Timer {
        property bool direction: true
        property int speed: 3
        interval: 10000
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
