import QtQuick 2.12
import QtQuick.Controls 2.12


Rectangle {
    property string dayname
    property bool active: false
    property bool even: false


    opacity: 0.7
    width: parent.width
    height: active ? 300 : 100
    border.color: "grey"
    border.width: 1
    color: even ? "#fff" : "#aaa"

    Label {

        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 10
        text: parent.dayname

        color: even ? "#aaa" : "#FFF"

        font.pointSize: parent.active ? 40 : 20
    }

    MouseArea {
        anchors.fill: parent
        //enabled: !parent.active
        onClicked: {

            for (var i = 0; i < parent.parent.children.length; i++)
            parent.parent.children[i].active = false


            parent.active = true
            flickable.contentY = parent.y - (parent.height/2)


        }
    }



}

