import QtQuick 2.12
import QtQuick.Controls 2.12


Item {
    anchors.fill: parent
Column {
    anchors.fill: parent

    Row {
        spacing: 5
     Text {
     anchors.verticalCenter: parent.verticalCenter

     text: "Update Interval in seconds"
      }

        TextField {

        font.pointSize: 14
        text: weather[0].interval
        onEditingFinished: weather[0].interval = parseInt(text)



        }

    }

Row {
    spacing: 5
 Text {
 anchors.verticalCenter: parent.verticalCenter

 text: "OpenWeather API Key"
  }

    TextField {

    font.pointSize: 14
    text: weather[0].api_key

    onEditingFinished: weather[0].api_key = text



    }

}
    Row {
        spacing: 20

        TextField {
            id: city_tf
            placeholderText: qsTr("City")
            font.pointSize: 14
            selectByMouse: true
        }
        Button {
            text: "Search"

            onClicked: {
                weather[0].update_cities(city_tf.text)
            }
        }

        Button {
            text: "Update"

            onClicked: {
                weather[0].update()
            }
        }
    }
    ScrollView {
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        height: 400

        ScrollBar.vertical.policy: ScrollBar.AlwaysOn

        ListView {

            clip: true
            orientation: Qt.Vertical
            flickableDirection: Flickable.VerticalFlick
            boundsBehavior: Flickable.StopAtBounds
            id: cityview
            width: parent.width
            model: weather[0].cities
            
            delegate: contactDelegate
            focus: true

            Component {
                id: contactDelegate

                Rectangle {
                    property int delindex: index
                    id: wrapper
                    height: 60
                    width: cityview.width
                    color: index % 2 === 0 ? "lightgrey" : "white"
                    Row {
                        spacing: 10
                        height: parent.height

                        RoundButton {
                            radius: height / 2
                            anchors.verticalCenter: parent.verticalCenter
                            visible: wrapper.ListView.isCurrentItem ? true : false
                            text: "\u2713 set"

                            onClicked: {

                                weather[0].lon = lon
                                weather[0].lat = lat
                                weather[0].city = name
                                weather[0].update()
                            }
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: '<b>' + name + ' ' + stat + '</b>, ' + country
                            font.pointSize: 12
                            MouseArea {
                                anchors.fill: parent
                                onClicked: cityview.currentIndex = wrapper.delindex
                            }
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: 'Latitude: ' + lat + ', Longitude: ' + lon
                            font.pointSize: 8
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: weather[0]
        onCitiesChanged: {
            cityview.update()
        }
    }
}
}
