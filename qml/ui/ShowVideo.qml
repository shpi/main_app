import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15
import QtGraphicalEffects 1.12
import QtMultimedia 5.15



import "qrc:/fonts"

Rectangle {

    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['UI']['ShowVideo'][0]
    property var instance: modules.loaded_instances['UI']['ShowVideo'][instancename]
    property bool iconview: parent.iconview !== undefined ? parent.iconview : false


    id: videolittle
    height: parent.height
    width: height * 0.7
    radius: 10
    color: Colors.whitetrans
    clip: true


    Video {
        id: camStream
        anchors.fill:parent
        source: instance.video_path

        autoPlay: false
        opacity: 1.0
        fillMode: VideoOutput.PreserveAspectFit
        muted: true
        flushMode: VideoOutput.LastFrame

        Text {
            visible: videolittle.iconview
            id: icontext
            text: instance.icon
            color: Colors.black
            anchors.top: parent.top
            anchors.topMargin: 3
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 90
            font.family: localFont.name
            z: camStream.z + 1
        }

    }






    MouseArea {
        anchors.fill: parent
        onClicked: { popupVideo.open(); camStream.parent = shutterPopup; camStream.source = instance.video_path; camStream.play(); videolittle.iconview = false;}
        enabled: iconview
    }

    Popup {
        id: popupVideo

        enter: Transition {

            NumberAnimation {property: "opacity"; from: 0.0; to: 1.0}
            NumberAnimation {property: "scale"; from: 0.5; to: 1.0}

        }

        exit: Transition {

            NumberAnimation {property: "opacity"; from: 1.0; to: 0.0}

        }

        height: window.height
        width: window.width

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


        Rectangle {
        anchors.fill: parent
        color: "transparent"
        id: shutterPopup
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
            onClicked:  { camStream.parent = videolittle; popupVideo.close(); camStream.pause(); videolittle.iconview = true; }

        }


    }


}
