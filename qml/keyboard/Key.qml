import QtQuick 2.0

Item {
    id: root

    property alias mainLabel: mainLabelItem.text
    property alias secondaryLabels: secondaryLabelsItem.text
    property bool isChekable: false
    property bool isChecked: false
    property int bounds: 2
    property alias mainFont: mainLabelItem.font
    property alias secondaryFont: secondaryLabelsItem.font
    property alias mainFontColor: mainLabelItem.color
    property alias secondaryFontColor: secondaryLabelsItem.color
    property color keyColor: "gray"
    property color keyPressedColor: "black"

    signal clicked
    signal alternatesClicked(string symbol)

    Rectangle {
        id: backgroundItem
        radius: 5
        anchors.fill: parent
        anchors.margins: root.bounds
        color: isChecked || mouseArea.pressed ? keyPressedColor : keyColor

        Text {
            id: secondaryLabelsItem
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            color: "white"
            font.pixelSize: 19
            font.family: localFont.name
            font.capitalization: allUpperCase ? Font.AllUppercase : Font.MixedCase
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            id: mainLabelItem
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            color: "white"
            font.pixelSize: 50
            font.family: localFont.name
            font.capitalization: allUpperCase ? Font.AllUppercase : Font.MixedCase
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }

    Row {
        id: alternatesRow
        property int selectedIndex: -1
        visible: false
        anchors.bottom: backgroundItem.top

        anchors.right: root.repindex > 5 ? parent.right : undefined
        anchors.left: root.repindex < 5 ? parent.left : undefined
        layoutDirection: root.repindex > 5 ? Qt.RightToLeft : Qt.LeftToRight

        Repeater {
            model: secondaryLabels.length

            Rectangle {
                color: alternatesRow.selectedIndex == index ? mainLabelItem.color : keyPressedColor
                height: backgroundItem.height
                width: backgroundItem.width
                radius: 5

                Text {
                    anchors.centerIn: parent
                    text: secondaryLabels[index]
                    font: mainLabelItem.font

                    color: alternatesRow.selectedIndex == index ? keyPressedColor : mainLabelItem.color
                }
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        onPressAndHold: alternatesRow.visible = true

        onClicked: {
            if (isChekable)
                isChecked = !isChecked
            root.clicked()
        }

        onReleased: {
            alternatesRow.visible = false
            if (alternatesRow.selectedIndex > -1)
                root.alternatesClicked(
                            secondaryLabels[alternatesRow.selectedIndex])
        }

        onMouseYChanged: {

            if (mouseY < 10)
                alternatesRow.visible = true
        }

        onMouseXChanged: {

            if (root.repindex > 5) {

                alternatesRow.selectedIndex
                        = (mouseY < 0 && (-mouseX + keyWidth)
                           > 0) ? Math.floor(
                                      (-mouseX + keyWidth) / backgroundItem.width) : -1
            } else {

                alternatesRow.selectedIndex
                        = (mouseY < 0
                           && mouseX > 0) ? Math.floor(
                                                mouseX / backgroundItem.width) : -1
            }
        }
    }
}
