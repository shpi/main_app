import QtQuick 2.0
import "../../fonts/"

Rectangle {
    id: root
    property var textfield: parent.textfield
    property alias source: keyboardItem.source
    property alias keyWidth: keyboardItem.keyWidth
    property alias keyHeight: keyboardItem.keyHeight
    property alias bounds: keyboardItem.bounds
    property alias mainFont: keyboardItem.mainFont
    property alias mainFontColor: keyboardItem.mainFontColor
    property alias secondaryFont: keyboardItem.secondaryFont
    property alias secondaryFontColor: keyboardItem.secondaryFontColor
    property alias keyColor: keyboardItem.keyColor
    property alias keyPressedColor: keyboardItem.keyPressedColor

    color: Colors.white
    width: 800
    height: 480

    Rectangle {
        width: keyboardItem.keyWidth * 10
        anchors.horizontalCenter: parent.horizontalCenter
        height: 70
        border.width: 1
        border.color: "white"
        color: "transparent"
        radius: 10
        clip: true


    TextInput {

        anchors.verticalCenter: parent.verticalCenter
        anchors.fill:parent
        id: valueText
        text: textfield !== undefined ? textfield.text : ''
        font.pixelSize: 50
        color: Colors.black

    }}

    KeyboardItem {
        id: keyboardItem
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: 30
        source: "keyboard_us.xml"

        onEnterClicked: {
            textfield.text = valueText.text
            textfield.focus = false
            keyboardPopup.close()}

        onKeyClicked: {
                       if (key == '\b') valueText.text = valueText.text.substring(0, valueText.text.length - 1)
                       else valueText.text += key
        }
        onSwitchSource: root.source = source
    }
}

