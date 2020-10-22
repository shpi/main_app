import QtQuick 2.12
import QtQuick.Controls 2.12


Column {
     anchors.horizontalCenter: parent.horizontalCenter
     anchors.verticalCenter: parent.verticalCenter

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


