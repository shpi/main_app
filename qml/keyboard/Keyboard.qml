import QtQuick 2.15

import "../../fonts/"

Rectangle {
    id: root
    color: Colors.white
    anchors.fill: parent

    property var textfield
    onTextfieldChanged: { valueText.text = textfield.text }


    ListModel {
        id: keyboard_de

            ListElement {label: "q";   alternate: "1";  ratio: "1"}
            ListElement {label: "w"; alternate: "2"; ratio: "1"}
            ListElement {label: "e"; alternate: "3"; ratio: "1"}
            ListElement {label: "r"; alternate: "4"; ratio: "1"}
            ListElement {label: "t"; alternate: "5"; ratio: "1"}
            ListElement {label: "z"; alternate: "6"; ratio: "1"}
            ListElement {label: "u"; alternate: "ü7"; ratio: "1"}
            ListElement {label: "i"; alternate: "8"; ratio: "1"}
            ListElement {label: "o"; alternate: "ö9"; ratio: "1"}
            ListElement {label: "p"; alternate: "0"; ratio: "1"}
            ListElement {label: "a"; alternate: "ä%`~"; ratio: "1"}
            ListElement {label: "s"; alternate: "ß^"; ratio: "1"}
            ListElement {label: "d"; alternate: "*\\"; ratio: "1"}
            ListElement {label: "f"; alternate: "{+"; ratio: "1"}
            ListElement {label: "g"; alternate: "}-"; ratio: "1"}
            ListElement {label: "h"; alternate: "[="; ratio: "1"}
            ListElement {label: "j"; alternate: "]_"; ratio: "1"}
            ListElement {label: "k"; alternate: "()"; ratio: "1"}
            ListElement {label: "l"; alternate: "'\""; ratio: "1"}
            ListElement {label: "/"; alternate: "?"; ratio: "1"}
            ListElement {label: "⇑"; command:"shift"; ratio: "1.5"; checkable:"true"}
            ListElement {label: "z"; alternate: "@"; ratio: "1"}
            ListElement {label: "x"; alternate: "$"; ratio: "1"}
            ListElement {label: "c"; alternate: "!"; ratio: "1"}
            ListElement {label: "v"; alternate: ";"; ratio: "1"}
            ListElement {label: "b"; alternate: ":"; ratio: "1"}
            ListElement {label: "n"; alternate: "<"; ratio: "1"}
            ListElement {label: "m"; alternate: ">"; ratio: "1"}
            ListElement {label: "⌫"; command:"backspace"; ratio: "1.5"}
            ListElement {label: "123"; command:"source"; source:"keyboard_num"; ratio: "1.5"}
            ListElement {label: "Us"; command:"source"; source:"keyboard_us"; ratio: "1"}
            ListElement {label: " "; alternate: ""; ratio: "5"}
            ListElement {label: "."; alternate: ","; ratio: "1"}
            ListElement {label: "↵"; command:"enter"; ratio: "1.5"}
    }


    ListModel {
        id: keyboard_us

            ListElement {label: "q";   alternate: "1";  ratio: "1"}
            ListElement {label: "w"; alternate: "2"; ratio: "1"}
            ListElement {label: "e"; alternate: "3"; ratio: "1"}
            ListElement {label: "r"; alternate: "4"; ratio: "1"}
            ListElement {label: "t"; alternate: "5"; ratio: "1"}
            ListElement {label: "y"; alternate: "6"; ratio: "1"}
            ListElement {label: "u"; alternate: "7"; ratio: "1"}
            ListElement {label: "i"; alternate: "8"; ratio: "1"}
            ListElement {label: "o"; alternate: "9"; ratio: "1"}
            ListElement {label: "p"; alternate: "0"; ratio: "1"}
            ListElement {label: "a"; alternate: "%`~"; ratio: "1"}
            ListElement {label: "s"; alternate: "^"; ratio: "1"}
            ListElement {label: "d"; alternate: "*\\"; ratio: "1"}
            ListElement {label: "f"; alternate: "{+"; ratio: "1"}
            ListElement {label: "g"; alternate: "}-"; ratio: "1"}
            ListElement {label: "h"; alternate: "[="; ratio: "1"}
            ListElement {label: "j"; alternate: "]_"; ratio: "1"}
            ListElement {label: "k"; alternate: "()"; ratio: "1"}
            ListElement {label: "l"; alternate: "'\""; ratio: "1"}
            ListElement {label: "/"; alternate: "?"; ratio: "1"}
            ListElement {label: "⇑"; command:"shift"; ratio: "1.5"; checkable:"true"}
            ListElement {label: "z"; alternate: "@"; ratio: "1"}
            ListElement {label: "x"; alternate: "$"; ratio: "1"}
            ListElement {label: "c"; alternate: "!"; ratio: "1"}
            ListElement {label: "v"; alternate: ";"; ratio: "1"}
            ListElement {label: "b"; alternate: ":"; ratio: "1"}
            ListElement {label: "n"; alternate: "<"; ratio: "1"}
            ListElement {label: "m"; alternate: ">"; ratio: "1"}
            ListElement {label: "⌫"; command:"backspace"; ratio: "1.5"}
            ListElement {label: "123"; command:"source"; source:"keyboard_num"; ratio: "1.5"}
            ListElement {label: "Ru"; command:"source"; source:"keyboard_ru"; ratio: "1"}
            ListElement {label: " "; alternate: ""; ratio: "5"}
            ListElement {label: "."; alternate: ","; ratio: "1"}
            ListElement {label: "↵"; command:"enter"; ratio: "1.5"}
    }
            ListModel {
                id: keyboard_num


            ListElement {label:  "1"; ratio: "1"}
            ListElement {label:  "2"; ratio: "1"}
            ListElement {label:  "3"; ratio: "1"}
            ListElement {label:  "4"; ratio: "1"}
            ListElement {label:  "5"; ratio: "1"}
            ListElement {label:  "6"; ratio: "1"}
            ListElement {label:  "7"; ratio: "1"}
            ListElement {label:  "8"; ratio: "1"}
            ListElement {label:  "9"; ratio: "1"}
            ListElement {label:  "0"; ratio: "1"}
            ListElement {label:  "@"; ratio: "1"}
            ListElement {label:  "#"; ratio: "1"}
            ListElement {label:  "%"; ratio: "1"}
            ListElement {label:  "+"; ratio: "1"}
            ListElement {label:  "-"; ratio: "1"}
            ListElement {label:  "*"; ratio: "1"}
            ListElement {label:  "/"; ratio: "1"}
            ListElement {label:  "="; ratio: "1"}
            ListElement {label:  "("; ratio: "1"}
            ListElement {label:  ")"; ratio: "1"}
            ListElement {label:  "⇄"; command:"tab"; ratio: "1"}
            ListElement {label:  "="; ratio: "1"}
            ListElement {label:  "^"; ratio: "1"}
            ListElement {label:  ","; ratio: "1"}
            ListElement {label:  "!"; ratio: "1"}
            ListElement {label:  "?"; ratio: "1"}
            ListElement {label:  ":"; ratio: "1"}
            ListElement {label:  ";"; ratio: "1"}
            ListElement {label:  "\""; ratio: "1"}
            ListElement {label:  "⌫"; command:"backspace"; ratio: "1"}
            ListElement {label:  "Us"; command:"source"; source:"keyboard_us"; ratio: "1.25"}
            ListElement {label:  "De"; command:"source"; source: "keyboard_de"; ratio: "1.25"}

            ListElement {label:  " "; ratio: "5"}
            ListElement {label:  "."; alternate: ",!?@"; ratio: "1"}
            ListElement {label:  "↵"; command:"enter"; ratio: "1.5"}
    }

            ListModel {
                id: keyboard_ru



    ListElement {label:  "й"; alternate: "1"; ratio: "0.9"}
    ListElement {label:  "ц"; alternate: "2"; ratio: "0.9"}
    ListElement {label:  "у"; alternate: "3"; ratio: "0.9"}
    ListElement {label:  "к"; alternate: "4"; ratio: "0.9"}
    ListElement {label:  "е"; alternate: "ё5"; ratio: "0.9"}
    ListElement {label:  "н"; alternate: "6"; ratio: "0.9"}
    ListElement {label:  "г"; alternate: "7"; ratio: "0.9"}
    ListElement {label:  "ш"; alternate: "8"; ratio: "0.9"}
    ListElement {label:  "щ"; alternate: "9"; ratio: "0.9"}
    ListElement {label:  "з"; alternate: "0"; ratio: "0.9"}
    ListElement {label:  "х"; alternate: "-_"  ; ratio: "0.9"}
    ListElement {label:  "ф"; alternate: "%`~"; ratio: "0.9"}
    ListElement {label:  "ы"; alternate: "^";  ratio: "0.9"}
    ListElement {label:  "в"; alternate: "*\""; ratio: "0.9"}
    ListElement {label:  "а"; alternate: "{"; ratio: "0.9"}
    ListElement {label:  "п"; alternate: "}"; ratio: "0.9"}
    ListElement {label:  "р"; alternate: "["; ratio: "0.9"}
    ListElement {label:  "о"; alternate: "]"; ratio: "0.9"}
    ListElement {label:  "л"; alternate: "()"; ratio: "0.9"}
    ListElement {label:  "д"; alternate: "'\""; ratio: "0.9"}
    ListElement {label:  "ж"; alternate: "/"; ratio: "0.9"}
    ListElement {label:  "э"; alternate: "?"; ratio: "0.9"}
    ListElement {label:  "⇑"; command:"shift"; ratio: "0.9"; checkable: "true"}
    ListElement {label:  "я"; alternate: "@"; ratio: "0.9"}
    ListElement {label:  "ч"; alternate: "$"; ratio: "0.9"}
    ListElement {label:  "с"; alternate: "!"; ratio: "0.9"}
    ListElement {label:  "м"; alternate: ";"; ratio: "0.9"}
    ListElement {label:  "и"; alternate: ":"; ratio: "0.9"}
    ListElement {label:  "т"; alternate: "=+"; ratio: "0.9"}
    ListElement {label:  "ь"; alternate: "ъ"; ratio: "0.9"}
    ListElement {label:  "б"; alternate: "<"; ratio: "0.9"}
    ListElement {label:  "ю"; alternate: ">"; ratio: "0.9"}
    ListElement {label:  "⌫"; command:"backspace"; ratio: "0.9"}
    ListElement {label:  "123"; command:"source"; source: "keyboard_num"; ratio: "1.5"}
    ListElement {label:  "De"; command:"source"; source:"keyboard_de"; ratio: "1"}
    ListElement {label:  " "; ratio: "5"}
    ListElement {label:  "."; alternate: ","; ratio: "1"}
    ListElement {label:  "↵"; commmand:"enter"; ratio: "1.5"}
    }




        property int keyWidth: (keyboardFlow.width - (2 * keyboardFlow.padding)) / 10
        property int keyHeight: (keyboardFlow.height - (2 * keyboardFlow.padding)) / 5
        property int bounds: 2

        property color keyColor: "gray"
        property color keyPressedColor: "black"
        property bool allUpperCase: false

        signal keyClicked(string key)
        signal enterClicked
        signal backspaceClicked

        Flow {
            id: keyboardFlow
            anchors.fill: parent
            padding: 10

            Rectangle {
                width: parent.width - (2 * keyboardFlow.padding)
                height: (keyboardFlow.height - (2 * keyboardFlow.padding)) / 5
                border.width: 1
                border.color: "white"
                color: "transparent"
                radius: 10
                clip: true

                TextInput {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.fill: parent
                    id: valueText
                    font.pixelSize: 50
                    color: Colors.black
                }
            }

                    Repeater {
                        id: keyRepeater
                        anchors.fill: parent


                        model: keyboard_de

                        Key {
                            id: key
                            width: root.keyWidth * ratio
                            height: root.keyHeight
                            keyColor: root.keyColor
                            keyPressedColor: root.keyPressedColor
                            bounds: root.bounds
                            isChekable: checkable !== undefined ? checkable : false
                            isChecked: isChekable && command === "shift" && root.allUpperCase


                            mainLabel: label
                            secondaryLabels: alternate !== undefined ? alternate : ''
                            property int repindex: (keyRepeater.model === keyboard_ru) ? index % 11 : index % 10
                            onClicked: {
                                if (command) {

                                    switch (command) {
                                    case "source":
                                        if (source == 'keyboard_num') keyRepeater.model = keyboard_num
                                        else if (source == 'keyboard_us') keyRepeater.model = keyboard_us
                                        else if (source == 'keyboard_ru') keyRepeater.model = keyboard_ru
                                        else if (source == 'keyboard_de') keyRepeater.model = keyboard_de
                                        return
                                    case "shift":
                                        root.allUpperCase = !root.allUpperCase
                                        return
                                    case "backspace":
                                        root.backspaceClicked()
                                        return
                                    case "enter":
                                        root.enterClicked()
                                        return
                                    case "tab":
                                        root.keyClicked('\t')
                                        return
                                    default:
                                        return

                                    }
                                }
                                if (mainLabel.length === 1)
                                    root.emitKeyClicked(mainLabel)
                            }
                            onAlternatesClicked: root.emitKeyClicked(symbol)
                        }
                    }
                }



        function emitKeyClicked(text) {
            keyClicked(root.allUpperCase ? text.toUpperCase() : text)
        }

        onEnterClicked: {
            textfield.text = valueText.text
            textfield.focus = false
            keyboardPopup.close()
        }

        onBackspaceClicked: valueText.text = valueText.text.substring(0, valueText.text.length - 1)

        onKeyClicked: valueText.text += key

    }

