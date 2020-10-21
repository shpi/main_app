import QtQuick 2.0
import Qt.labs.folderlistmodel 2.15


Item {

property int i: 0




FolderListModel {
          caseSensitive: false
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



Timer {
            property bool direction: true
            property int speed: 3
            id: resetTimer
            interval: 5000
            repeat: true
            running: parent.parent._isCurrentItem
            onTriggered: {

            moving_text.opacity = 0
            moving_text.x = 10 + Math.random() * Math.floor(parent.width - moving_text.width - 20)
            moving_text.y = 10 + Math.random() * Math.floor(parent.height - moving_text.height - 20)
            showSlow.start()
            bg.source =  folderModel.get (Math.random() * Math.floor(folderModel.count), "fileURL")

             /*
             if (direction)    moving_text.x = moving_text.x - speed
             else              moving_text.x = moving_text.x + speed

             if(moving_text.x < 0) direction = false
             else

            if(moving_text.x > (parent.width - moving_text.width)) {
              direction = true
              speed = Math.random() * Math.floor(5)
           }
            */

            }



        }


        Text{
            id:moving_text
            x:parent.width - moving_text.width
            y:parent.height - moving_text.width
            text:"Uhrzeit"
            color: "white"
            font.pointSize: 40
            NumberAnimation {id:showSlow; target: moving_text; property: "opacity"; from: 0.00; to:1.00; duration: 1000 }
        }




}

