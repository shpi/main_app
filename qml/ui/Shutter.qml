import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import "../../fonts/"

Item {

    property string instancename: 'local'

    anchors.fill: parent



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
        from: 0
        to: 100
        value: pressed == false ? modules.loaded_instances['Logic']['Shutter'][instancename].actual_position : modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
        orientation: Qt.Vertical
        height: parent.height - 8
        width: 300
        anchors.centerIn: parent
        stepSize: 5
        onPressedChanged: if (this.pressed === false) modules.loaded_instances['Logic']['Shutter'][instancename].set_position(this.value)


        Text {
            text: modules.loaded_instances['Logic']['Shutter'][instancename].desired_position + "%"
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
        visible: modules.loaded_instances['Logic']['Shutter'][instancename].actual_position !== modules.loaded_instances['Logic']['Shutter'][instancename].desired_position && parent.pressed == false ? true : false



        width: parent.width * 1.1
        height: parent.height * 0.15
        radius: 13
        opacity: 0.5
        color: Colors.black
        y: control.topPadding + (1 - (modules.loaded_instances['Logic']['Shutter'][instancename].desired_position / 100)) * (control.availableHeight - height)
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

                text: {modules.loaded_instances['Logic']['Shutter'][instancename].desired_position === modules.loaded_instances['Logic']['Shutter'][instancename].actual_position ? Icons.shutter :  Icons.arrow
                }
                rotation: modules.loaded_instances['Logic']['Shutter'][instancename].actual_position > modules.loaded_instances['Logic']['Shutter'][instancename].desired_position ? 0 : 180
                anchors.centerIn: parent
                font.pointSize: 20
                opacity: 1


            }



        }


    }




    }




}


