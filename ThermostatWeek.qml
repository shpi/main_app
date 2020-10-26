import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    anchors.fill: parent


Column {
     property var weekday: ["Sunday", "Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday"]
     id: weekdays
     anchors.horizontalCenter: parent.horizontalCenter
     anchors.verticalCenter: parent.verticalCenter
     anchors.fill: parent
     spacing: 1
     clip: true

     Repeater{


         model: 13

     ThermostatWeekDay {
      dayname: (Math.floor(index / 7) + 1)  + "." + parent.weekday[(index%7)]
      even: index % 2 ? true : false
     ThermostatWeekKnob {value:1440;to:1440;from:0}
     ThermostatWeekKnob {value:550;to:1440;from:0}

    }
     }



}

Row {
    anchors.top: parent.top
    height: parent.height
    anchors.centerIn: parent
    width: parent.width - 80  //weekknob width
    spacing: ((parent.width) / 14) +1



Repeater{
    model: 13

    Rectangle {
    color: "black"
    opacity: 0.3
    width:1
    height: parent.height
    anchors.top: parent.top
    Label {
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.top: parent.top
    text: index * 2
    font.pointSize: 8

    }

    Label {
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.top: parent.bottom
    text: index * 2
    font.pointSize: 8
    }
    }

}



}

Loader {
       property int value: 0
       id: loader
       focus: true
       width: parent.width
       height: 280
       anchors.centerIn:parent
       source: "ThermostatKnobSlider.qml"
       visible: false
   }


}
