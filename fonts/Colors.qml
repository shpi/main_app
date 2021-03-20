pragma Singleton

import QtQuick 2.15

QtObject {
    readonly property color white: appearance.night === 1 ? "#000000" : "#ffffff"
    readonly property color black: appearance.night === 1 ? "#ffffff" : "#000000"
    readonly property color blacktrans: appearance.night === 1 ? "#33ffffff" : "#33000000"
    readonly property color whitetrans: appearance.night === 1 ? "#33000000" : "#33ffffff"
    readonly property color grey: appearance.night === 1 ? "darkgrey" : "lightgrey"
}
