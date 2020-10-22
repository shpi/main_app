import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12


import "fonts/"



Item {
    anchors.fill: parent


    TabBar {
        anchors.top: parent.top
        anchors.left: parent.left
        width: parent.width * 0.3
        id: tabBar
        height:parent.height

            currentIndex: swipeView.currentIndex

            TabButton {

                anchors.top: parent.top
                height: parent.height / 3
                id: firstButton
                text: Icons.fire
                font.family: localFont.name
                font.pointSize: 30
                anchors.right: parent.right

            }
            TabButton {
                height: parent.height / 3
                id: secondButton

                text: Icons.settings
                font.family: localFont.name
                font.pointSize: 30
                anchors.top: firstButton.bottom
                anchors.right: parent.right
            }
            TabButton {
                height: parent.height / 3
                text: Icons.clock
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
        width: parent.width * 0.9
        currentIndex: tabBar.currentIndex
        orientation: Qt.Vertical


        Item {



        Dial {
            id: dialTherm
            width: parent.width * 0.8
            height: parent.height * 0.8
            anchors.centerIn: parent


            enabled: false
            from: 15.0
            to: 32.0
            stepSize: 0.1
            snapMode: Dial.SnapAlways
            onPressedChanged: if (pressed == false) {
                                  enabled = false
                                  dialLocker.enabled = true
                                  view.interactive = true
                              }


            Text {
            id: actualSetTemperature
            text: parent.value.toFixed(1) + "°"
            anchors.top: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            font.pointSize: 30
            }

            Text {
            id: actualTemperature
            text: parent.value.toFixed(1) + "°"
            anchors.bottom: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            font.pointSize: 40
            }

            Shape {
                id: thermostatrange
                width: parent.height * 1.1
                height: parent.height * 1.1
                anchors.centerIn: parent
                layer.enabled: true
                layer.smooth: true
                layer.samples: 4

                ShapePath {
                    strokeWidth: 0
                    strokeColor: "transparent"
                    fillGradient: ConicalGradient {

                        centerX: (thermostatrange.width / 2) ; centerY: (thermostatrange.height / 2)
                        angle: -120
                        GradientStop { position: 1; color: "#0000ff" }
                        GradientStop { position: 0; color: "#ff0000" }

                    }

                    PathAngleArc {
                           id:outer
                           centerX: (thermostatrange.width / 2); centerY: (thermostatrange.height / 2)
                           radiusX: (thermostatrange.width / 2)  ; radiusY: (thermostatrange.width / 2)
                           startAngle: -230
                           sweepAngle:dialTherm.angle + 140

                       }
                    PathAngleArc {
                           moveToStart : false
                           centerX: outer.centerX; centerY: outer.centerY
                           radiusX: (thermostatrange.width / 2) * 0.9
                           radiusY: (thermostatrange.width / 2) * 0.9
                           startAngle: outer.startAngle + outer.sweepAngle
                           sweepAngle: -outer.sweepAngle

                       }

                }
            }


           InnerShadow {
                anchors.fill: thermostatrange
                radius: 8.0
                samples: 16
                horizontalOffset: -3
                verticalOffset: 3
                color: "#b0000000"
                source: thermostatrange
            }



        }

        MouseArea
               {
                   id: dialLocker
                   anchors.fill: parent
                   onDoubleClicked: {dialTherm.enabled = true
                                     enabled = false
                                     view.interactive = false
                                    }
                   onPressAndHold: {dialTherm.enabled = true
                                     enabled = false
                                     view.interactive = false
                                    }
               }

}

        Item {

            Rectangle {
            width: parent.width
            height: parent.height
            anchors.centerIn: parent
            color: "red"

      }
  }

        Item {
            Flickable {
            id: flickable
            anchors.fill:parent
            contentHeight: parent.height * 1.7

            Loader {

                anchors.fill:parent
                id: verticalTabs
                source: "ThermostatWeek.qml"
             }

        }}


 }


}




