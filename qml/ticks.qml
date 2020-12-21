import QtQuick 2.12
import QtGraphicalEffects 1.12
import QtQuick.Shapes 1.12



Rectangle {

    property real max_temp: 32
    property real min_temp: 16

    id: tickswindow
    height:parent.height
    width: height
    anchors.horizontalCenter: parent.horizontalCenter

    color: "transparent"


    Text {
        id: temptext
        property real temperatur : 20

        //text: temperatur.toFixed(1) + '°C'
        //text: (32 - ( (rotator.rotation / 15))).toFixed(1) + "°C"
        text: (min_temp + (-rotator.rotation + 240) * ((max_temp - min_temp) / 240)).toFixed(1) + '°C'
        color: "white"
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: 20

        font.pointSize: 30
    }


    Rectangle {
        anchors.top: tickswindow.top
        height:tickswindow.height
        width: tickswindow.width/4
        anchors.right: tickswindow.right
        //border.width: 1
        //border.color: "white"
        //opacity: 0.5
        color: "transparent"



    MouseArea {
                anchors.fill: parent
                preventStealing: true
                property real velocity: 0.0
                property int xStart: 0
                property int xPrev: 0
                property bool tracing: false
                onPressed: {
                    xStart = mouse.y
                    xPrev = mouse.y
                    velocity = 0
                    tracing = true

                }
                onPositionChanged: {
                    if ( !tracing ) return
                    var currVel = (mouse.y-xPrev)
                    velocity = (velocity + currVel)/2.0
                    xPrev = mouse.y
                    if ( velocity > 10) {

                        rotator.rotation -= (velocity/10)*(velocity/10)
                        if (rotator.rotation < 0) rotator.rotation = 0




                  }

                    if ( velocity < -10) {
                        rotator.rotation += (velocity/10)*(velocity/10)

                        if (rotator.rotation > 240) rotator.rotation = 240




                  }

                }
                onReleased: {
                    tracing = false
                    if (rotator.rotation < 0) rotator.rotation = 0
                     if (rotator.rotation > 240) rotator.rotation = 240

                }
            }}



Rectangle {
    id: rotator
    height: tickswindow.height + 240
    width: height
    anchors.verticalCenter: tickswindow.verticalCenter
    anchors.horizontalCenter: tickswindow.right
    anchors.horizontalCenterOffset:  110
    color: "transparent"
    border.width: 1
    border.color: "white"
    radius: width / 2
    rotation: 90
    Behavior on rotation { PropertyAnimation {} }

Repeater {

model: 120

Rectangle {
    anchors.centerIn: parent
    width: 5
    height: parent.height - 40
    color: "transparent"
    rotation: index * 3 - 27
    //border.width: 1
    //border.color: "white"



    Text {
        text: index % 5 == 0 ? (min_temp + ((index * 3) - 60) * ((max_temp - min_temp) / 240)).toFixed(0)  : ''
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenterOffset: -240
        anchors.horizontalCenterOffset: 0
        visible: index % 5  == 0  && this.text <= max_temp &&  this.text >= min_temp ?  true : false
        color: "white"
        rotation:  90
    }



Rectangle {
    color: Qt.rgba(((index-20)/80), (1 - 2 * Math.abs(((index-20)/80) - 0.5)), 1-((index-20)/80), 1)
    width: 5
    height: 40
    anchors.left: parent.left
    antialiasing : true


}}}
}



}







