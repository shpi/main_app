import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.VirtualKeyboard 2.1

import "../fonts/"

ApplicationWindow {
    id: window
    title: qsTr("SHPI")
    width: 800
    height: 480
    visible: true

    background: Rectangle {
       color: Colors.white
    }

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
        visible: true
        interactive: settingsstackView.depth > 0 ? false : true
        Behavior on position {
            PropertyAnimation {}
        }
        background: Rectangle {
            color: "transparent"
        }

        Rectangle {

            id: drawerheader
            color: Colors.white
            opacity: 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 20
            height: mainsettingsView.height
            anchors.top: parent.top
            radius: 20
            anchors.topMargin: 5

            ListView {
                spacing: settingsstackView.depth > 0 ? 10 : 25
                height: settingsstackView.depth > 0 ? 85 : 130
                id: mainsettingsView
                orientation: ListView.Horizontal
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 15
                model: mainsettingsModel
                delegate: mainsettingsDelegate
                layoutDirection: ListView.RightToLeft
            }

            RoundButton {
                anchors.left: parent.left
                anchors.leftMargin: 5
                anchors.verticalCenter: parent.verticalCenter
                font.family: localFont.name
                //settingsstackView.depth > 0 ? true : false
                text: settingsstackView.depth > 1 ? Icons.arrow : settingsstackView.depth
                                                    > 0 ? Icons.close : Icons.arrow
                rotation: settingsstackView.depth == 0 ? 180 : 90
                width: height
                palette.button: settingsstackView.depth > 0 ? "darkred" : "#11000000"
                palette.buttonText: settingsstackView.depth > 0 ? "white" : Colors.black
                font.pointSize: settingsstackView.depth > 0 ? 20 : 30
                onClicked: {
                    if (settingsstackView.depth === 0)
                        drawer.position = 0

                    if (settingsstackView.depth == 1)
                        settingsstackView.clear()
                    else
                        settingsstackView.pop()

                    if (settingsstackView.depth === 0)
                        drawer.actual_setting = ''
                }
            }

            ListModel {
                id: mainsettingsModel
                ListElement {
                    title: "\uE00C" // Icons.sun
                    page: "core/AppearanceSettings.qml"
                }
                ListElement {
                    title: "\uE016" // Icons.wifi
                    page: "hardware/WifiSettings.qml"
                }
                ListElement {
                    title: "\uE046" // Icons.speaker
                    page: "hardware/AlsaSettings.qml"
                }

                ListElement {
                    title: "\uE045" // Icons.reset
                    page: "hardware/Reset.qml"
                }

                ListElement {
                    title: "\uE010" // Icons.settings
                    page: "Settings.qml"
                }
            }

            Component {
                id: mainsettingsDelegate
                RoundButton {
                    anchors.verticalCenter: parent.verticalCenter
                    font.family: localFont.name
                    font.pointSize: settingsstackView.depth > 0 ? 20 : 30
                    text: title
                    onClicked: {
                        settingsstackView.clear()
                        settingsstackView.push(Qt.resolvedUrl(page))
                        drawer.actual_setting = page
                    }
                    palette.button: drawer.actual_setting == page ? "#1E90FF" : 'lightgrey'
                    palette.buttonText: drawer.actual_setting == page ? "white" : "#555"
                    width: height
                }
            }
        }

        Rectangle {
            color: Colors.white
            opacity: 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 20
            height: window.height - drawerheader.height - 20
            visible: settingsstackView.depth > 0 ? true : false
            clip: true
            anchors.top: drawerheader.bottom
            radius: 20
            anchors.topMargin: 5

            StackView {
                id: settingsstackView
                anchors.fill: parent
                focus: true
            }
        }
    }

    SwipeView {
        id: view

        currentIndex: 1
        anchors.fill: parent
        anchors.bottom: inputPanel.top

        Loader {
            id: shutter
            source: "ui/Shutter.qml"
        }

        Loader {
            id: ticks
            source: "ui/Thermostat.qml"
        }


        Loader {
            id: colorwheel
            source: "ui/ColorWheel.qml"
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



Repeater {

            id: weatherrepeater
            model: modules.modules['Info']['Weather'].length > 0 ?  1 : 0

            onItemAdded: console.log(weatherrepeater.count)
            onItemRemoved:  console.log(weatherrepeater.count)

            delegate: Loader {
                id: weatherslide
                source: "weather/Weather.qml"
                visible: modules.modules['Info']['Weather'].length > 0 ?  1 : 0

            }
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
            color: Colors.white
            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.top: parent.top
                padding: 2
                anchors.left: parent.left
                anchors.leftMargin: this.width > parent.width ? parent.width - this.width : 5
                color: Colors.black
                text: InputContext.surroundingText
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
        color: Colors.white
        visible: drawer.position == 0 ? false : true
    }

    Rectangle {
        id: backlighthelper
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, appearance.blackfilter)
    }

    Connections {
        target: appearance
        onJumpHome: view.currentIndex = 1
    }

    Component.onCompleted: {

        console.log('count of weater instances : ' + modules.modules['Info']['Weather'].length)
        Colors.night = appearance.night

        /*  for (let [key, value] of Object.entries(inputs.data)) {
      if (key.toString().startsWith('alsa'))   { console.log(`${key}: ${value}`);

       for (let [subkey, subvalue] of Object.entries(value)) {
            console.log(`${subkey}: ${subvalue}`);

       } }

      }
    }

*/ }
}
