import QtQuick 2.0
import QtQuick.Controls 2.12

Item {

    anchors.fill: parent


Dial {
    id: dialTherm
    height: parent.height * 0.8
    anchors.centerIn : parent
    enabled: false
    onPressedChanged: if (pressed == false) {
                          enabled = false
                          dialLocker.enabled = true
                      }

}

MouseArea
       {
           id: dialLocker
           anchors.fill: parent
           onDoubleClicked: {dialTherm.enabled = true
                             enabled = false
                            }
       }

}
