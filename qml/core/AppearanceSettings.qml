import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/fonts"

Item {



function formatText(count, modelData) {
    return modelData.toString().padStart(2, '0');
}

function getMinutes(timestring) {
    return parseInt(timestring.split(':')[1]);
}

function getHours(timestring) {
    return parseInt(timestring.split(':')[0]);
}



function getIndex(path, mmodel) {
    for (var i = 0; i < mmodel.rowCount(); i++) {
        if (path === mmodel.data(mmodel.index(i, 0), Qt.UserRole + 1000)) {
            return i;
        }
    }
    return 0;
}

    
    
    ListModel {
        id : settingsModel
        ListElement {
            name : "Backlight Range"
            expanded : true
            component : "backlightrange"
        }
        ListElement {
            name : "Timing Settings"
            expanded : false
            component : "timingsettings"
        }
        ListElement {
            name : "Nightmode Settings"
            expanded : false
            component : "nightmodesettings"
        }
        ListElement {
            name : "Timezone Setting"
            expanded : false
            component : "timezonesettings"
        }
        ListElement {
            name : "Tracked Input Devices "
            expanded : false
            component : "trackeddevices"
        }
    }
    
    
    
    ListView {
        anchors.fill : parent
        id : settingsview
        model : settingsModel
        delegate : Rectangle {
            id : settingsDelegate
            width: settingsview.width
            height : expanded
                ? 80 + delegateLoader.implicitHeight
                : 80
            color : index % 2 === 0
                ? "transparent"
                : Colors.whitetrans
            Text {
                id : textitem
                color : Colors.black
                font.pixelSize : 40
                text : name
                anchors.top : parent.top
                anchors.left : parent.left
                anchors.leftMargin : 30
                anchors.right : parent.right
                anchors.topMargin : 20
                MouseArea {
                    anchors.fill : parent
                    onClicked : {
                        model.expanded = !model.expanded
                    }
                }
            }
            Rectangle {
                id : seperator
                anchors.top : settingsDelegate.top
                anchors.left : parent.left
                anchors.right : parent.right
                anchors.topMargin : 80
                height : 1
                color : "#424246"
            }
            Text {
                anchors.topMargin : 20
                anchors.right : parent.right
                anchors.rightMargin : 20
                text : Icons.arrow
                rotation : expanded
                    ? 0
                    : 270
                font.family : localFont.name
                color : Colors.black
                anchors.top : parent.top
            }
            Loader {
                id : delegateLoader
                anchors.top : seperator.bottom
                width : parent.width
                visible : expanded
                active : expanded
                sourceComponent : switch (component) {
                    case "nightmodesettings":
                        return nightmodesettings
                    case "timezonesettings":
                        return timezonesettings
                    case "backlightrange":
                        return backlightrange
                    case "timingsettings":
                        return timingsettings
                    case "trackeddevices":
                        return trackeddevices
                }
            }
        }
    
    
    
    
    }







    Component {
        id : nightmodesettings

        Rectangle {
         anchors.centerIn:parent
         color: "transparent"
         height: nightmodecolumn.height + 60

        ButtonGroup {
            id : nightGroup
        }

        Column {
        anchors.centerIn:parent
        id: nightmodecolumn
        padding: 30
        spacing: 20

        Row {
            spacing : 20

            RadioButton {
                font.pixelSize: 30
                checked : appearance.night_mode === 0
                onReleased : {
                    if (this.checked) 
                        appearance.night_mode = 0
                    
                }
                text : qsTr("off")
                ButtonGroup.group : nightGroup
                contentItem : Text {
                    text : parent.text
                     font.pixelSize: 30
                  
                    color : Colors.black
                    leftPadding : parent.indicator.width + parent.spacing
                    verticalAlignment : Text.AlignVCenter
                }
            }
            RadioButton {
                checked : appearance.night_mode === 1
                font.pixelSize: 30

                onReleased : {
                    if (this.checked) 
                        appearance.night_mode = 1
                    
                }
                text : qsTr("on")
                ButtonGroup.group : nightGroup
                contentItem : Text {
                    text : parent.text
                    font.pixelSize: 30
                    color : Colors.black
                    leftPadding : parent.indicator.width + parent.spacing
                    verticalAlignment : Text.AlignVCenter
                }
            }
            RadioButton {
                font.pixelSize: 30

                checked : appearance.night_mode === 2
                onReleased : {
                    if (this.checked) 
                        appearance.night_mode = 2
                    
                    appearance.night_mode_start = hoursTumbler.currentIndex.toString() + ':' + minutesTumbler
                        .currentIndex
                        .toString()
                        appearance
                        .night_mode_end = hoursTumbler2.currentIndex.toString() + ':' + minutesTumbler2.currentIndex.toString()
                }
                text : qsTr("timerange")
                ButtonGroup.group : nightGroup
                contentItem : Text {
                    font.pixelSize: 30
                    text : parent.text
                    color : Colors.black
                    leftPadding : parent.indicator.width + parent.spacing
                    verticalAlignment : Text.AlignVCenter
                }
            }
            RadioButton {
                font.pixelSize: 30

                checked : appearance.night_mode === 3
                onReleased : {
                    if (this.checked) 
                        appearance.night_mode = 3
                    
                }
                text : qsTr("dynamic")
                contentItem : Text {
                    text : parent.text
                    color : Colors.black
                    font.pixelSize: 30
                    leftPadding : parent.indicator.width + parent.spacing
                    verticalAlignment : Text.AlignVCenter
                }
                ButtonGroup.group : nightGroup
            }
        }


        Frame {
            padding : 0
            anchors.horizontalCenter : parent.horizontalCenter
            visible : appearance.night_mode === 2
            Row {
                Tumbler {
                    id : hoursTumbler
                    model : 24
                    currentIndex : getHours(appearance.night_mode_start)
                    delegate : delegateTime
                    visibleItemCount : 3
                    height : 100
                    onCurrentIndexChanged : { // console.log('onCurrentItemChanged called')
                        if (appearance.night_mode === 2) 
                            appearance.night_mode_start = hoursTumbler.currentIndex.toString() + ':' + minutesTumbler.currentIndex.toString()
                        
                    }
                }
                Text {
                    anchors.verticalCenter : parent.verticalCenter
                    text : ":"
                    color : Colors.black
                    font.bold : true
                }
                Tumbler {
                    id : minutesTumbler
                    model : 60
                    currentIndex : getMinutes(appearance.night_mode_start)
                    delegate : delegateTime
                    visibleItemCount : 3
                    height : 100
                    onCurrentIndexChanged : {
                        if (appearance.night_mode === 2) 
                            appearance.night_mode_start = hoursTumbler.currentIndex.toString() + ':' + minutesTumbler.currentIndex.toString()
                        
                    }
                }
                Text {
                    anchors.verticalCenter : parent.verticalCenter
                    anchors.leftMargin : 20
                    anchors.rightMargin : 20
                    text : "till"
                    color : Colors.black
                    font.bold : true
                }
                Tumbler {
                    id : hoursTumbler2
                    model : 24
                    currentIndex : getHours(appearance.night_mode_end)
                    delegate : delegateTime
                    visibleItemCount : 3
                    height : 100
                    onCurrentIndexChanged : {
                        if (appearance.night_mode === 2) 
                            appearance.night_mode_end = hoursTumbler2.currentIndex.toString() + ':' + minutesTumbler2.currentIndex.toString()
                        
                    }
                }
                Text {
                    anchors.verticalCenter : parent.verticalCenter
                    text : ":"
                    color : Colors.black
                    font.bold : true
                }
                Tumbler {
                    id : minutesTumbler2
                    model : 60
                    currentIndex : getMinutes(appearance.night_mode_end)
                    delegate : delegateTime
                    visibleItemCount : 3
                    height : 100
                    onCurrentIndexChanged : {
                        if (appearance.night_mode === 2) 
                            appearance.night_mode_end = hoursTumbler2.currentIndex.toString() + ':' + minutesTumbler2.currentIndex.toString()
                        
                    }
                }
            }
        }
        ComboBox {
            id : combo_night_mode_start
            visible : appearance.night_mode === 3
            Label {
                anchors.right : parent.left
                anchors.rightMargin : 10
                text : "start"
                color : Colors.black
            }
            anchors.horizontalCenter : parent.horizontalCenter
            width : 600
            model : inputs.typeList
            textRole : 'path'
            onActivated : appearance.start_input_key = this.currentText
        }
        ComboBox {
            id : combo_night_mode_end
            visible : appearance.night_mode === 3
            Label {
                anchors.right : parent.left
                anchors.rightMargin : 10
                text : "end"
                color : Colors.black
            }
            anchors.horizontalCenter : parent.horizontalCenter
            width : 600
            model : inputs.typeList
            textRole : 'path'
            onActivated : appearance.stop_input_key = this.currentText
        }
        CheckBox {
            anchors.rightMargin : 20
            Text {
                anchors.verticalCenter : parent.verticalCenter
                wrapMode : Text.WordWrap
                width : parent.parent.width - 40
                anchors.topMargin : 20
                anchors.left : parent.right
                anchors.leftMargin : 10
                font.pixelSize: 30
                color : Colors.black
                text : 'Background Pictures in Nightmode'
            }
            Component.onCompleted : this.checked = appearance.background_night
            onCheckStateChanged : {
                appearance.background_night = this.checked
                    ? 1
                    : 0
                }
            Component {
                id : delegateTime
                Label {
                    text : formatText(Tumbler.tumbler.count, modelData)
                    horizontalAlignment : Text.AlignHCenter
                    verticalAlignment : Text.AlignVCenter
                    color : Tumbler.displacement != 0
                        ? "grey"
                        : Colors.black
                }
            }
        }
    }
}
}





    


 Component {
        id : timezonesettings
        Rectangle {
        color: "transparent"
        height: 150        

        Row {
            padding: 30
            spacing : 20
            anchors.horizontalCenter : parent.horizontalCenter
            ComboBox {
                id : continentComboBox
                width : 250
                height : 60
                model : appearance.continents
                onCurrentTextChanged : cityComboBox.model = appearance.cities(currentText)
            }
            ComboBox {
                height : 60
                id : cityComboBox
                width : 250
                visible : cityComboBox.count > 0
                model : []
            }
            Button {
                height : 60
                text : "Set"
                onClicked : appearance.set_timezone(continentComboBox.currentText, cityComboBox.currentText)
            }
            Component.onCompleted : {
                var continent = appearance.get_current_continent()
                var city = appearance.get_current_city()
                var index = continentComboBox.model.indexOf(continent)
                if (index !== -1) {
                    continentComboBox.currentIndex = index
                }
                if (cityComboBox.model.count == 0) {
                    cityComboBox.model = appearance.cities(continentComboBox.currentText)
                }
                var index = cityComboBox.model.indexOf(city)
                if (index !== -1) {
                    cityComboBox.currentIndex = index
                }
            }
        }
    }
  }


 Component {
        id : timingsettings

        Rectangle {
        anchors.centerIn:parent
        height: timingcolumn.implicitHeight + 60
        color: "transparent"

        Column {
        anchors.centerIn:parent
        id: timingcolumn
        spacing: 30
        padding: 30

        Row {
             anchors.right: parent.right
             spacing:30 
             Text {
                anchors.verticalCenter : parent.verticalCenter
                font.pixelSize : 25
                text : "Dim Backlight after"
                color : Colors.black
            }


        SpinBox {
            value : appearance.dim_timer
            font.pixelSize : 65
            stepSize : 1
            onValueChanged : appearance.dim_timer = this.value
            from : 0
            textFromValue : function (value, locale) {
                return Number(value) + "s"
            }
            valueFromText : function (text, locale) {
                return Number.fromLocaleString(locale, text)
            }
            to : 1000
        }
       }

        Row {
            anchors.right: parent.right
            spacing: 30
           Text {
                anchors.verticalCenter : parent.verticalCenter
                font.pixelSize : 25
                text : "Turn display off after"
                color : Colors.black
            }

        SpinBox {
            value : appearance.off_timer
            font.pixelSize : 65
            stepSize : 1
            textFromValue : function (value, locale) {
                return Number(value) + "s"
            }
            valueFromText : function (text, locale) {
                return Number.fromLocaleString(locale, text)
            }
            onValueChanged : appearance.off_timer = this.value
            from : 0
            to : 1000
        }
        }
       Row {
            spacing: 30
           anchors.right: parent.right
              Text {
                anchors.verticalCenter : parent.verticalCenter
                text : "Jump to home after"
                font.pixelSize : 25
                color : Colors.black
            }


        SpinBox {
            value : appearance.jump_timer
            font.pixelSize : 65
            stepSize : 1
            onValueChanged : appearance.jump_timer = this.value
            textFromValue : function (value, locale) {
                return Number(value) + "s"
            }
            valueFromText : function (text, locale) {
                return Number.fromLocaleString(locale, text)
            }
            from : 0
            to : 1000
        } }
    }
   }
  }


















    Component {
        id : backlightrange

        Rectangle {
        width: settingsview.width * 0.9
        anchors.centerIn: parent
        color: "transparent"
        height: 200

        RangeSlider {
            id : backlightslider
            snapMode : RangeSlider.SnapAlways
            from : 0
            height : 100
            width : parent.width - 130
            to : 100
            anchors.centerIn:parent
            stepSize : 2
            first.value : appearance.night === 0
                ? appearance.minbacklight
                : appearance.minbacklight_night
            second.value : appearance.night === 0
                ? appearance.maxbacklight
                : appearance.maxbacklight_night
            second.onMoved : if (appearance.night === 0) {
                appearance.maxbacklight = second.value
            } else {
                appearance.maxbacklight_night = second.value
            }
            first.onMoved : if (appearance.night === 0) {
                appearance.minbacklight = first.value
            } else {
                appearance.minbacklight_night = first.value
            }
            background : Rectangle {
                x : backlightslider.leftPadding
                y : backlightslider.topPadding + backlightslider.availableHeight / 2 - height / 2
                //implicitWidth : 200
                implicitHeight : 10
                width : backlightslider.availableWidth
                height : implicitHeight
                radius : 2
                color : "#bdbebf"
                Rectangle {
                    x : backlightslider.first.visualPosition * parent.width
                    width : backlightslider.second.visualPosition * parent.width - x
                    height : parent.height + 2
                    color : "#21be2b"
                    radius : 2
                }
            }
            Label {
                anchors.horizontalCenter : parent
                    .first
                    .handle
                    .horizontalCenter
                text : Math.round(parent.first.value)
                color : Colors.black
            }
            Label {
                anchors.horizontalCenter : parent
                    .second
                    .handle
                    .horizontalCenter
                text : Math.round(parent.second.value)
                color : Colors.black
            }
            Label {
                text : "MIN"
                anchors.verticalCenter : parent.verticalCenter
                anchors.right : parent.left
                color : Colors.black
            }
            Label {
                text : "MAX"
                anchors.verticalCenter : parent.verticalCenter
                anchors.left : parent.right
                color : Colors.black
            }
        }
    }

    }













    Component {
        id : trackeddevices
        Column {
            padding: 50
            spacing : 10
            Repeater {
                width : parent.width
                height : appearance.devices.length * 50
                model : appearance.devices
                CheckBox {
                    checked : appearance.selected_device(modelData)
                    height : 50
                    width : 100
                    Text {
                        id : subtext
                        anchors.verticalCenter : parent.verticalCenter
                        anchors.left : parent.right
                        anchors.leftMargin: 5
                        color : Colors.black
                        font.pixelSize : 24
                        text : appearance.device_description(modelData)
                        wrapMode : Text.WordWrap
                        width : parent.width - 100
                    }
                    onCheckStateChanged : {
                        appearance.setDeviceTrack(modelData, this.checked)
                    }
                }
            }
        }
    }
    





   Component.onCompleted : {
        inputs.set_typeList('time')
        if (appearance.night_mode === 3) {
            combo_night_mode_end.currentIndex = getIndex(appearance.stop_input_key, inputs.typeList)
            combo_night_mode_start.currentIndex = getIndex(appearance.start_input_key, inputs.typeList)
        }
    }   








}
