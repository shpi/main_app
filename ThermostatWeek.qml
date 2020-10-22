import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    anchors.fill: parent
    anchors.top: parent.top



Column {
     anchors.horizontalCenter: parent.horizontalCenter
     anchors.verticalCenter: parent.verticalCenter
     anchors.fill: parent
     anchors.top: parent.top
     spacing: 1


     TWeekDay {
      dayname: "MONDAY"
      even: true
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }


    TWeekDay {
     dayname: "TUESDAY"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "WEDNESDAY"
     even: true
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "THURSDAY"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "FRIDAY"
     even: true
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "SATURDAY"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "SUNDAY"
     even: true
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }


}

Row {
    anchors.top: parent.top
    height: parent.height
    anchors.centerIn: parent
    width: parent.width - (200/3)  //weekknob width
    spacing: (parent.width / 13) -2



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
    text: index * 2 + ":00"
    font.pointSize: 8

    }

    Label {
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.top: parent.bottom
    text: index * 2 + ":00"
    }
    }

}


}

}
