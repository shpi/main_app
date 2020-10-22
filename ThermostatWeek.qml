import QtQuick 2.15
import QtQuick.Controls 2.12



Column {
     anchors.horizontalCenter: parent.horizontalCenter
     anchors.verticalCenter: parent.verticalCenter

     spacing: 1

     TWeekDay {
      dayname: "Monday"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }


    TWeekDay {
     dayname: "Tuesday"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "Wednesday"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "Thursday"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "Friday"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "Saturday"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }

    TWeekDay {
     dayname: "Sunday"
     TWeekKnob {value:1440;to:1440;from:0}
     TWeekKnob {value:550;to:1440;from:0}

    }


}


