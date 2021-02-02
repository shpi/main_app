import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.VirtualKeyboard 2.1
import Qt.labs.folderlistmodel 2.12
import QtGraphicalEffects 1.12

import "../fonts/"

ApplicationWindow {
    id: window
    title: qsTr("SHPI")
    width: 800
    height: 480
    visible: true
    font.family: localFont.name


    function keyboard(object) {
       if (object.activeFocus === true) {
       keyboardLoader.item.textfield = object
       keyboardPopup.open() }

    }

    function getIndex(path, mmodel) {
        for (var i = 0; i < mmodel.rowCount(); i++) {
            var idx = mmodel.index(i, 0)
            var value = mmodel.data(idx, Qt.UserRole + 1000)
            if (path === value) {
                return i
            }
        }
        return 0
    }

    background: Rectangle {
        color: Colors.white
    }

    property int i: 0

    FolderListModel {
        caseSensitive: false
        id: folderModel
        folder: "../backgrounds/"
        nameFilters: ["*.png", "*.jpg"]
        onCountChanged: {
            if (folderModel.count > 0)
                bg.source = folderModel.get(i, "fileURL")
        }
    }

    Image {
        anchors.fill: parent
        id: bg
        source: ""
        fillMode: Image.Stretch
        visible: appearance.night === 0 || appearance.background_night > 0 ? true : false

        RadialGradient {
            angle: 30
            horizontalOffset: 0
            verticalOffset: 0
            horizontalRadius: parent.height
            verticalRadius: parent.height

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

            id: mask
            anchors.fill: parent
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
        source: "../fonts/orkney-custom.ttf"
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



       /* InputPanel {
            id: inputPanel
            z: 99
            y: Qt.inputMethod.visible ? parent.height - inputPanel.height : parent.height
            anchors.left: parent.left
            anchors.right: parent.right
            visible: Qt.inputMethod.visible

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
                    font.pixelSize: 45
                }
            }
        }
       */



        Rectangle {

            id: drawerheader
            color: appearance.night ? "#222222" : Colors.white
            opacity: 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 20
            height: mainsettingsView.height
            anchors.top: parent.top
            radius: 20
            anchors.topMargin: 5

            ListView {
                spacing: 10
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
                font.pixelSize: settingsstackView.depth > 0 ? 50 : 75
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
                    page: "core/AppearanceSettings.qml"
                }
                ListElement {
                    title: "\uE016" // Icons.wifi
                    size: 50
                    page: "hardware/WifiSettings.qml"
                }
                ListElement {
                    title: "\uE046" // Icons.speaker
                    size: 50
                    page: "hardware/AlsaSettings.qml"
                }


                ListElement {
                    title: "\uE010" // Icons.settings
                    size: 50
                    page: "Settings.qml"
                }
            }

            Component {
                id: mainsettingsDelegate
                RoundButton {
                    anchors.verticalCenter: parent.verticalCenter
                    font.family: localFont.name
                    height:  settingsstackView.depth > 0 ? 80 : 110
                    font.pixelSize: settingsstackView.depth > 0 ?  size : size * 1.5
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
            color: appearance.night ? "#222222" : Colors.white
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
        //anchors.bottom: inputPanel.top




        Loader {
            asynchronous: true
            id: rooms
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "Rooms.qml"
        }

        Loader {
            asynchronous: true
            id: screensaver
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "screensaver/Screensaver.qml"
        }



        Repeater {

            id: thermostatrepeater
            model: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0
            visible: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0

            delegate: Loader {
                asynchronous: true
                id: thermostatslide
                source: "thermostat/Thermostat.qml"
                visible: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0
                active: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0

            }
        }

        Repeater {

            id: weatherrepeater
            model: modules.modules['Info']['Weather'].length > 0 ? 1 : 0
            visible: modules.modules['Info']['Weather'].length > 0 ? 1 : 0

            delegate: Loader {
                asynchronous: true
                id: weatherslide
                source: "weather/WeatherFull.qml"
                visible: modules.modules['Info']['Weather'].length > 0 ? 1 : 0
                 active: modules.modules['Info']['Weather'].length > 0 ? 1 : 0
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


    Rectangle {
        id: backlighthelper
        visible: false
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, appearance.blackfilter)
    }

    Connections {
        target: appearance
        function onJumpHome() {
            view.currentIndex = 1
        }
    }

    Timer {

        interval: 20000
        repeat: true
        running: appearance.jump_state > 0 //to make ui more fluent
        onTriggered: {

            mask.angle = Math.random() * 180

            mask.verticalOffset = -mask.height / 4 + (Math.random(
                                                          ) * mask.height) / 2
            mask.horizontalOffset = -mask.width / 4 + (Math.random(
                                                           ) * mask.width) / 2

            if (appearance.night === 0 || appearance.background_night > 0) {
                if (Math.random() > 0.7)
                    bg.source = folderModel.get(Math.random() * Math.floor(
                                                    folderModel.count),
                                                "fileURL")
            }
        }
    }

    Component.onCompleted: {
        //console.log('count of weater instances : ' + modules.modules['Info']['Weather'].length)
        Colors.night = appearance.night



        /*  for (let [key, value] of Object.entries(inputs.data)) {
      if (key.toString().startsWith('alsa'))   { console.log(`${key}: ${value}`);

       for (let [subkey, subvalue] of Object.entries(value)) {
            console.log(`${subkey}: ${subvalue}`);

       } }

      }
    }

*/ }




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
            onClicked:  {graphPopup.close()
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
            source: "keyboard/Keyboard.qml"

        }



    }






}
