import QtQuick 2.12
import QtQuick.Controls 2.12

Item {

    function formatText(count, modelData) {
        var data = count === 24 ? modelData  : modelData;
        return data.toString().length < 2 ? "0" + data : data;
    }


    function getMinutes(timestring) {
        var minutes = timestring.split(':')[1]
        return parseInt(minutes);
    }

    function getHours(timestring) {
        var hours = timestring.split(':')[0]
        return parseInt(hours);
    }



    function getIndex(path, mmodel) {

           for(var i = 0; i < mmodel.rowCount(); i++) {
               var idx = mmodel.index(i,0);
               var value = mmodel.data(idx, Qt.UserRole + 1000);
               if(path === value) {
                   return i;
               }
           }
           return 0;
}



Flickable {

    anchors.fill:parent
    contentHeight: settingscolumn.implicitHeight

Column {
    id: settingscolumn
    anchors.fill:parent
    spacing: 15
    padding: 10


    Text {

    text: "Backlight Range"
    color: "white"
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
        first.value:  appearance.minbacklight
        second.value: appearance.maxbacklight
        second.onMoved: appearance.maxbacklight = second.value
        first.onMoved: appearance.minbacklight = first.value

        Label {
            anchors.horizontalCenter: parent.first.handle.horizontalCenter
            text: parent.first.value
            color: "white"
        }

        Label {
            anchors.horizontalCenter: parent.second.handle.horizontalCenter
            text: parent.second.value
            color: "white"
        }

        Label {
            text: "MIN"
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.left
            color: "white"
        }

        Label {
            text: "MAX"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            color: "white"
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
            color: "white"
        }

        Label {
            anchors.right: parent.left
            anchors.rightMargin: 10
            text: "Dim Backlight after"
            color: "white"
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
            color: "white"
        }

        Label {
            anchors.right: parent.left
            anchors.rightMargin: 10
            text: "Turn display off after"
            color: "white"
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
            color: "white"
        }

        Label {
            anchors.right: parent.left
            anchors.rightMargin: 10
            text: "Jump to home after"
            color: "white"
        }

    }


    Text {

        text: "Nightmode"
        color: "white"
        font.bold: true
        anchors.topMargin: 20

    }




    Component {
           id: delegateTime

           Label {
               text: formatText(Tumbler.tumbler.count, modelData)
               opacity: appearance.night_mode === 0 ? 1.0 - Math.abs(Tumbler.displacement) / (Tumbler.tumbler.visibleItemCount / 2) : 1.0 - Math.abs(Tumbler.displacement)
               horizontalAlignment: Text.AlignHCenter
               verticalAlignment: Text.AlignVCenter
               color: "white"




           }
       }

    ButtonGroup { id: nightGroup }

Row {
    anchors.horizontalCenter: parent.horizontalCenter
    RadioButton {
           checked: appearance.night_mode === -1 ? true : false
           onReleased: {
               if (this.checked)  appearance.night_mode = -1
                }

           text: qsTr("off")
           ButtonGroup.group: nightGroup
           contentItem: Text {
                   text: parent.text
                   color: "white"
                   leftPadding: parent.indicator.width + parent.spacing
                   verticalAlignment: Text.AlignVCenter
               }
    }

    RadioButton {
           checked: appearance.night_mode === 0 ? true : false
           onReleased: {
               if (this.checked)  appearance.night_mode = 0
                }

           text: qsTr("manual")
           ButtonGroup.group: nightGroup
           contentItem: Text {
                   text: parent.text
                   color: "white"
                   leftPadding: parent.indicator.width + parent.spacing
                   verticalAlignment: Text.AlignVCenter
               }
    }


    RadioButton {
           checked: appearance.night_mode === 1 ? true : false
           onReleased: {
                        if (this.checked)  appearance.night_mode = 1
                         }

           text: qsTr("auto")
           contentItem: Text {
                   text: parent.text
                   color: "white"
                   leftPadding: parent.indicator.width + parent.spacing
                   verticalAlignment: Text.AlignVCenter
               }
           ButtonGroup.group: nightGroup
       }
}

    Frame {

        padding: 0
        anchors.horizontalCenter: parent.horizontalCenter
        visible: appearance.night_mode === 0 ? true : false
        Row {




           Tumbler {
                id: hoursTumbler
                model: 24

                delegate: delegateTime
                visibleItemCount: 3
                height: appearance.night_mode === 0 ? 100 : 50
                onCurrentItemChanged:
                    if (appearance.night_mode === 0)
                    appearance.night_mode_start = hoursTumbler.currentIndex.toString() + ':' + minutesTumbler.currentIndex.toString()

            }
           Text {
               anchors.verticalCenter: parent.verticalCenter
               text: ":"
               color: "white"
               font.bold: true


           }
            Tumbler {
                id: minutesTumbler
                model: 60

                delegate: delegateTime
                visibleItemCount: 3
                height: appearance.night_mode === 0 ? 100 : 50
                onCurrentItemChanged:  if (appearance.night_mode === 0)  appearance.night_mode_start = hoursTumbler.currentIndex.toString() + ':' + minutesTumbler.currentIndex.toString()

            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 20
                anchors.rightMargin: 20
                text: "til"
                color: "white"
                font.bold: true


            }

            Tumbler {
                 id: hoursTumbler2
                 model: 24

                 delegate: delegateTime
                 visibleItemCount: 3
                 height: appearance.night_mode === 0 ? 100 : 50
                 onCurrentItemChanged:  if (appearance.night_mode === 0)  appearance.night_mode_end = hoursTumbler2.currentIndex.toString() + ':' + minutesTumbler2.currentIndex.toString()

             }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: ":"
                color: "white"
                font.bold: true


            }
            Tumbler {
                id: minutesTumbler2
                model: 60
                delegate: delegateTime
                visibleItemCount: 3
                height: appearance.night_mode === 0 ? 100 : 50
                onCurrentItemChanged: if (appearance.night_mode === 0)  appearance.night_mode_end = hoursTumbler2.currentIndex.toString() + ':' + minutesTumbler2.currentIndex.toString()

            }

        }
    }





    ComboBox {
        id: combo_night_mode_start
        visible: appearance.night_mode === 1 ? true : false
        Label {
        anchors.right: parent.left
        anchors.rightMargin: 10
        text: "start"
        color: "white"
        }

        anchors.horizontalCenter: parent.horizontalCenter
        width: 600
        model: inputs.typeList
        textRole: 'path'
        onFocusChanged:  appearance.night_mode_start = this.currentText

    }


    ComboBox {
        id: combo_night_mode_end
        visible: appearance.night_mode === 1 ? true : false
        Label {
        anchors.right: parent.left
        anchors.rightMargin: 10
        text: "end"
        color: "white"
        }
        anchors.horizontalCenter: parent.horizontalCenter
        width: 600
        model: inputs.typeList
        textRole: 'path'
        onFocusChanged:  appearance.night_mode_end = this.currentText
    }

    Text {

        text: "Track Input Devices for activity"
        color: "white"
        font.bold: true
        anchors.topMargin: 20

    }

    Repeater {
          model: appearance.devices.list
          CheckBox { checked: appearance.devices[modelData]
                     Text {
                     anchors.left: parent.right
                     anchors.leftMargin: 10
                     color: "white"
                     text: inputs.data[modelData]['description'] }
                     onCheckStateChanged: appearance.setDeviceTrack(modelData, this.checked)

          }
      }

}

}

    Component.onCompleted: {

           inputs.set_typeList('time')

           if (appearance.night_mode === 1) {

               combo_night_mode_end.currentIndex = getIndex(appearance.night_mode_end, inputs.typeList)
               combo_night_mode_start.currentIndex = getIndex(appearance.night_mode_start, inputs.typeList)


               }
           else {

               minutesTumbler.currentIndex = getMinutes(appearance.night_mode_start)
               hoursTumbler.currentIndex = getHours(appearance.night_mode_start)

               minutesTumbler2.currentIndex = getMinutes(appearance.night_mode_end)
               hoursTumbler2.currentIndex = getHours(appearance.night_mode_end)


           }


           }

    }
