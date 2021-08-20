pragma Singleton

import QtQuick 2.15

QtObject {
    readonly property color white: appearance.night_active ? "#000000" : "#ffffff"
    readonly property color white2: appearance.night_active ? "#111111" : "#eeeeee"
    readonly property color black: appearance.night_active ? "#ffffff" : "#000000"
    readonly property color black2: appearance.night_active ? "#eeeeee" : "#111111"
    readonly property color blacktrans: appearance.night_active ? "#33ffffff" : "#33000000"
    readonly property color whitetrans: appearance.night_active ? "#33000000" : "#33ffffff"
    readonly property color grey: appearance.night_active ? "darkgrey" : "lightgrey"
}
