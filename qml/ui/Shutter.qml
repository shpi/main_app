import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import "../../fonts/"

Item {
    anchors.fill: parent


    TabBar {
        anchors.top: parent.top
        anchors.left: parent.left
        width: parent.width * 0.266
        id: tabBar
        height: parent.height
        currentIndex: swipeView.currentIndex
        background: Rectangle {
            color: Colors.white
        }

        TabButton {

            anchors.top: parent.top
            height: parent.height / 2
            id: firstButton
            text: Icons.shutter
            font.family: localFont.name
            font.pointSize: 25
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
                   color:  tabBar.currentIndex == 0 ? "transparent" :"#22FFFFFF"

               }

        }
        TabButton {
            height: parent.height / 2
            id: secondButton
            text: Icons.settings
            font.family: localFont.name
            font.pointSize: 25
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
                   color:  tabBar.currentIndex == 1 ? "transparent" :"#22FFFFFF"

               }
        }

    }

    SwipeView {
        id: swipeView
        anchors.right: parent.right
        anchors.top: parent.top
        height: parent.height
        width: parent.width - (tabBar.width / 2)
        currentIndex: tabBar.currentIndex
        orientation: Qt.Vertical

    Item {


    Text {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
        text: Icons.sunset
        font.family: localFont.name
        font.pointSize: 30
        color: Colors.black
    }

    Text {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 10
        font.pointSize: 30
        font.family: localFont.name
        text: Icons.sunrise
        color: Colors.black
    }

    Rectangle {
        height: parent.height * 0.75 + 8
        width: 308
        border.width: 4
        border.color: "grey"
        anchors.centerIn:parent
    Slider {
        id: control
        enabled: shutter2.state !== 'STOPSLEEP'  ? true : false
        from: 0
        to: 100
        value: pressed == false ? shutter2.actual_position : shutter2.desired_position
        orientation: Qt.Vertical
        height: parent.height - 8
        width: 300
        anchors.centerIn: parent
        stepSize: 5
        onPressedChanged: this.pressed === false ? shutter2.set_position(this.value) : undefined


        Text {
            text: shutter2.desired_position + "%"
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.left
            font.pointSize: 15
            anchors.rightMargin: 20
            color: Colors.black
        }

        background: Rectangle {

            width: 300
            height: parent.height

            LinearGradient {
                anchors.fill: parent
                start: Qt.point(0, 0)
                end: Qt.point(0, control.visualPosition * parent.height)
                gradient: Gradient {
                    GradientStop {
                        position: 0.0
                        color: "#DDD"
                    }
                    GradientStop {
                        position: 1.0
                        color: "#555"
                    }
                }
            }

            Column {
                spacing: 30
                anchors.top: parent.top
                anchors.fill: parent
                Repeater {
                    model: 10
                    Rectangle {
                        width: parent.parent.width
                        height: 1
                        color: "grey"
                    }
                }
            }

            Rectangle {


                anchors.bottom: parent.bottom
                height: parent.height - (control.visualPosition * parent.height)
                width: 300

                LinearGradient {
                    anchors.fill: parent
                    start: Qt.point(0, 1)
                    end: Qt.point(0, 5 + control.visualPosition * parent.height)
                    gradient: Gradient {
                        GradientStop {
                            position: 0.0
                            color: "#002"
                        }
                        GradientStop {
                            position: 1.0
                            color: "#55f"
                        }
                    }
                }
            }
        }


        Rectangle {
        z: parent.handle.z - 0.01
        visible: shutter2.state !== 'STOP' && parent.pressed == false ? true : false
        width: parent.width * 1.1
        height: parent.height * 0.15
        radius: 13
        opacity: 0.5
        color: Colors.black
        y: control.topPadding + (1 - (shutter2.desired_position / 100)) * (control.availableHeight - height)
        anchors.horizontalCenter: parent.horizontalCenter
       }




        handle: Rectangle {

            y: control.topPadding + control.visualPosition * (control.availableHeight - height)
            width: parent.width * 1.1
            anchors.horizontalCenter: parent.horizontalCenter
            height: parent.height * 0.15
            radius: 13
            color: control.pressed ? "#f0f0f0" : "#f6f6f6"
            border.color: "#bdbebf"
            Text {
                id: handleIcon
                font.family: localFont.name

                text: {shutter2.state === 'STOP' ? Icons.shutter :
                       shutter2.state === 'STOPSLEEP' ?  Icons.locked : Icons.arrow
                }
                rotation: shutter2.state === 'UP' ? 180 : 0
                anchors.centerIn: parent
                font.pointSize: 20
                opacity: shutter2.state === 'STOP' ? 1 : 1

              /*  NumberAnimation {
                     target: handleIcon
                     from: 0.05
                     to: 1
                     properties: "opacity"
                     duration: 1000
                     running: shutter2.state === 'STOP' ? false : true
                     loops: Animation.Infinite
                 } */
            }



        }


    }




    }


   /* Text {
        anchors.verticalCenter: parent.verticalCenter
        anchors.bottomMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 10
        font.pointSize: 15
        color: Colors.black
        //text: shutter2.residue_time === 0 ? '' : shutter2.residue_time.toFixed(1)  + Icons.timer
        font.family: localFont.name
    }
  */


}

    Item {


            Loader {

                anchors.fill: parent

                source: "ShutterSettings.qml"
            }


    }

    }
}
