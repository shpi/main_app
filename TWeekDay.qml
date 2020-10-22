import QtQuick 2.15
import QtQuick.Controls 2.12


Rectangle {
    property string dayname
    property bool active: false



    opacity: 0.7
    width: parent.width
    height: active ? 300 : 60
    border.color: "grey"
    border.width: 1

    Label {

        anchors.centerIn: parent
        anchors.horizontalCenter: parent.horizontalCenter
        text: parent.dayname
        color: active ? "red" : "black"
        font.pointSize: parent.active ? 20 : 10
    }

    MouseArea {
        anchors.fill: parent
        //enabled: !parent.active
        onClicked: {
            var active2 = parent.active

            for (var i = 0; i < parent.parent.children.length; i++)
            parent.parent.children[i].active = false


            parent.active = !active2

        }
    }
}

