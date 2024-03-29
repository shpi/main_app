import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/fonts"

Item {
    ListView {
        id: inputsview
        anchors.fill: parent
        clip: true
        cacheBuffer: 20
        model: inputs.searchList
        delegate: inputDelegate
        header:  Rectangle {
            width: parent.width
            height: 70
            color: "transparent"
            Text {
                id: title
                width: parent.width
                text: 'Audio Settings'
                font.bold: true
                font.pixelSize: 32
                color: Colors.black
                anchors.left: parent.left
                height: 70
                padding: 10
            }
        }


    

    Component {
        id: inputDelegate
        Rectangle {
            id: wrapper
            property int sensorvalue: value
            property int slidermin: min !== undefined ? min : 0 // Default to 0 if min is undefined
            property int slidermax: max !== undefined ? max : 100 // Default to 100 if max is undefined



            height: 110
            width: inputsview.width
            color: index % 2 === 0 ? Colors.white : "transparent"

            Row {
                spacing: 10
                width: parent.width
                height: parent.height

                Text {
                    horizontalAlignment: Text.AlignHCenter
                    anchors.verticalCenter: parent.verticalCenter
                    text: description + ' '
                    font.pixelSize: 24
                    color: Colors.black
                    wrapMode: Text.WordWrap
                    width: parent.width - 220
                }

                Loader {
                    anchors.verticalCenter: parent.verticalCenter
                    asynchronous: true
                    sourceComponent: selectSourceComponent(output, type)

                    function selectSourceComponent(output, type) {
                        if (output === false) {
                            switch (type) {
                                case "percent_int": return gaugebar
                                default: return plaintext
                            }
                        } else {
                            switch (type) {
                                case "boolean":
                                case "thread": return boolswitch
                                case "enum": return enumcombo
                                case "integer": return intslider
                                default: return textfield
                            }

                        }

                    }


        // Component Definitions
    Component {
        id: plaintext
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: sensorvalue
            width: 200
            font.pixelSize: 24
            color: Colors.black
        }
    }

    Component {
        id: gaugebar
        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            width: 200
            height: 30
            color: "darkgrey"
            border.color: Colors.black

            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                height: parent.height - 2
                anchors.left: parent.left
                anchors.leftMargin: 1
                width: ((parent.width - 2) / 100) * sensorvalue
                color: Qt.rgba(1, 0.5, 0, 0.7)
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                text: sensorvalue + '%'
                font.pixelSize: 24
                color: Colors.black
            }
        }
    }

    Component {
        id: textfield
        TextField {
            onActiveFocusChanged: keyboard(this)
            anchors.verticalCenter: parent.verticalCenter
            font.pixelSize: 24
            width: 200
            color: Colors.black
            placeholderText: (output == '1' ? sensorvalue.toString() : '')
            onEditingFinished: inputs.set(path, this.text)
        }
    }


 Component {
                                id: boolswitch

                                Switch {

                                    id: switchcontrol
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    indicator: Rectangle {
                                        anchors.horizontalCenter: parent.horizontalCenter

                                        anchors.verticalCenter: switchcontrol.verticalCenter
                                        implicitWidth: 96
                                        implicitHeight: 26
                                        x: parent.leftPadding
                                        y: parent.height / 2 - height / 2
                                        radius: 26
                                        color: parent.checked ? "#17a81a" : "#cccccc"
                                        border.color: parent.checked ? "#17a81a" : "#cccccc"

                                        Rectangle {

                                            anchors.verticalCenter: parent.verticalCenter
                                            x: switchcontrol.checked ? parent.width - width : 0
                                            width: 35
                                            height: 35
                                            radius: 17
                                            color: switchcontrol.down ? "#cccccc" : "#ffffff"
                                            border.color: switchcontrol.checked ? (switchcontrol.down ? "#17a81a" : "#21be2b") : "#999999"
                                        }
                                    }

                                    checked: sensorvalue === 1 ? true : false
                                    anchors.verticalCenter: parent.verticalCenter
                                    //visible: output == '1' ? 1 : 0
                                    width: 200
                                    onToggled: inputs.set(
                                                   path,
                                                   this.checked === true ? 1 : 0)
                                }
                            }


    Component {
        id: enumcombo
        ComboBox {
            currentIndex: parseInt(sensorvalue)
            width: 200
            anchors.horizontalCenter: parent.horizontalCenter
            model: available
            onActivated: inputs.set(path, this.currentIndex)
        }
    }

    Component {
        id: intslider
        Slider {
            from: slidermin
            value: sensorvalue
            width: 200
            to: slidermax
            stepSize: step === 0 ? 1 : step
            onPressedChanged: if (!this.pressed) inputs.set(path, this.value)
        }
    }



                }
            }
        }
    }

}
}
