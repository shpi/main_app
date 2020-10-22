import QtQuick 2.12
import QtQuick.Controls 2.12


Rectangle {
    property string dayname
    property bool active: false
    property bool even: false


    opacity: 0.7
    width: parent.width
    height: active ? 300 : 60
    border.color: "grey"
    border.width: 1
    color: even ? "#fff" : "#BBB"

    Label {

        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 10
        text: parent.dayname
        opacity: active ? 1 : 0.7
        color: even ? "#BBB" : "#FFF"

        font.pointSize: parent.active ? 30 : 20
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

