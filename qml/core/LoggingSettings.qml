import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {

    color: "transparent"
    anchors.fill: parent

    ListView {
        cacheBuffer: 200
        id: listView
        boundsBehavior: Flickable.StopAtBounds

        //clip: true
        model: logs
        width: parent.width
        height: parent.height - 50
        anchors.bottom: parent.bottom
        anchors.margins: 5
        delegate: itemDelegate
        
        verticalLayoutDirection: ListView.BottomToTop

        onCountChanged: {

            //while (listView.count > 100)   logs.removeRows(0)

            Qt.callLater( listView.positionViewAtEnd )

            //if (listView.contentY == listView.contentHeight) {Qt.callLater(listView.positionViewAtEnd) }
        }
    }

    Component {
        id: itemDelegate
        property color red: Qt.tint(Colors.white, "#44aa4444")
        property color blue: Qt.tint(Colors.white, "#444444aa")


        Rectangle {
            id: delegate
            color: index % 2 ? levelno < 30 ? blu : red  : Colors.white
            height: content.height + 10
            width: ListView.view.width

            Text {
                id: level
                font.pixelSize: 25
                text: levelname + ' '
                color: levelno < 30 ? "steelblue" : "red"
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                id: content
                wrapMode: Text.Wrap
                text: asctime + ' ' + msg
                font.pixelSize: 20
                color: Colors.black
                //elide: Text.ElideRight
                anchors.right: parent.right
                width: parent.width - level.width
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
