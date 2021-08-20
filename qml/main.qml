import QtQuick 2.15
import QtQuick.Controls 2.15
// import QtQuick.VirtualKeyboard 2.1
import Qt.labs.folderlistmodel 2.12
import QtGraphicalEffects 1.12

import "qrc:/fonts"

ApplicationWindow {
    id: window
    title: "SHPI"
    width: 800
    height: 480
    visible: true
    font.family: localFont.name

    function keyboard(object) {
        keyboardLoader.item.textfield = object
        if (object.activeFocus === true) {
            keyboardPopup.open()
        }
    }

    background: Rectangle {
        color: Colors.white
    }

    FolderListModel {
        id: folderModel
        // Component.onCompleted: console.error(applicationDirPath)

        caseSensitive: false
        folder: "file://" + applicationDirPath + "/backgrounds/"
        nameFilters: ["*.png", "*.jpg"]
        onCountChanged: {
            if (folderModel.count > 0)
                bg.source = folderModel.get(0, "fileURL") // i
        }
    }

    Image {
        id: bg
        anchors.fill: parent
        source: ""
        fillMode: Image.Stretch
        visible: appearance.night_active === false || appearance.background_night

        RadialGradient {
            id: mask
            angle: 30
            horizontalOffset: 0
            verticalOffset: 0
            horizontalRadius: parent.height
            verticalRadius: parent.height
            anchors.fill: parent

            Behavior on angle {
                PropertyAnimation {
                    duration: 1000
                }
            }

            Behavior on horizontalOffset {
                PropertyAnimation {
                    duration: 1000
                }
            }

            Behavior on verticalOffset {
                PropertyAnimation {
                    duration: 1000
                }
            }

            gradient: Gradient {
                GradientStop {
                    position: -0.10
                    color: "transparent"
                }
                GradientStop {
                    position: 0.6
                    color: Colors.white
                }
            }
        }
    }

    FontLoader {
        id: localFont
        source: "/fonts/dejavu-custom.ttf"
    }

    Drawer {
        property string actual_setting
        id: drawer
        dragMargin: 20
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
            color: appearance.night_active ? "#222222" : Colors.white
            opacity: 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 20
            height: mainsettingsView.height
            anchors.top: parent.top
            radius: 20
            anchors.topMargin: 5

            ListView {
                id: mainsettingsView
                spacing: 10
                height: settingsstackView.depth > 0 ? 85 : 130
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
                font.pixelSize: settingsstackView.depth > 0 ? 50 : 50
                onClicked: {
                    if (settingsstackView.depth === 0)
                        //drawer.position = 0.0
                        drawer.close()

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
                    title: "LOG" // Icons.sun
                    size: 20
                    page: "core/LoggingSettings.qml"
                }
                ListElement {
                    title: "\uE00C" // Icons.sun
                    size: 50
                    page: "/modules/Appearance.qml"
                }
                ListElement {
                    title: "\uE016" // Icons.wifi
                    size: 50
                    page: "core/WifiSettings.qml"
                }
                ListElement {
                    title: "\uE046" // Icons.speaker
                    size: 50
                    page: "hardware/AlsaSettings.qml"
                }

                ListElement {
                    title: "\uE045" // Icons.reset
                    size: 50
                    page: "core/GitSettings.qml"
                }

                ListElement {
                    title: "\uE010" // Icons.settings
                    size: 50
                    page: "/qml/settings/Settings.qml"
                }
            }

            Component {
                id: mainsettingsDelegate
                RoundButton {
                    anchors.verticalCenter: parent.verticalCenter
                    font.family: localFont.name
                    height: settingsstackView.depth > 0 ? 80 : 100
                    font.pixelSize: settingsstackView.depth > 0 ? size : size * 1.5
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
            color: appearance.night_active ? "#222222" : Colors.white
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

        Loader {
            id: categories
            asynchronous: true
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "/qml/CategoriesListView.qml"
        }

        Loader {
            id: mainscreen
            asynchronous: true
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "/qml/MainScreen.qml"
        }

        Repeater {
            id: slidesrepeater
            model: modules.slides
            // visible: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0

            Text {
                // anchors.fill: parent
                text: modelData
                color: Colors.black
                font.bold: true
                font.pixelSize: 40
            }

            /* Loader {
                asynchronous: true
                id: slide
                source: "thermostat/Thermostat.qml"
                // visible: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0
                // active: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0
            } */
        }
    }

    PageIndicator {
        id: indicator
        count: view.count
        currentIndex: view.currentIndex
        anchors.bottom: view.bottom
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Rectangle {
        id: backlighthelper
        visible: appearance.blackfilter > 0
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, appearance.blackfilter)
    }

    Connections {
        target: appearance
        function onJump_home() {
            view.currentIndex = 1
        }
    }

    Timer {
        interval: 30000
        repeat: true
        running: (view.currentIndex === 1
                  && appearance.backlightlevel > 0)  // to make ui more fluent

        onTriggered: {
            mask.angle = Math.random() * 180
            mask.verticalOffset = -mask.height / 4 + (Math.random(
                                                          ) * mask.height) / 2
            mask.horizontalOffset = -mask.width / 4 + (Math.random(
                                                           ) * mask.width) / 2

            if (!appearance.night_active || appearance.background_night) {
                // Set random background
                if (Math.random() > 0.7)
                    bg.source = folderModel.get(Math.random() * Math.floor(folderModel.count),
                                                "fileURL")
            }
        }
    }

    Popup {
        id: graphPopup
        width: parent.width
        height: parent.height
        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        padding: 0
        topInset: 0
        leftInset: 0
        rightInset: 0
        bottomInset: 0

        background: Rectangle {
            color: Colors.white
        }

        Loader {
            property string sensorpath: ''
            property real divider: 0
            property int interval: 0

            anchors.fill: parent
            id: graphLoader
            source: "Graph.qml"
        }

        RoundButton {
            opacity: 0.5
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.topMargin: 10
            anchors.leftMargin: 10
            width: height
            text: Icons.close
            palette.button: "darkred"
            palette.buttonText: "white"
            font.pixelSize: 50
            font.family: localFont.name
            onClicked: {
                graphPopup.close()
                graphLoader.sensorpath = ''
                graphLoader.divider = 0
            }
        }
    }

    Popup {
        id: keyboardPopup
        width: parent.width
        height: parent.height
        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        padding: 0
        topInset: 0
        leftInset: 0
        rightInset: 0
        bottomInset: 0

        background: Rectangle {
            color: Colors.white
        }

        Loader {
            id: keyboardLoader
            anchors.fill: parent
            source: "/qml/keyboard/Keyboard.qml"
        }
    }
}
