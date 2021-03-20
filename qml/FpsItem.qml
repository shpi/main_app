import QtQuick 2.15
import QtQuick.Window 2.2

Rectangle {
    id: root
    property int frameCounter: 0
    property int frameCounterAvg: 0
    property int counter: 0
    property int fps: 0
    property int fpsAvg: 0

    readonly property real dp: Screen.pixelDensity * 25.4/160

    color: "black"
    width:  childrenRect.width + 10*dp;
    height: childrenRect.height + 10*dp;

    Rectangle{
        id: spinnerImage
        anchors.verticalCenter: parent.verticalCenter
        x: 4 * dp
        width: 20 * dp
        height: 20 * dp

        NumberAnimation on rotation {
            from:0
            to: 360
            duration: 800
            loops: Animation.Infinite
        }
        onRotationChanged: frameCounter++;
    }

    Text {
        anchors.left: spinnerImage.right
        anchors.leftMargin: 8 * dp
        anchors.verticalCenter: spinnerImage.verticalCenter
        color: "#c0c0c0"
        font.pixelSize: 18 * dp
        text: "Ø " + root.fpsAvg + " | " + root.fps + " fps"
    }

    Timer {
        interval: 2000
        repeat: true
        running: true
        onTriggered: {
            frameCounterAvg += frameCounter;
            root.fps = frameCounter/2;
            counter++;
            frameCounter = 0;
            if (counter >= 3) {
                root.fpsAvg = frameCounterAvg/(2*counter)
                frameCounterAvg = 0;
                counter = 0;
            }
        }
    }
}
