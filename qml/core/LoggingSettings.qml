import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Rectangle {

    color: "transparent"
    anchors.fill: parent

    ListView {
        cacheBuffer: 100
        id: listView
        boundsBehavior: Flickable.StopAtBounds
        property color red: Qt.tint(Colors.white, "#44aa4444")
        property color blue: Qt.tint(Colors.white, "#444444aa")

        model: logs
        width: parent.width
        height: parent.height - 50
        anchors.centerIn: parent
        anchors.margins: 5
        delegate: itemDelegate

        verticalLayoutDirection: ListView.BottomToTop

        onCountChanged: {

            if (listView.atYBeginning)

                Qt.callLater(listView.positionViewAtEnd)
        }
    }

    Component {
        id: itemDelegate

        Rectangle {
            id: delegate
            color: index % 2 ? levelno < 30 ? listView.blue : listView.red : Colors.white
            width: ListView.view.width
            height: title.height >  content.height ? title.height : content.height
                      

           Rectangle {
            id:title
            anchors.left: parent.left
            width: 150
            height: 40
            anchors.verticalCenter: parent.verticalCenter
            color: "transparent"

            Text {
                id: level
                font.pixelSize: 20
                text: levelname + ' '
                color: levelno < 30 ? "steelblue" : "red"
                width: parent.width
                anchors.top: parent.top
                horizontalAlignment: Text.AlignHCenter
            }

           Text {
             id: time
             text: asctime
             color: Colors.black
             width: parent.width
             font.pixelSize: 16
             anchors.bottom: parent.bottom
             wrapMode: Text.WordWrap
             horizontalAlignment: Text.AlignHCenter
            }}


            Text {
                id: pymodule
                wrapMode: Text.WordWrap
                text:  module
                width: 120
                anchors.left: title.right
                font.bold: true
                font.pixelSize: 20
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
                horizontalAlignment: Text.AlignHCenter
            }


            Text {
                padding: 5
                id: content
                anchors.right: parent.right
                wrapMode: Text.WordWrap
                text:  msg
                width: parent.width - pymodule.width - level.width - 20
                font.pixelSize: 16
                color: Colors.black
                anchors.verticalCenter: parent.verticalCenter
            } 
        }
    }

} 
