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
            height: content.height + 5

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
