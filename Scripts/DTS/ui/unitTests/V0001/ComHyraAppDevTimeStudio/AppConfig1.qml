import QtQuick 2.6

import "../../..";

Item
{
    id: root
        
    property string title: "medium version"

    property int widthBg: 1200

    property int heightBg: 800

    property variant colorBg: "gray"

    property variant configLarge: ViewCrossRectsConfig
    {
        id: configLarge

        axisRect: Qt.rect( 0, 0, 350*5, 350*5 )

        axisStep: Qt.size( 5, 5 )
    }

    function
    loadExample1()
    {
        var _repeats = 1

        for( var i = 0; i < _repeats; i++ )
        {
            flick1.appendAutoStage( 0,   5, true, "red" );

            flick1.appendAutoStageContinue( 10, true, "green" );

            flick1.appendAutoStageContinue( 15, true, "pink" );

            flick1.appendAutoStageContinue( 4, true, "magenta" );

            flick1.appendAutoStageContinue( 8, true, "orange" );

            flick1.appendAutoStageContinue( 8, true, "blue" );

            flick1.appendAutoStageContinue( 50, true, "gold" );
        }
    }

}
