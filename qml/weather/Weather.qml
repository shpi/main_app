import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {
    anchors.fill: parent

    TabBar {
        anchors.top: parent.top
        anchors.left: parent.left
        width: parent.width * 0.4
        id: tabBar
        height: parent.height

        currentIndex: swipeView.currentIndex

        TabButton {

            anchors.top: parent.top
            height: parent.height / 3
            id: firstButton
            text: Icons.cloudsun
            font.family: localFont.name
            font.pointSize: 30
            anchors.right: parent.right
        }
        TabButton {
            height: parent.height / 3
            id: secondButton

            text: Icons.graph
            font.family: localFont.name
            font.pointSize: 30
            anchors.top: firstButton.bottom
            anchors.right: parent.right
        }
        TabButton {
            height: parent.height / 3
            text: Icons.settings
            font.family: localFont.name
            font.pointSize: 30
            anchors.top: secondButton.bottom
            anchors.right: parent.right
        }
    }

    SwipeView {
        id: swipeView
        anchors.right: parent.right
        anchors.top: parent.top
        height: parent.height
        width: parent.width - (tabBar.width / 3)
        currentIndex: tabBar.currentIndex
        orientation: Qt.Vertical


        Loader {
            width: parent.width
            height: 480
            id: weatherdays
            source: "WeatherDays.qml"
         }

        Loader {
            width: parent.width
            height: 480
            id: weathergraph
            source: "WeatherGraph.qml"
         }

        Loader {
            width: parent.width
            height: 480
            id: weathersettings
            source: "WeatherSettings.qml"
         }



    }
}
