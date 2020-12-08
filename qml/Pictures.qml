import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.folderlistmodel 1.0

import "../fonts/"

Item {

GridView {
anchors.fill: parent
cellWidth:380
cellHeight:230
model: folderModel
delegate: fileDelegate
}


FolderListModel {
    id: folderModel
    folder: "../backgrounds/"
    nameFilters: [ "*.png", "*.jpg" ]
}

Component {
    id: fileDelegate

    Rectangle {
        width: 350
        height: 210
        color: "transparent"


        Image {
            anchors.centerIn: parent
            width: 300; height: 180
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
                font.pointSize:  20
                onClicked: appearance.delete_file('backgrounds/' + fileName)
            }

        }
        Text { anchors.horizontalCenter: parent.horizontalCenter
               text: fileName
               color: Colors.black
               font.pointSize: 5}

    }



}

}
