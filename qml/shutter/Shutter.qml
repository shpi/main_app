import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import "../../fonts/"

Item {
    anchors.fill: parent


    Text {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
        text: Icons.sunset
        font.family: localFont.name
        font.pointSize: 30
    }

    Text {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 10
        font.pointSize: 30
        font.family: localFont.name
        text: Icons.sunrise
    }

    Slider {
        id: control
        enabled: shutter2.state !== 'STOPSLEEP'  ? true : false
        from: 0
        to: 100
        value: pressed == false ? shutter2.actual_position : shutter2.desired_position
        orientation: Qt.Vertical
        height: parent.height * 0.75
        width: 300
        anchors.centerIn: parent
        stepSize: 5
        onPressedChanged: this.pressed === false ? shutter2.set_position(this.value) : undefined


        Text {
            text: shutter2.desired_position + "%"
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.left
            font.pointSize: 30
            anchors.rightMargin: 20
            color: "black"
        }

        background: Rectangle {

            border.width: 2
            border.color: "black"
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
                width: parent.width

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
        color: "black"
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



    Text {
        anchors.verticalCenter: parent.verticalCenter
        anchors.bottomMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 10
        font.pointSize: 30
        text: shutter2.residue_time === 0 ? '' : shutter2.residue_time.toFixed(1)  + Icons.timer
        font.family: localFont.name
    }


    Text {
               id: time
               font.pixelSize: 30
               text: time.startTime != 0 ? new Date().getTime() - time.startTime + " ms" : 0
               anchors.horizontalCenter: parent.horizontalCenter
               property double startTime: 0
           }

           Button {

               background: Rectangle {
                           color: parent.down ?  "#f0f0f0" : "#f6f6f6"
                           border.color: "#bdbebf"
                           border.width: 1
                           radius: 13
                       }


              text: "Timer!"
              anchors.horizontalCenter: parent.horizontalCenter
              anchors.horizontalCenterOffset: 100
               onClicked: {
                   if(time.startTime == 0){
                       time.startTime = new Date().getTime()
                       timer.running = true
                   } else {
                       timer.running = false
                       time.text = ((new Date().getTime() - time.startTime) / 1000).toFixed(1) + "s"
                       time.startTime = 0
                   }}}

           Timer {
                   id: timer
                   interval: 200; running: false; repeat: true
                   onTriggered: time.text = ((new Date().getTime() - time.startTime) / 1000).toFixed(1) + "s"
               }
}
