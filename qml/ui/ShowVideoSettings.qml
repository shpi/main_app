import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    property var icons: []
    property var listnames: []

    function getIndexofList(path, mmodel) {

        for (var i = 0; i < mmodel.length; i++) {

            if (path === mmodel[i]) {
                return i
            }
        }
        return 0
    }

    function listProperty() {

        var component = Qt.createComponent("../../fonts/Icons.qml")
        var obj = component.createObject()

        listnames = []

        icons = []

        for (var prop in obj) {

            if (typeof (obj[prop]) == 'string' && prop !== 'objectName') {
                // console.log(prop + ' ' +  obj[prop]);
                listnames.push(prop)
                icons.push(obj[prop])
            }
        }
    }

    property string instancename: modules.modules['UI']['ShowVideo'][0]

    color: "transparent"

    Flickable {
        anchors.fill: parent
        contentHeight: list.implicitHeight + 100


        Text {
            id: title
            text: "Video Settings > " + instancename
            color: Colors.black
            font.bold: true
            font.pixelSize:32
            padding: 10
            width: parent.width
            height:70
        }


    Column {
        width: parent.width * 0.9
        anchors.horizontalCenter: parent.horizontalCenter
        id: list
        anchors.top: title.bottom
        spacing: 20
        padding: 10




        Flow {
            width: parent.width
            height: implicitHeight

            Text {
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: "Path"
                font.pixelSize: 24
                color: Colors.black
                wrapMode: Text.WordWrap
                width: parent.width < 500 ? parent.width : parent.width * 0.2
                height: 50
            }

        TextField {
            onActiveFocusChanged: keyboard(this)
            id: video_path
            height: 50
            width: parent.width < 500 ? parent.width : parent.width * 0.8
            Component.onCompleted: video_path.text = modules.loaded_instances['UI']['ShowVideo'][instancename].video_path
            onTextChanged: modules.loaded_instances['UI']['ShowVideo'][instancename].video_path
                           = video_path.text

        }

}

        Flow {
            width: parent.width
            height: implicitHeight

            Text {
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: "Icon"
                font.pixelSize: 24
                color: Colors.black
                wrapMode: Text.WordWrap
                width: parent.width < 500 ? parent.width : parent.width * 0.2
                height: 50
            }

        ComboBox {
            id: combo_icon
            height: 50
            width: parent.width < 500 ? parent.width : parent.width * 0.8
            model: listnames

            onActivated: {
                modules.loaded_instances['UI']['ShowVideo'][instancename].icon
                        = icons[combo_icon.currentIndex]
                iconpreview.text = icons[combo_icon.currentIndex]
            }





        }
}

        Text {
            text: icons[combo_icon.currentIndex]
            id: iconpreview
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: localFont.name
            font.pixelSize: 120
            color: Colors.black
        }

        RoundButton {
            text: 'Delete Instance'
            palette.button: "darkred"
            palette.buttonText: "white"
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width < 500 ? parent.width : parent.width * 0.7
            onClicked: {

                settingsstackView.pop()
                modules.remove_instance('UI', 'ShowVideo', instancename)


            }
        }
    }

    Component.onCompleted: {
        listProperty()
        combo_icon.model = listnames
        combo_icon.currentIndex = getIndexofList(
                    modules.loaded_instances['UI']['ShowVideo'][instancename].icon,
                    icons)
    }
}
}
