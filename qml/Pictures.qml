import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.folderlistmodel 1.0

import "qrc:/fonts"

Item {

Rectangle {
    anchors.fill:parent
    color: "transparent"


    GridView {
        anchors.centerIn:parent
        height: parent.height - 40
        width: 380 * 2
        cellWidth: 380
        cellHeight: 230
        model: folderModel
        delegate: fileDelegate
        header:  Rectangle {
        id: inforect
        width: parent.width
        border.color: "red"
        border.width: 1
        color: "transparent"
        height: infotext.implicitHeight
        Text {

        id: infotext
        anchors.centerIn:parent
        width: parent.width
        padding: 20
        color: Colors.black
        text: "You can upload new images here: " + wifi.wpa_ip + ":" + httpserver.port + "/upload"
        wrapMode: Text.WrapAnywhere
        }

        }



    }

    FolderListModel {
        id: folderModel
        folder: "file://" + applicationDirPath + "/backgrounds/"
        nameFilters: ["*.png", "*.jpg"]
    }

    Component {
        id: fileDelegate

        Rectangle {
            width: 380
            height: 230
            color: "transparent"
            
            Image {
                anchors.centerIn: parent
                width: 300
                height: 180
                fillMode: Image.PreserveAspectFit
                smooth: true
                source: folderModel.folder + "/" + fileName

                RoundButton {

                    anchors.right: parent.right
                    anchors.rightMargin: -20
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: -20
                    font.family: localFont.name
                    text: Icons.trash
                    width: height
                    palette.button: "#1E90FF"
                    palette.buttonText: Colors.black
                    font.pixelSize: 50
                    onClicked: appearance.delete_file('backgrounds/' + fileName)
                }
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: fileName
                color: Colors.black
                font.pixelSize: 20
                width: parent.width                
                wrapMode: Text.WrapAnywhere
                horizontalAlignment: Text.AlignHCenter

            }
        }
    }
}
}
