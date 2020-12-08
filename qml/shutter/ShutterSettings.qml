import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Rectangle {
   anchors.fill: parent
   color: Colors.white

// Operationsmodus, Ausgänge,  Autmatisch hochfahren uhrzeit, Autmatisch runterfahren uhrzeit
   Column {

       anchors.centerIn: parent
       spacing:  20

   Text {

       text: "Working Mode"
       color: Colors.black
       font.bold: true
       anchors.topMargin: 20

   }

   Row {
       anchors.horizontalCenter: parent.horizontalCenter
       RadioButton {
              checked: shutter2.mode === 'boolean' ? true : false

              text: qsTr("boolean")
              contentItem: Text {
                      text: parent.text
                      color: Colors.black
                      leftPadding: parent.indicator.width + parent.spacing
                      verticalAlignment: Text.AlignVCenter
                  }
       }

       RadioButton {
              checked: shutter2.mode === 'percent' ? true : false


              text: qsTr("percent")
              contentItem: Text {
                      text: parent.text
                      color: Colors.black
                      leftPadding: parent.indicator.width + parent.spacing
                      verticalAlignment: Text.AlignVCenter
                  }
       }



   }





Row {
    spacing:  10
    Text {
    anchors.verticalCenter: parent.verticalCenter
    text: "Temperature offset"
    color: Colors.black
    }

    SpinBox {

        id: tempoffset
        from: -100 * 100
        value: 10
        to: 100 * 100
        stepSize: 10
        font.pointSize: 18
        property int decimals: 2
        property real realValue: value / 100

        validator: DoubleValidator {
            bottom: Math.min(tempoffset.from, tempoffset.to)
            top:  Math.max(tempoffset.from, tempoffset.to)
        }

        textFromValue: function(value, locale) {
            return Number(value / 100).toLocaleString(locale, 'f', tempoffset.decimals) + "°"
        }

        valueFromText: function(text, locale) {
            return Number.fromLocaleString(locale, text) * 100
        }


    }}

    Row {
        spacing:  10
    Text {
        anchors.verticalCenter: parent.verticalCenter
        color: Colors.black
    text: "Temperature hysteresis"

    }
    SpinBox {

        id: hysterese
        from: 0
        value: 10
        to: 100 * 100
        stepSize: 10


        font.pointSize: 18
        property int decimals: 2
        property real realValue: value / 100

        validator: DoubleValidator {
            bottom: Math.min(hysterese.from, hysterese.to)
            top:  Math.max(hysterese.from, hysterese.to)
        }

        textFromValue: function(value, locale) {
            return Number(value / 100).toLocaleString(locale, 'f', hysterese.decimals) + "°"
        }

        valueFromText: function(text, locale) {
            return Number.fromLocaleString(locale, text) * 100
        }


    }

}


}
}

