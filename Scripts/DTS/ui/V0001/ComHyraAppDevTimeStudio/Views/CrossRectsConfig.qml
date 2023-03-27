import QtQuick 2.6

Item
{
    id: root

    property int debugLevel: 0
    
    property real axisScale: 1.0

    property rect axisRect: Qt.rect( 0, 0, 200*3, 200*3 )

    property size axisStep: Qt.size( 40, 40 )

    property point axisSpacing: Qt.point( 0, 0 )

    property size axisStepWithoutSpacing: Qt.size( axisStep.width - axisSpacing.x, axisStep.height - axisSpacing.y )

    property real axisHorizontalCount: axisRect.width / (axisStep.width * axisScale)

    property real axisVerticalCount: axisRect.height / (axisStep.height * axisScale)


    property point axisCurrentCursorPos : Qt.point( -1, -1 )

    property point axisCurrentCursorMirrorPos : Qt.point( -1, -1 )

    property variant cursorUpperColorFg: Qt.rgba( .6 , .6, .6 )
//    property variant cursorUpperColorFg: Qt.rgba( .8, .0, .0, .8 )

    property variant cursorLowerColorFg: Qt.rgba( .0, .8, .0, .8 )

    property variant crossFg: Qt.rgba( .8, .8, .8, .5 )


    property real rotAngleDefault: 360-45

    property real rotAngle: rotAngleDefault

    function 
    rotAngleReset()
    {
        rotAngle = rotAngleDefault
    }

    Behavior on rotAngle { PropertyAnimation { alwaysRunToEnd: true; duration: 200 } }


    function
    lutUpper( model_ )
    {
        return Qt.rgba( model_.value, model_.value, model_.value )
    }

    function
    lutCenter( model_ )
    {
        return "white"
    }

    function
    lutLower( model_ )
    {
        return Qt.rgba( 0.2*model_.value, 0.2, 0.2 )
    }

    property bool flagMini: false

    property bool flagLowerText: false
}
