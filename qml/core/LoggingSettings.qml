import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"



        Rectangle {

            color: "transparent"
            anchors.fill: parent

            ListView {
                id: listView

                clip: true

                model: logs

                anchors.fill: parent
                anchors.margins: 5

                delegate: itemDelegate


                onCountChanged:    {listView.positionViewAtEnd() }

                }




        Component {
            id: itemDelegate

            MouseArea {
                id: delegate

                width: ListView.view.width
                height: content.height + 10

                clip: true
                hoverEnabled: true

                property color levelColor: levelno < 30 ? "steelblue" : "red"

                Rectangle {
                    anchors.fill: parent
                    color: delegate.levelColor
                    opacity: delegate.containsMouse ? 0.1 : 0

                }

                Row {
                    id: content

                    width: parent.width
                    spacing: 5

                    anchors.verticalCenter: parent.verticalCenter

                    clip: true



                    Rectangle {
                        id: level
                        height: levelText.paintedHeight + 4
                        width: levelText.paintedWidth + 4

                        color: Qt.lighter(delegate.levelColor, 1.8)

                        Text {
                            id: levelText
                            font.pixelSize: 25
                            text: levelname
                            color: delegate.levelColor
                            anchors.fill: parent
                            anchors.margins: 2
                        }
                    }

                    Text {
                        wrapMode: Text.Wrap
                        text: asctime + ' ' + msg
                        font.pixelSize: 20
                        elide: Text.ElideRight
                        width: delegate.width - level.width
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }
    }



