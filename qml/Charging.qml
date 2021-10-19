import QtQuick 2.15

import QtGraphicalEffects 1.12

import QtQuick.Particles 2.0

import "qrc:/fonts"

Item {

    anchors.fill: parent






ParticleSystem {
    anchors.fill: parent


    Image {
    id: tesla
    source: "https://static-assets.tesla.com/configurator/compositor?&options=CPF1,APBS,DV2W,IBB0,PPSB,PRM30,SC04,$PPSB,$W38B,$DV2W,$MT302,$IN3PB&view=STUD_3QTR&model=m3&size=1441&bkba_opt=1&version=0.0.25"
    width: parent.width * 0.9
    fillMode: Image.PreserveAspectFit
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 20
    anchors.horizontalCenter: parent.horizontalCenter

    }


    Image {
    id:photovoltaik
    source: "./photovoltaic.png"
    width: parent.width/1.5
    fillMode: Image.PreserveAspectFit

    anchors.top: parent.top
    anchors.topMargin: 20
    anchors.horizontalCenter: parent.horizontalCenter

    }


    ImageParticle {
        groups: ["C"]
        anchors.fill: parent
        source: "qrc:///particleresources/star.png"
        color:"#F0F000"
        redVariation: 0.8
    }

    Emitter {
        id: cemitter
        group: "C"
        anchors.top: photovoltaik.bottom
        anchors.horizontalCenter: photovoltaik.horizontalCenter
        anchors.horizontalCenterOffset: -30
        emitRate: 200
        NumberAnimation on emitRate {
            loops: Animation.Infinite
             running: true
             duration: 1000
             from: 50; to: 200
           }
        lifeSpan: 2600
        size: 32
        sizeVariation: 5
        velocity: AngleDirection {  angle: 90; magnitude: 80; magnitudeVariation: 40}
        acceleration: AngleDirection { angle:90; magnitude: 80 }
        width: emitRate / 4
        height: 20

    }

    //! [C]
    Affector {
        groups: ["C"]
        anchors.horizontalCenter: tesla.horizontalCenter
        anchors.horizontalCenterOffset: -  cemitter.emitRate / 4
        anchors.top: tesla.verticalCenter
        anchors.topMargin: 50
        width: tesla.width
        height: tesla.height
        once: false
        relative: false
        velocity: AngleDirection {  angle: 350; magnitude: 300; magnitudeVariation: 40; angleVariation:5}

    }
    //! [C]






}
}



