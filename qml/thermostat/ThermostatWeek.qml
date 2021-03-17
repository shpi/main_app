import QtQuick 2.12
import QtQuick.Controls 2.12

import "qrc:/fonts"

Rectangle {
    id: root
    property string instancename: parent.instancename != undefined ? parent.instancename : modules.modules['Logic']['Thermostat'][0]


    color: Colors.white

    function extractSchedule() {

        var schedulelist = ''

        for (var i = 0; i < dayrepeater.count; i++) {

            for (var a = 0; a < dayrepeater.itemAt(i).children.length; a++) {
                if (dayrepeater.itemAt(i).children[a].offset !== undefined)
                    schedulelist += dayrepeater.itemAt(
                                i).children[a].value + ':' + dayrepeater.itemAt(
                                i).children[a].offset + ';'
            }

            schedulelist += '\n'
        }

        modules.loaded_instances['Logic']['Thermostat'][root.instancename].save_schedule(
                    schedulelist)
    }

    function deleteKnob() {

        for (var i = 0; i < dayrepeater.count; i++) {
            if (dayrepeater.itemAt(i).selected === true) {

                var last = dayrepeater.itemAt(i).children.length

                for (var a = 0; a < last; a++) {

                    if (dayrepeater.itemAt(
                                i).children[a].dayindex !== undefined) {
                        if (dayrepeater.itemAt(i).children[a].model > 0)
                            dayrepeater.itemAt(i).children[a].model -= 1
                    }
                }
            }
        }
    }

    function addKnob() {

        for (var i = 0; i < dayrepeater.count; i++) {
            if (dayrepeater.itemAt(i).selected === true) {

                var last = dayrepeater.itemAt(i).children.length

                for (var a = 0; a < last; a++) {

                    if (dayrepeater.itemAt(
                                i).children[a].dayindex !== undefined) {

                        dayrepeater.itemAt(i).children[a].model += 1
                    }
                }
            }
        }
    }

    Rectangle {
        id: header
        anchors.top: parent.top
        width: parent.width
        height: 100
        color: Colors.white

        RoundButton {
            id: exitbutton
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
            rotation: 90
            font.family: localFont.name
            font.pixelSize: 50
            text: Icons.arrow
            onClicked: thermostatPopup.close()
            palette.button: 'lightgrey'
            palette.buttonText: "#555"
            width: height
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: exitbutton.right
            anchors.leftMargin: 10
            text: 'Thermostat Schedule'
            color: Colors.black
            font.bold: true
            font.pixelSize:40
        }

        Row {
            anchors.right: parent.right
            anchors.rightMargin: 10
            height: parent.height
            spacing: 10

            RoundButton {
                anchors.verticalCenter: parent.verticalCenter
                font.family: localFont.name
                font.pixelSize: 50
                text: '+'
                onClicked: addKnob()
                palette.button: 'lightgrey'
                palette.buttonText: "#555"
                width: height
            }

            RoundButton {
                anchors.verticalCenter: parent.verticalCenter
                font.family: localFont.name
                font.pixelSize: 50
                text: Icons.trash
                onClicked: deleteKnob()
                palette.button: 'lightgrey'
                palette.buttonText: "#555"
                width: height
            }
        }
    }

    Flickable {
        id: scheduleFlick
        width: parent.width
        contentHeight: dayrepeater.count * 100 + 200
        height: 380
        anchors.top: header.bottom
        clip: true

        Column {
            property var week:['Weekend','Workday']
            property var weekday: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            property int schedulemode: modules.loaded_instances['Logic']['Thermostat'][root.instancename].schedule_mode

            id: weekdays
            width: parent.width
            height: dayrepeater.count * 100 + 200
            spacing: 0

            Repeater {
                id: dayrepeater

                model: weekdays.schedulemode

                ThermostatWeekDay {
                    dayname:  weekdays.schedulemode == 7 ? parent.weekday[(index % 7)] :

                              weekdays.schedulemode == 1 ? '' :

                              weekdays.schedulemode == 2 ? parent.week[(index % 2)] : ''


                    even: index % 2 ? true : false

                    Repeater {

                        id: knobrepeater
                        property real settemp: modules.loaded_instances['Logic']['Thermostat'][root.instancename].set_temp
                        property int dayindex: index
                        model: modules.loaded_instances['Logic']['Thermostat'][root.instancename].schedule[index] !== undefined ? modules.loaded_instances['Logic']['Thermostat'][root.instancename].schedule[index].length : 1

                        ThermostatWeekKnob {
                            value:  modules.loaded_instances['Logic']['Thermostat'][root.instancename].schedule[knobrepeater.dayindex][index] !== undefined ? modules.loaded_instances['Logic']['Thermostat'][root.instancename].schedule[knobrepeater.dayindex][index][0] : 1440
                            offset: modules.loaded_instances['Logic']['Thermostat'][root.instancename].schedule[knobrepeater.dayindex][index] !== undefined ? modules.loaded_instances['Logic']['Thermostat'][root.instancename].schedule[knobrepeater.dayindex][index][1] : 0


                            to: 1440
                            from: 0
                        }
                    }
                }
            }
        }
    }

    Row {
        anchors.top: header.bottom
        height: 380
        width: parent.width - 80 //weekknob width
        spacing: ((parent.width) / 14) + 1
        anchors.horizontalCenter: parent.horizontalCenter

        Repeater {
            model: 13

            Rectangle {
                color: Colors.black
                width: 1
                height: parent.height
                anchors.top: parent.top

                Label {

                    anchors.horizontalCenter: parent.horizontalCenter
                    x: header.height + 5
                    text: index * 2
                    font.pixelSize: 24
                    color: Colors.black
                }

                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    text: index * 2
                    font.pixelSize: 24
                    color: Colors.black
                }
            }
        }
    }

    Loader {
        asynchronous: true
        property int value: 0
        id: loader
        width: parent.width
        height: 290
        anchors.centerIn: parent
        source: "ThermostatKnobSlider.qml"
        visible: false
    }
}
