import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.folderlistmodel 2.15
import QtGraphicalEffects 1.15
import QtQuick.Particles 2.15


//import "../fonts"
import "qrc:/fonts"

ApplicationWindow {
    id: window
    title: "SHPI"
    width: 800
    height: 480
    visible: true
    font.family: localFont.name

    property int minsize: width < height ? width: height

    function keyboard(object) {
        keyboardLoader.item.textfield = object
        if (object.activeFocus === true) {
            keyboardPopup.open()
        } 

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
        folder: "file://" + applicationDirPath + "/backgrounds/"
        nameFilters: ["*.png", "*.jpg"]

        onCountChanged: {
        if (folderModel.count > 0) {
        bg.source = folderModel.get(i, "fileURL")
        }

        }




    }






    Image {
        anchors.fill: parent
        id: bg
        fillMode: Image.Stretch
        visible: appearance.night === 0
                 || appearance.background_night > 0 ? true : false

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
    
        source: ""






    }

    FontLoader {
        id: localFont
        source: "../fonts/dejavu-custom.ttf"
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
            color: appearance.night ? "#222222" : Colors.white
            opacity: 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 10
            height: subrct.height + 10
            anchors.top: parent.top
            radius: 20
            anchors.topMargin: 5

            Rectangle {
                id: subrct
                height: mainsettingsView.height < closebutton.height ? closebutton.height : mainsettingsView.height
                anchors.top: parent.top
                anchors.topMargin: 5
                width: parent.width - 10
                anchors.left: parent.left
                anchors.rightMargin: 5
                anchors.leftMargin: 5
                color: "transparent"


            Flow {

                id: mainsettingsView
                width: parent.width - closebutton.width - 5
                anchors.right: parent.right

                spacing: 10

                layoutDirection: Qt.RightToLeft

                Repeater {
                    model: mainsettingsModel
                    delegate: mainsettingsDelegate
                }

            }

            RoundButton {
                id: closebutton
                font.family: localFont.name
                text: settingsstackView.depth > 1 ? Icons.arrow : settingsstackView.depth
                                                    > 0 ? Icons.close : Icons.arrow
                rotation: settingsstackView.depth == 0 ? 180 : 90
                width: height
                palette.button: settingsstackView.depth > 0 ? "darkred" : "#11000000"
                palette.buttonText: settingsstackView.depth > 0 ? "white" : Colors.black
                
                //Behavior on height { PropertyAnimation {}  }

                height: settingsstackView.depth > 0 ? 100: 150
                font.pixelSize: height * 0.8



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
                    size: 0.33
                    page: "core/LoggingSettings.qml"
                }
                ListElement {
                    title: "\uE00C" // Icons.sun
                    size: 1
                    page: "core/AppearanceSettings.qml"
                }
                ListElement {
                    title: "\uE016" // Icons.wifi
                    size: 1
                    page: "core/WifiSettings.qml"
                }
                ListElement {
                    title: "\uE046" // Icons.speaker
                    size: 1
                    page: "hardware/AlsaSettings.qml"
                }

                ListElement {
                    title: "\uE045" // Icons.reset
                    size: 1
                    page: "core/GitSettings.qml"
                }

                ListElement {
                    title: "\uE010" // Icons.settings
                    size: 1
                    page: "Settings.qml"
                }
            }

            Component {
                id: mainsettingsDelegate
                RoundButton {
                    property int butwidth: parent.width / mainsettingsModel.count - parent.spacing
                    //anchors.verticalCenter: parent.verticalCenter

                    //Behavior on height { PropertyAnimation {}  }


                    font.family: localFont.name
                    height: settingsstackView.depth > 0 ? butwidth : 1.9 * butwidth
                    font.pixelSize: size * height * 0.8
                    text: title
                    onClicked: {
                        if (page == "hardware/AlsaSettings.qml") {inputs.set_searchlist('sound');}
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

/*        Loader {
            asynchronous: true
            id: charging
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "Charging.qml"
        }

  */      Loader {
            asynchronous: true
            id: screensaver
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "screensaver/Screensaver.qml"
        }



Repeater {
    id: thermostatrepeater
    model: modules.modules['Logic']['Thermostat'].length > 0 ? 1 : 0

    delegate: Loader {
        asynchronous: true
        id: thermostatslide
        property bool _isCurrentItem: SwipeView.isCurrentItem
        source: "thermostat/Thermostat.qml"

    }
}

Repeater {
    id: weatherrepeater
    model: modules.modules['Info']['Weather'].length > 0 ? 1 : 0

    delegate: Loader {
        asynchronous: true
        id: weatherslide
        property bool _isCurrentItem: SwipeView.isCurrentItem
        source: "weather/WeatherFull.qml"
        visible: parent.visible
    }
}


        Loader {
            property SwipeView swipeView: view
            asynchronous: true
            id: fingerpaint
            property bool _isCurrentItem: SwipeView.isCurrentItem
            source: "fingerpaint.qml"
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
        function onJump() {
                console.log("jump state fired")
                if (view.interactive == true) {
                view.currentIndex = 1
                graphPopup.close()
                graphLoader.sensorpath = ''
                graphLoader.divider = 0
            }
        }
    }

    Timer {

        interval: 30000
        repeat: true
        running: (appearance.backlightlevel > 0) //to make ui more fluent
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

        Colors.night = appearance.night



    }

    Popup {

        enter: Transition {

            NumberAnimation {property: "opacity"; from: 0.0; to: 1.0}

        }

        exit: Transition {

            NumberAnimation {property: "opacity"; from: 1.0; to: 0.0}

        }

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

        enter: Transition {

            NumberAnimation {property: "opacity"; from: 0.0; to: 1.0}

        }

        exit: Transition {

            NumberAnimation {property: "opacity"; from: 1.0; to: 0.0}

        }

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
