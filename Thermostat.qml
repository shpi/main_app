import QtQuick 2.15
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.15

Item {


Dial {
    id: dialTherm
    width: parent.width * 0.8
    height: parent.height * 0.8
    anchors.verticalCenter : parent.verticalCenter
    anchors.right: parent.right
    anchors.rightMargin: 5

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
