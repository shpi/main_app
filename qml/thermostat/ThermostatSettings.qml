import QtQuick 2.12
import QtQuick.Controls 2.12

import "../../fonts/"

Item {
   anchors.fill: parent



    // Temperaturreduzierung bei Abwesenheit 1′ pro 24h ? Urlaubsmodus

Column {

    anchors.centerIn: parent
    spacing:  20

    Row {
        spacing:  10
        Text {
        anchors.verticalCenter: parent.verticalCenter
        text: "Auto-Away"
        }
    Switch {}

    Text {
    anchors.verticalCenter: parent.verticalCenter
    text: "Valveprotection"
    }
Switch {}

    }


Row {
    spacing:  10
    Text {
    anchors.verticalCenter: parent.verticalCenter
    text: "Temperature offset"
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

    Row {
        spacing: 20

    RoundButton {
        height: width
        font.family: localFont.name
        text: Icons.schedule
        font.pointSize: 50
        enabled: false
        }


Frame {
    id: scheduleframe




    Grid {
        columns: 2
        spacing: 2
        RadioButton {
            checked: true
            text: qsTr("No schedule")
        }
        RadioButton {
            text: qsTr("Daily")
        }

        RadioButton {
            text: qsTr("Weekly")
        }
        RadioButton {
            text: qsTr("Monthly")
        }


    }

}
}
}

}

