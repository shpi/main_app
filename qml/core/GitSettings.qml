import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Dialogs 1.1

import "../../fonts/"

Rectangle {



    color: "transparent"
    anchors.fill: parent

    Column {
        padding: 5
        spacing: 10
        anchors.fill: parent


    Text {
    visible: git.updates_remote === 0
    text: "You're up to date!"
    anchors.horizontalCenter: parent.horizontalCenter
    color: "green"
    }


    Text {
    visible: git.updates_remote > 0
    text: "New version available (" + git.updates_remote + ")"
    anchors.horizontalCenter: parent.horizontalCenter
    color: "red"
    }


    Row {
        visible: git.updates_remote > 0
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20

        Text {
            visible: git.updates_remote > 0
            anchors.verticalCenter: parent.verticalCenter
            text: 'version:'
            font.family: localFont.name
            font.pixelSize: 24
            color: Colors.black
        }
        Text {
            visible: git.updates_remote > 0
            text: git.update_shex + ', ' + new Date(git.update_timestamp * 1000).toLocaleDateString()
            font.pixelSize: 20
            color: Colors.black
            anchors.verticalCenter: parent.verticalCenter
        }


    }

    Row {
        visible: git.updates_remote > 0
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20

        Text {
            visible: git.updates_remote > 0
            anchors.verticalCenter: parent.verticalCenter
            text: 'Description:'
            font.family: localFont.name
            font.pixelSize: 24
            color: Colors.black
        }
        Text {
            visible: git.updates_remote > 0

            text: git.update_description
            font.pixelSize: 20
            color: Colors.black
            anchors.verticalCenter: parent.verticalCenter
        }


    }


    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: 'installed version:'
            font.family: localFont.name
            font.pixelSize: 24
            color: Colors.black
        }
        Text {

            text: new Date(git.actual_version * 1000).toLocaleDateString()

            font.pixelSize: 20
            color: Colors.black
            anchors.verticalCenter: parent.verticalCenter
        }


    }

/*
    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: 'Branch:'
            font.family: localFont.name
            font.pixelSize: 24
            color: Colors.black
        }
        Text {
            width: 200
            text: git.actual_branch

            font.pixelSize: 20
            color: Colors.black
            anchors.verticalCenter: parent.verticalCenter
        }


    } */


    Popup {
           property string text2: ''
           id: messageDialog
           width: parent.width * 0.7
           height: parent.height * 0.7
           parent: Overlay.overlay
           x: Math.round((parent.width - width) / 2)
           y: Math.round((parent.height - height) / 2)
           padding: 10
           topInset: 0
           leftInset: 0
           rightInset: 0
           bottomInset: 0

           background: Rectangle {
               color: Colors.white
               radius: 20
               border.width: 1
               border.color: Colors.black
           }

           Text {
           text: messageDialog.text2
           anchors.centerIn:parent
           color: Colors.black
           font.pixelSize: 30
           }


           RoundButton {
               opacity: 1
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
               onClicked:  messageDialog.close()
               }
           }





    DelayButton {
        text: "merge " + Icons.doublearrow
        delay: 2500
        width: 300
        height: 80
        font.pixelSize: 50
        onActivated: {messageDialog.text2 = git.merge()
                      messageDialog.open()
                      git.update()}
        anchors.horizontalCenter: parent.horizontalCenter
        visible: git.updates_remote > 0 && git.updates_local === 0

        background: Rectangle {
             color: "green"
            radius: 20
            opacity: 0.3
            border.width: 2
        }


    }


    DelayButton {
        text: "reboot " + Icons.reset
        delay: 2500
        width: 300
        height: 80
        font.pixelSize: 50
        onActivated: git.reboot()
        anchors.horizontalCenter: parent.horizontalCenter

        background: Rectangle {
             color: "red"
            radius: 20
            opacity: 0.3
            border.width: 2
        }


    }



}
}
