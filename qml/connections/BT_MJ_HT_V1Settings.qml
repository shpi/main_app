import QtQuick 2.15
import QtQuick.Controls 2.15

import "qrc:/fonts"

Item {


    ListView {


                    TextField {
                        onActiveFocusChanged: keyboard(this)
                        id: ip_textfield
                        width: 350
                        text: modules.loaded_instances['Connections']['BT_MJ_HT_V1'].name
                    }


                    RoundButton {

                        text: 'Update'
                        palette.button: "darkred"
                        palette.buttonText: "white"
                        font.pixelSize: 32
                        font.family: localFont.name
                        onClicked: {
                            modules.loaded_instances['Connections']['HTTP'][instancename].scan_devices()
                        }

            RoundButton {
                text: 'Delete Instance'
                palette.button: "darkred"
                palette.buttonText: "white"
                onClicked: {

                    settingsstackView.pop()
                    modules.remove_instance('Connections', 'HTTP', instancename)



        model: modules.loaded_instances['Connections']['HTTP'][instancename].inputList

        delegate: inputDelegate

            }
        }
    }
}
