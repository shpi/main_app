import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.VirtualKeyboard 2.1
import QtQuick.Window 2.15

import "../fonts/"

ApplicationWindow {
    id: window
    title: qsTr("SHPI")
    width: 800
    height: 480
    visible: true

    FontLoader {
        id: localFont
        source: "../fonts/orkney-custom.ttf"
    }

    Drawer {
        property string actual_setting
        id: drawer
        width: window.width
        height: parent.height
        edge: Qt.TopEdge
        position: 0
        visible: true
        interactive: settingsloader.source == "" ? true : false

        background: Rectangle {
            color: "transparent"
        }

        Rectangle {
            id: drawerheader
            color: Qt.rgba(0,0,0)

            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 20
            height: row.height + 20
            anchors.top: parent.top
            radius: 20
            anchors.topMargin: 5

            RoundButton {
                anchors.verticalCenter: parent.verticalCenter
                font.family: localFont.name
            text: Icons.close
            width: height
            palette {
                    button: "darkred"
                    buttonText: "white"
                }
            anchors.left: drawerheader.left
            anchors.leftMargin: 10
            font.pointSize: settingsloader.source != "" ? 20 : 30
            onClicked: {
                drawer.actual_setting = ''
                settingsloader.source = ""}
            visible: settingsloader.source != "" ? true : false

            }

            Row {
                id: row
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 10

                spacing: 10



                RoundButton {
                    font.family: localFont.name
                    font.pointSize:  settingsloader.source != "" ? 20 : 30
                    text: Icons.sun
                    width: height
                    onClicked: {
                        drawer.actual_setting = 'Backlight.qml'
                        settingsloader.source = 'Backlight.qml'}
                    palette.button: drawer.actual_setting === 'Backlight.qml' ? "green" : 'white'



                }

                RoundButton {
                    font.family: localFont.name
                    font.pointSize: settingsloader.source != "" ? 20 : 30
                    text: Icons.wifi
                    width: height
                    onClicked: {
                        drawer.actual_setting = 'Wifi.qml'
                        settingsloader.setSource("Wifi.qml") }
                    palette.button: drawer.actual_setting == 'Wifi.qml' ? "green" : 'white'

                }

                RoundButton {
                    font.family: localFont.name
                    font.pointSize: settingsloader.source != "" ? 20 : 30
                    text: Icons.speaker
                    onClicked: {
                        drawer.actual_setting = 'Alsa.qml'
                        inputs.set_searchList('alsa')
                        settingsloader.setSource("Alsa.qml")}
                    palette.button: drawer.actual_setting == 'Alsa.qml' ? "green" : 'white'

                    width: height
                }

                RoundButton {
                    font.family: localFont.name
                    font.pointSize: settingsloader.source != "" ? 20 : 30
                    text: Icons.reset
                    width: height
                }

                RoundButton {
                    font.family: localFont.name
                    font.pointSize: settingsloader.source != "" ? 20 : 30
                    text: Icons.settings
                    width: height
                }

            }
        }




            Rectangle {
            color: Qt.rgba(0,0,0,0.5)
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 20
            height: settingsloader.source != "" ? (window.height - drawerheader.height - 20) : 0
            clip: true

                Loader {
                    id: settingsloader
                    anchors.fill: parent



            }

            anchors.top: drawerheader.bottom
            radius: 20
            anchors.topMargin: 5

        }


    }

    SwipeView {
        id: view

        currentIndex: 2
        anchors.fill: parent
        anchors.bottom: inputPanel.top


        Loader {
            id: inputSlide
            source: "Inputs.qml"
        }

        Loader {
            id: shutter
            source: "shutter/Shutter.qml"
        }

        Loader {
            id: screensaver
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "screensaver/Screensaver.qml"
        }

        Loader {
            id: thermostat
            source: "thermostat/Thermostat.qml"
        }

        Loader {
            id: weatherslide
            source: "weather/Weather.qml"
        }
    }

    PageIndicator {
        id: indicator
        count: view.count
        currentIndex: view.currentIndex
        anchors.bottom: view.bottom
        anchors.horizontalCenter: parent.horizontalCenter
    }

    InputPanel {
        id: inputPanel
        y: Qt.inputMethod.visible ? parent.height - inputPanel.height : parent.height
        anchors.left: parent.left
        anchors.right: parent.right

        Rectangle {
        visible: Qt.inputMethod.visible
        anchors.bottom: parent.top
        width: parent.width
        height: 50
        color: 'black'
        Text {
                   anchors.verticalCenter: parent.verticalCenter
        anchors.top: parent.top
        padding: 2
        anchors.left: parent.left
        anchors.leftMargin: this.width > parent.width ? parent.width - this.width : 5
        color: 'white'
        text:   InputContext.surroundingText
        font.pointSize: 15
        }
        }
    }

    Text {

        anchors.bottom: view.bottom
        anchors.right: view.right

        anchors.rightMargin: 30
        font.family: localFont.name
        font.pointSize: 50
        text: Icons.logo
        color: "white"
        visible: drawer.visible
    }


    Rectangle {
       id: backlighthelper
       anchors.fill:parent
       color: Qt.rgba(0,0,0,appearance.blackfilter)


    }


Connections {
target: appearance

onJumpHome: view.currentIndex = 2


}

Component.onCompleted: {

  /*  for (let [key, value] of Object.entries(inputs.data)) {
      if (key.toString().startsWith('alsa'))   { console.log(`${key}: ${value}`);

       for (let [subkey, subvalue] of Object.entries(value)) {
            console.log(`${subkey}: ${subvalue}`);

       } }

      }
    }

*/}

}


