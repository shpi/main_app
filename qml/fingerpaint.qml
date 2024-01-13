import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls 1.4

import "qrc:/fonts"

Rectangle {
    anchors.fill: parent
    color: "black"


    // Properties for paint color and width
    property color selectedColor: "red"
    property int lineWidth: 5

    // Button to clear the canvas
    Button {
        id: clearButton
        text: "Clear"
        anchors.top: lockswipe.bottom
        anchors.right: parent.right
        anchors.margins: 10
        onClicked: {
            myCanvas.clear();
        }
    }

    // Button to toggle swipe
    Button {
        id:lockswipe
        text: swipeView && !swipeView.interactive ? "Unlock Swiping" : "Lock Swiping"
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10
        z: 1
        onClicked: {
            if (swipeView) {
                swipeView.interactive = !swipeView.interactive;
            }
        }
    }

    // Color picker for selecting paint color
    ComboBox {
        id: colorPicker
        model: ["red", "blue", "green", "yellow", "black"]
        anchors.top: clearButton.bottom
        anchors.right: parent.right
        anchors.margins: 10
        onCurrentTextChanged: {
            selectedColor = currentText;
        }
    }

    // Slider for selecting line width
    Slider {
        id: widthSlider
        anchors.top: colorPicker.bottom
        anchors.right: parent.right
        anchors.margins: 10
        minimumValue: 1
        maximumValue: 10
        onValueChanged: {
            lineWidth = value;
        }
    }


Button {
    text: "Save Image"
    anchors.top: widthSlider.bottom
    anchors.right: parent.right
    anchors.margins: 10
    onClicked: {
        myCanvas.saveCanvasImage();
    }
}


    Canvas {
        id: myCanvas
        anchors.fill: parent
        property var lastPosById
        property var posById

        property var colors: ["#00BFFF", "#FF69B4", "#F0E68C", "#ADD8E6", "#FFA07A", "#9370DB", "#98FB98", "#DDA0DD", "#FF6347", "#40E0D0"]

        anchors.rightMargin: 100

        function clear() {
            var ctx = getContext('2d');
            ctx.clearRect(0, 0, width, height);
            lastPosById = {};
            posById = {};



        requestPaint(); // Request a repaint to update the canvas immediately
   
        }     


function saveCanvasImage() {
        var now = new Date();
        var fileName = Qt.formatDateTime(now, "MM-dd-hh-mm") + ".jpg";

        myCanvas.grabToImage(function(result) {
            result.saveToFile("backgrounds/paint-" + fileName);
        });
    }


   onPaint: {
            var ctx = getContext('2d')
            if (lastPosById == undefined) {
                lastPosById = {}
                posById = {}
            }

            for (var id in lastPosById) {
                //ctx.strokeStyle = colors[id % colors.length]
         
                ctx.strokeStyle = selectedColor;
                ctx.lineWidth = lineWidth;
                ctx.beginPath()
                ctx.moveTo(lastPosById[id].x, lastPosById[id].y)
                ctx.lineTo(posById[id].x, posById[id].y)
                ctx.stroke()

                // update lastpos
                lastPosById[id] = posById[id]
            }
        }

        MultiPointTouchArea {
            anchors.fill: parent

            onPressed: {
                for (var i = 0; i < touchPoints.length; ++i) {
                    var point = touchPoints[i]
                    // update both so we have data
                    myCanvas.lastPosById[point.pointId] = {
                        "x": point.x,
                        "y": point.y
                    }
                    myCanvas.posById[point.pointId] = {
                        "x": point.x,
                        "y": point.y
                    }
                }
            }
            onUpdated: {
                for (var i = 0; i < touchPoints.length; ++i) {
                    var point = touchPoints[i]
                    // only update current pos, last update set on paint
                    myCanvas.posById[point.pointId] = {
                        "x": point.x,
                        "y": point.y
                    }
                }
                myCanvas.requestPaint()
            }
            onReleased: {
                for (var i = 0; i < touchPoints.length; ++i) {
                    var point = touchPoints[i]
                    delete myCanvas.lastPosById[point.pointId]
                    delete myCanvas.posById[point.pointId]
                }
            }
        }
    }
}
