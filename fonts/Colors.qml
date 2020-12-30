pragma Singleton
import QtQuick 2.12

QtObject {
    readonly property color white: appearance.night === 1 ? "#000000" : "#ffffff"
    readonly property color black: appearance.night === 1 ? "#ffffff" : "#000000"
}
