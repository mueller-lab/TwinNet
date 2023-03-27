import QtQuick 2.6

import "../../..";

import "../../../../cache/QML";

import "."

Rectangle
{
    id: root

    AppConfig2
    {
        id: appconfig
    }

    width: appconfig.widthBg

    height: appconfig.heightBg

    color: appconfig.colorBg

    states: [

        State
        {
            name: ""
        },

        State
        {
            name: "dark"

            PropertyChanges
            {
                target: root

                color: "black"
            }
        }
        
    ]


    Keys.onPressed: (event) => {
        
        if( event.key == Qt.Key_N )
        {
            state = ""
        }
        else
        if( event.key == Qt.Key_A )
        {
            state = "dark"
        }

    }




    Text
    {
        anchors
        {
            top: parent.top
            
            horizontalCenter: parent.horizontalCenter

            margins: 5
        }

        color: "white"
        
        text: "Figure1: Example data"
    }
    
    Rectangle
    {
        anchors
        {
            fill: flick1
            
            margins: border.width * -1
        }

        border
        {
            width: 1

            color: "white"
        }

        color: "transparent" // Qt.rgba( 0.1, 0.1, 0.0 )
    }

    ViewCrossRectsFlickable
    {
        id: flick1

        anchors
        {
            fill: parent

            margins: 50
        }

        focus: true

        config1 : appconfig.configLarge

        ListModel
        {
            id: modelAutoStages
        }

        function
        appendAutoStageContinue( width_, flagEnabled_, color_ )
        {
            var posEndLast = 0;

            if( modelAutoStages.count )
            {
                posEndLast = modelAutoStages.get( modelAutoStages.count - 1 ).posEnd;
            }
            
            modelAutoStages.append( 
                {
                    flagEnabled: flagEnabled_,
                    
                    posBegin: posEndLast,

                    posEnd: posEndLast + width_,

                    color: color_
                }
            );
        }
        
        function
        fillAutoStageExample( decl_ )
        {
            if( decl_.flagEnabled )
            {
                var _height = decl_.posEnd - decl_.posBegin;

                for( var i = decl_.posBegin; i < decl_.posEnd; i++ )
                {
                    for( var j = 0; j < _height; j++ )
                    {
                        //if(  i >= j )
                        view1.model.append( {

                            value: Math.random(),
                            
                            posX: i,

                            posY: j + decl_.posBegin,

                            flagCenter : (i - decl_.posBegin) == j,
                            
                            flagUpper : !( (i-decl_.posBegin) == j) && ( (i-decl_.posBegin) >= j),

                            colorBg : decl_.color

                        } );
                    }
                }
            }
        }

        Timer
        {
            id: tiAddStages

            interval: 1000

            repeat: true
            
            property int lastPos : 0
            
            onTriggered: {

                var o = modelAutoStages.get( lastPos );

                flick1.fillAutoStageExample( o );

                lastPos = lastPos + 1

                if( lastPos > modelAutoStages.count-1 )
                    running = false

                
            }
            
        }

        Component.onCompleted: {

            appconfig.loadExample1();
            
            tiAddStages.running = true

        }
        
    }

    Rectangle
    {
        id: mini
        
        anchors
        {
            right: parent.right

            bottom: parent.bottom

            margins: 90
        }
        
        width: 300

        height: 300

        visible: flick1.config1.flagMini
        
        opacity : typeof flick1.view1.cursorUpper.oindex != 'undefined' ? 1.0 : 0.0

        Behavior on opacity 
        { 
            PropertyAnimation 
            { 
                duration: 500 
            } 
        }
        
        color: {

            if( typeof flick1.view1.cursorUpper.oindex != 'undefined' )
            {
                var o = flick1.view1.model.get( flick1.view1.cursorUpper.oindex )

                return flick1.config1.lutUpper( o )
            }

            return "transparent"
        }
        
        border
        {
            width: 1

            color: "white"
        }
    }

    

    Text
    {
        anchors
        {
            bottom: parent.bottom

            right: parent.right

            margins: 5
        }

        color: "white"
        
        text: "debugLevel("+flick1.config1.debugLevel+"), rotAngle("+flick1.config1.rotAngle.toFixed(1)+"), cursor("+flick1.config1.axisCurrentCursorPos.x+","+flick1.config1.axisCurrentCursorPos.x+"):"+
              "cursorMirror("+flick1.config1.axisCurrentCursorMirrorPos.x+","+flick1.config1.axisCurrentCursorMirrorPos.y+")"
    }

}
