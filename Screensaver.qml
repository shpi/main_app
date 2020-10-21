import QtQuick 2.0
import Qt.labs.folderlistmodel 2.15


Item {

anchors.fill : parent


property int i: 0

FolderListModel {
          //caseSensitive: false
          id: folderModel
          folder: "backgrounds/"
          nameFilters: [ "*.png", "*.jpg" ]
          onCountChanged: {
                  if (folderModel.count > 0)
                           bg.source =  folderModel.get (i, "fileURL")
                           console.log("Found images for screensaver: " + folderModel.count)
      }

      }



Image {
        anchors.fill: parent
        id: bg
        source :  ""
        fillMode: Image.Stretch
}



}

