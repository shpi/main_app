import QtQuick 2.12
import QtQuick.Controls 2.12
import "../../fonts/"

Item {
    function formatText(count, modelData) {
        var data = modelData
        if (data.toString().length < 2)
            return "0" + data
        else
            return data
    }

    function getMinutes(timestring) {
        var minutes = timestring.split(':')[1]
        return parseInt(minutes)
    }

    function getHours(timestring) {
        var hours = timestring.split(':')[0]
        return parseInt(hours)
    }

    function getIndex(path, mmodel) {
        for (var i = 0; i < mmodel.rowCount(); i++) {
            var idx = mmodel.index(i, 0)
            var value = mmodel.data(idx, Qt.UserRole + 1000)
            if (path === value) {
                return i
            }
        }
        return 0
    }

    Flickable {
        anchors.fill: parent
        contentHeight: settingscolumn.implicitHeight

        Column {
            id: settingscolumn
            anchors.fill: parent
            spacing: 15
            padding: 10

            Text {
                text: "Backlight Range"
                color: Colors.black
                font.bold: true
            }

            RangeSlider {
                id: backlightslider
                from: 0
                height: 100
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 130

                to: 100
                stepSize: 1
                first.value: appearance.minbacklight
                second.value: appearance.maxbacklight
                second.onMoved: appearance.maxbacklight = second.value
                first.onMoved: appearance.minbacklight = first.value

                background: Rectangle {
                    x: backlightslider.leftPadding
                    y: backlightslider.topPadding + backlightslider.availableHeight / 2 - height / 2
                    implicitWidth: 200
                    implicitHeight: 8
                    width: backlightslider.availableWidth
                    height: implicitHeight
                    radius: 2
                    color: "#bdbebf"

                    Rectangle {
                        x: backlightslider.first.visualPosition * parent.width
                        width: backlightslider.second.visualPosition * parent.width - x
                        height: parent.height
                        color: "#21be2b"
                        radius: 2
                    }
                }

                Label {
                    anchors.horizontalCenter: parent.first.handle.horizontalCenter
                    text: parent.first.value
                    color: Colors.black
                }

                Label {
                    anchors.horizontalCenter: parent.second.handle.horizontalCenter
                    text: parent.second.value
                    color: Colors.black
                }

                Label {
                    text: "MIN"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.left
                    color: Colors.black
                }

                Label {
                    text: "MAX"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.right
                    color: Colors.black
                }
            }

            SpinBox {
                value: appearance.dim_timer
                anchors.horizontalCenter: parent.horizontalCenter
                stepSize: 1
                onValueChanged: appearance.dim_timer = this.value
                from: 0
                to: 1000
                Label {
                    anchors.left: parent.right
                    anchors.leftMargin: 10
                    text: "seconds inactivity."
                    color: Colors.black
                }

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "Dim Backlight after"
                    color: Colors.black
                }
            }

            SpinBox {
                value: appearance.off_timer
                anchors.horizontalCenter: parent.horizontalCenter
                stepSize: 1
                onValueChanged: appearance.off_timer = this.value
                from: 0
                to: 1000
                Label {
                    anchors.left: parent.right
                    anchors.leftMargin: 10
                    text: "seconds inactivity."
                    color: Colors.black
                }

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "Turn display off after"
                    color: Colors.black
                }
            }

            SpinBox {
                value: appearance.jump_timer
                anchors.horizontalCenter: parent.horizontalCenter
                stepSize: 1
                onValueChanged: appearance.jump_timer = this.value
                from: 0
                to: 1000
                Label {
                    anchors.left: parent.right
                    anchors.leftMargin: 10
                    text: "seconds inactivity."
                    color: Colors.black
                }

                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "Jump to home after"
                    color: Colors.black
                }
            }

            Text {
                text: "Nightmode"
                color: Colors.black
                font.bold: true
                anchors.topMargin: 20
            }

            Component {
                id: delegateTime

                Label {
                    text: formatText(Tumbler.tumbler.count, modelData)
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    color: Tumbler.displacement != 0 ? "grey" : Colors.black
                }
            }

            ButtonGroup {
                id: nightGroup
            }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                RadioButton {
                    checked: appearance.night_mode === 0
                    onReleased: {
                        if (this.checked)
                            appearance.night_mode = 0
                    }

                    text: qsTr("off")
                    ButtonGroup.group: nightGroup
                    contentItem: Text {
                        text: parent.text
                        color: Colors.black
                        leftPadding: parent.indicator.width + parent.spacing
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                RadioButton {
                    checked: appearance.night_mode === 1
                    onReleased: {
                        if (this.checked)
                            appearance.night_mode = 1
                    }

                    text: qsTr("on")
                    ButtonGroup.group: nightGroup
                    contentItem: Text {
                        text: parent.text
                        color: Colors.black
                        leftPadding: parent.indicator.width + parent.spacing
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                RadioButton {
                    checked: appearance.night_mode === 2
                    onReleased: {
                        if (this.checked)
                            appearance.night_mode = 2

                        appearance.night_mode_start = hoursTumbler.currentIndex.toString(
                                    ) + ':' + minutesTumbler.currentIndex.toString()
                        appearance.night_mode_end = hoursTumbler2.currentIndex.toString(
                                    ) + ':' + minutesTumbler2.currentIndex.toString()
                    }

                    text: qsTr("during timerange")
                    ButtonGroup.group: nightGroup
                    contentItem: Text {
                        text: parent.text
                        color: Colors.black
                        leftPadding: parent.indicator.width + parent.spacing
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                RadioButton {
                    checked: appearance.night_mode === 3
                    onReleased: {
                        if (this.checked)
                            appearance.night_mode = 3
                    }

                    text: qsTr("dynamic timerange")
                    contentItem: Text {
                        text: parent.text
                        color: Colors.black
                        leftPadding: parent.indicator.width + parent.spacing
                        verticalAlignment: Text.AlignVCenter
                    }
                    ButtonGroup.group: nightGroup
                }
            }

            Frame {
                padding: 0
                anchors.horizontalCenter: parent.horizontalCenter
                visible: appearance.night_mode === 2
                Row {
                    Tumbler {
                        id: hoursTumbler
                        model: 24
                        currentIndex: getHours(appearance.night_mode_start)
                        delegate: delegateTime
                        visibleItemCount: 3
                        height: 100
                        onCurrentIndexChanged: {
                            //console.log('onCurrentItemChanged called')
                            if (appearance.night_mode === 2)
                                appearance.night_mode_start = hoursTumbler.currentIndex.toString(
                                            ) + ':' + minutesTumbler.currentIndex.toString()
                        }
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: ":"
                        color: Colors.black
                        font.bold: true
                    }

                    Tumbler {
                        id: minutesTumbler
                        model: 60
                        currentIndex: getMinutes(appearance.night_mode_start)
                        delegate: delegateTime
                        visibleItemCount: 3
                        height: 100

                        onCurrentIndexChanged: {
                            if (appearance.night_mode === 2)
                                appearance.night_mode_start = hoursTumbler.currentIndex.toString(
                                            ) + ':' + minutesTumbler.currentIndex.toString()
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 20
                        anchors.rightMargin: 20
                        text: "till"
                        color: Colors.black
                        font.bold: true
                    }

                    Tumbler {
                        id: hoursTumbler2
                        model: 24
                        currentIndex: getHours(appearance.night_mode_end)
                        delegate: delegateTime
                        visibleItemCount: 3
                        height: 100
                        onCurrentIndexChanged: {
                            if (appearance.night_mode === 2)
                                appearance.night_mode_end = hoursTumbler2.currentIndex.toString(
                                            ) + ':' + minutesTumbler2.currentIndex.toString()
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: ":"
                        color: Colors.black
                        font.bold: true
                    }
                    Tumbler {
                        id: minutesTumbler2
                        model: 60
                        currentIndex: getMinutes(appearance.night_mode_end)
                        delegate: delegateTime
                        visibleItemCount: 3
                        height: 100
                        onCurrentIndexChanged: {
                            if (appearance.night_mode === 2)
                                appearance.night_mode_end = hoursTumbler2.currentIndex.toString(
                                            ) + ':' + minutesTumbler2.currentIndex.toString()
                        }
                    }
                }
            }

            ComboBox {
                id: combo_night_mode_start
                visible: appearance.night_mode === 3
                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "start"
                    color: Colors.black
                }

                anchors.horizontalCenter: parent.horizontalCenter
                width: 600
                model: inputs.typeList
                textRole: 'path'
                onActivated: appearance.night_mode_start = this.currentText
            }

            ComboBox {
                id: combo_night_mode_end
                visible: appearance.night_mode === 3
                Label {
                    anchors.right: parent.left
                    anchors.rightMargin: 10
                    text: "end"
                    color: Colors.black
                }
                anchors.horizontalCenter: parent.horizontalCenter
                width: 600
                model: inputs.typeList
                textRole: 'path'
                onActivated: appearance.night_mode_end = this.currentText
            }

            Text {
                text: "Nightmode Settings"
                color: Colors.black
                font.bold: true
                anchors.topMargin: 20
            }

            RangeSlider {
                id: backlightslider_night
                from: 0
                height: 100
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 130

                to: 100

                stepSize: 1
                first.value: appearance.minbacklight_night
                second.value: appearance.maxbacklight_night
                second.onMoved: appearance.maxbacklight_night = second.value
                first.onMoved: appearance.minbacklight_night = first.value

                background: Rectangle {
                    x: backlightslider_night.leftPadding
                    y: backlightslider_night.topPadding
                       + backlightslider_night.availableHeight / 2 - height / 2
                    implicitWidth: 200
                    implicitHeight: 8
                    width: backlightslider_night.availableWidth
                    height: implicitHeight
                    radius: 2
                    color: "#bdbebf"

                    Rectangle {
                        x: backlightslider_night.first.visualPosition * parent.width
                        width: backlightslider_night.second.visualPosition * parent.width - x
                        height: parent.height
                        color: "#21be2b"
                        radius: 2
                    }
                }

                Label {
                    anchors.horizontalCenter: parent.first.handle.horizontalCenter
                    text: parent.first.value
                    color: Colors.black
                }

                Label {
                    anchors.horizontalCenter: parent.second.handle.horizontalCenter
                    text: parent.second.value
                    color: Colors.black
                }

                Label {
                    text: "MIN"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.left
                    color: Colors.black
                }

                Label {
                    text: "MAX"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.right
                    color: Colors.black
                }
            }


            /* CheckBox { checked: appearance.invert_at_night === 1 ? true : false
               Text {
               anchors.left: parent.right
               anchors.leftMargin: 10
               color: Colors.black
               text: 'Invert Colors in Nightmode' }
               onCheckStateChanged:
               {
                   appearance.invert_at_night =  this.checked
                  }
    }*/
            CheckBox {
                Text {
                    anchors.left: parent.right
                    anchors.leftMargin: 10
                    color: Colors.black
                    text: 'Show Background Pictures in Nightmode'
                }
                Component.onCompleted: this.checked = appearance.background_night

                onCheckStateChanged: {
                    appearance.background_night = this.checked ? 1 : 0
                }
            }

            Text {
                text: "Track Input Devices for activity"
                color: Colors.black
                font.bold: true
                anchors.topMargin: 20
            }

            Repeater {
                model: appearance.devices.list
                CheckBox {
                    checked: appearance.devices[modelData]
                    Text {
                        anchors.left: parent.right
                        anchors.leftMargin: 10
                        color: Colors.black
                        text: inputs.data[modelData]['description']
                    }
                    onCheckStateChanged: {
                        // console.log('onCheckStateChanged called')
                        appearance.setDeviceTrack(modelData, this.checked)
                    }
                }
            }
        }
    }

    Component.onCompleted: {

        inputs.set_typeList('time')

        if (appearance.night_mode === 3) {
            combo_night_mode_end.currentIndex = getIndex(
                        appearance.night_mode_end, inputs.typeList)
            combo_night_mode_start.currentIndex = getIndex(
                        appearance.night_mode_start, inputs.typeList)
        }
    }
}
