import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {
    anchors.fill: parent

    TabBar {
        anchors.top: parent.top
        anchors.left: parent.left
        width: parent.width * 0.3
        id: tabBar
        height: parent.height

        currentIndex: swipeView.currentIndex

        background: Rectangle {
            color: "transparent"
        }

        TabButton {

            anchors.top: parent.top
            height: parent.height / 2
            id: firstButton
            text: Icons.cloudsun
            font.family: localFont.name
            font.pointSize: 30
            anchors.right: parent.right

            contentItem: Text {
                text: parent.text
                font: parent.font
                color: tabBar.currentIndex == 0 ? Colors.black : Colors.white
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }
            background: Rectangle {
                color: tabBar.currentIndex == 0 ? Colors.whitetrans : Colors.blacktrans
            }
        }
        TabButton {
            height: parent.height / 2
            id: secondButton

            text: Icons.graph
            font.family: localFont.name
            font.pointSize: 30
            anchors.top: firstButton.bottom
            anchors.right: parent.right

            contentItem: Text {
                text: parent.text
                font: parent.font
                color: tabBar.currentIndex == 1 ? Colors.black : Colors.white
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }
            background: Rectangle {
                color: tabBar.currentIndex == 1 ? Colors.whitetrans : Colors.blacktrans
            }
        }

        /*   TabButton {
            height: parent.height / 3
            text: Icons.settings
            font.family: localFont.name
            font.pointSize: 30
            anchors.top: secondButton.bottom
            anchors.right: parent.right

            contentItem: Text {
                   text: parent.text
                   font: parent.font
                   color: tabBar.currentIndex == 2 ? Colors.black : Colors.white
                   horizontalAlignment: Text.AlignHCenter
                   verticalAlignment: Text.AlignVCenter
                   elide: Text.ElideRight
               }
            background: Rectangle {
                   color:  tabBar.currentIndex == 2 ? Colors.white :"#666"

               }
        } */
    }

    SwipeView {
        property string instancename: modules.modules['Info']['Weather'][0]

        id: swipeView
        anchors.right: parent.right
        anchors.top: parent.top
        height: parent.height
        width: parent.width - (tabBar.width / 2)
        currentIndex: tabBar.currentIndex
        orientation: Qt.Vertical

        Loader {
            width: parent.width
            height: 480
            id: weatherdays
            source: "WeatherDays.qml"
        }

        Connections {
            target: weatherdays.item
            onMessage: weathergraphloader.item.reload()
        }

        Loader {
            width: parent.width
            height: 480
            id: weathergraphloader
            source: "WeatherGraph.qml"
        }


        /*      Loader {
            width: parent.width
            height: 480
            id: weathersettings
            source: "WeatherSettings.qml"
         }

*/
    }
}
