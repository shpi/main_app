import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import "../../fonts/"

Rectangle {

    height: parent.height
    width: height * 0.7
    radius: 10
    color: Colors.whitetrans
    clip: true
    property string instancename: modules.modules['Logic']['Shutter'][0]

    Rectangle {

        height: parent.height * 0.75
        width: height * 0.7
        border.width: 1
        border.color: Colors.black

        anchors.horizontalCenter: parent.horizontalCenter

        anchors.verticalCenter: parent.verticalCenter

        Slider {
            id: control
            from: 0
            to: 100
            value: pressed == false ? modules.loaded_instances['Logic']['Shutter'][instancename].actual_position : modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
            orientation: Qt.Vertical
            height: parent.height - 2
            width: parent.width - 2
            anchors.centerIn: parent

            stepSize: 5
            onPressedChanged: if (this.pressed === false)
                                  modules.loaded_instances['Logic']['Shutter'][instancename].set_desired_position(
                                              this.value)

            Text {
                text: modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.horizontalCenterOffset: -parent.width * 0.07
                anchors.verticalCenterOffset: parent.value > 50 ? parent.height
                                                                  * 0.2 : -parent.height * 0.2
                font.pixelSize: parent.height * 0.29
                color: Colors.black
                Text {
                    text: "%"
                    font.pixelSize: parent.parent.height * 0.14
                    anchors.left: parent.right
                    anchors.bottom: parent.bottom
                    color: Colors.black
                }
            }

            background: Rectangle {

                width: control.width
                height: control.height
                border.width: 1
                border.color: Colors.grey

                color: appearance.night === 1 ? "#333" : "#ddd"

                Column {
                    spacing: parent.height / 10
                    anchors.top: parent.top
                    anchors.fill: parent
                    Repeater {
                        model: 10
                        Rectangle {
                            width: parent.parent.width
                            height: 1
                            color: Colors.grey
                        }
                    }
                }

                Rectangle {

                    anchors.bottom: parent.bottom
                    height: parent.height - (control.visualPosition * parent.height)
                    width: control.width
                    border.width: 1
                    border.color: Colors.grey
                    color: appearance.night === 1 ? "#117" : "#99f"


                    /* LinearGradient {
                    anchors.fill: parent
                    start: Qt.point(0, 1)
                    end: Qt.point(0, 100)
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
                } */
                }
            }

            Rectangle {
                z: parent.handle.z - 0.01
                visible: modules.loaded_instances['Logic']['Shutter'][instancename].actual_position
                         !== modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
                         && parent.pressed == false ? true : false

                width: parent.width * 1.1
                height: parent.height * 0.15
                radius: height / 2
                opacity: 0.5
                color: Colors.black

                y: control.height
                   - ((modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
                       / 100) * control.height) - height / 2

                anchors.horizontalCenter: parent.horizontalCenter
            }

            handle: Rectangle {

                //y: control.topPadding + control.visualPosition * (control.availableHeight - height)
                y: (control.visualPosition * control.height) - height / 2
                width: parent.width * 1.1
                anchors.horizontalCenter: parent.horizontalCenter
                height: parent.height * 0.15
                radius: height / 2
                color: control.pressed ? "#f0f0f0" : "#f6f6f6"
                border.color: "#bdbebf"
                Text {
                    id: handleIcon
                    font.family: localFont.name

                    text: {
                        modules.loaded_instances['Logic']['Shutter'][instancename].desired_position
                                === modules.loaded_instances['Logic']['Shutter'][instancename].actual_position ? Icons.shutter : Icons.arrow
                    }
                    rotation: modules.loaded_instances['Logic']['Shutter'][instancename].desired_position > modules.loaded_instances['Logic']['Shutter'][instancename].actual_position ? 180 : 0
                    anchors.centerIn: parent
                    font.pixelSize: parent.height
                    opacity: 1
                }
            }
        }
    }
}
