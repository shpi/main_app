import QtQuick 2.12

import QtGraphicalEffects 1.12

import "../fonts/"

Item {

    anchors.fill: parent

    Item {
        id: clock
        width: 300
        height: 300
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenterOffset: -60

        property int hours
        property int minutes
        property int seconds

        function timeChanged() {
            var date = new Date
            hours = date.getHours()
            minutes = date.getMinutes()
            seconds = date.getSeconds()
        }

        Timer {
            interval: 1000
            running: true
            repeat: true
            onTriggered: clock.timeChanged()
        }

        Rectangle {
            id: clockRect
            layer.enabled: true
            layer.smooth: true
            anchors.fill: parent
            radius: height / 2
            color: "#22ffffff"
            border.color: Colors.black
            border.width: 1

            Repeater {

                model: 12

                Rectangle {
                    anchors.bottom: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    height: parent.height / 2.2
                    width: 5
                    color: "transparent"
                    transformOrigin: Item.Bottom
                    rotation: index * 30

                    Rectangle {

                        width: parent.width
                        anchors.top: parent.top
                        anchors.topMargin: 15
                        height: 20
                        opacity: 0.7
                        color: Colors.black
                    }

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter

                        text: index !== 0 ? index : '12'
                        anchors.top: parent.top
                        anchors.topMargin: -17
                        color: Colors.black
                    }
                }
            }

            Rectangle {
                anchors.bottom: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                height: parent.height / 3.5
                width: 10
                color: Colors.black
                transformOrigin: Item.Bottom
                radius: width / 2
                rotation: (clock.hours * 30) + (clock.minutes * 0.5)
            }

            Rectangle {
                anchors.bottom: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                height: parent.height / 2.5
                width: 6
                color: Colors.black
                transformOrigin: Item.Bottom
                radius: width / 2
                rotation: clock.minutes * 6
            }

            Rectangle {
                anchors.bottom: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                height: parent.height / 2
                width: 3
                color: Colors.black
                transformOrigin: Item.Bottom
                rotation: clock.seconds * 6
                radius: width / 2


                /* Behavior on rotation {
                                SpringAnimation { spring: 2; damping: 0.2; modulus: 360 }
                            }
            */
                Rectangle {

                    color: "red"
                    height: 10

                    width: parent.width
                    anchors.top: parent.top
                }
            }

            Rectangle {

                height: 15
                width: 15
                radius: 7.5
                color: 'red'
                anchors.centerIn: parent
            }

            Rectangle {
                id: _mask
                anchors.fill: parent
                color: "transparent"
                visible: true
                Rectangle {
                    anchors.centerIn: parent
                    width: clock.height * 0.7
                    height: clock.height * 0.7
                    radius: height / 2
                    color: "black"
                }

                layer.enabled: true
                layer.samplerName: "maskSource"
                layer.effect: ShaderEffect {
                    property variant source: clockRect
                    fragmentShader: "
varying highp vec2 qt_TexCoord0;
uniform highp float qt_Opacity;
uniform lowp sampler2D source;
uniform lowp sampler2D maskSource;
void main(void) {
gl_FragColor = texture2D(source, qt_TexCoord0.st) * (1.0-texture2D(maskSource, qt_TexCoord0.st).a) * qt_Opacity;
}
"
                }
            }
        }
    }

    Rectangle {

        width: parent.width
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
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

                component = Qt.createComponent(module[0].toLowerCase(
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

            component = Qt.createComponent(module[0].toLowerCase(
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
