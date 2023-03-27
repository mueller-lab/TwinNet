import QtQuick 2.6

import "../../..";

FocusScope
{
    id: root

    property variant config: config1

    ViewCrossRectsConfig
    {
        id: config1
    }
        
    property variant model


    width: config.axisRect.width

    height: config.axisRect.height


    property alias cursorUpper: cursorUpper

    property alias cursorLower: cursorLower

    //clip: true

    function
    getModelIndexFromXY( point_ )
    {
        //return point_.y * config.axisStep.width + point_.x

        for( var i=0; i < model.count; i++ )
        {
            var o = model.get( i );

            if( point_.x == o.posX )
                if( point_.y == o.posY )
                    return i;
        }
    }
    
    Rectangle
    {
        visible: config.debugLevel > 0
        
        anchors
        {
            fill: parent
        }

        color: "yellow"
    }
    

    Item
    {
        id: playfield


        anchors
        {
            centerIn: parent
        }

        
        width: config.axisRect.width

        height: config.axisRect.height

        transform: [

	    Rotation
	    {
	        angle: config.rotAngle //-90-45

	        origin
                {
                    x: root.width/2

                    y: root.height/2
                }
	    }
        ]
        
        Rectangle
        {
            anchors
            {
                fill: parent
                margins: -1
            }

            color: "transparent" //Qt.rgba( 0.8, 0, 0, 0.2 )

            border.width: 2
            
            border.color: "white"
        }

        MouseArea
        {
            id: ma

            enabled: true

            anchors
            {
                fill: parent
            }

            hoverEnabled: true

            onPositionChanged: {

                if( containsMouse )
                {
                    config.axisCurrentCursorPos = Qt.point( Math.floor(mouseX/config.axisStep.width), Math.floor(mouseY/config.axisStep.height) )

                    config.axisCurrentCursorMirrorPos = Qt.point( config.axisCurrentCursorPos.y, config.axisCurrentCursorPos.x )

                    //if( config.axisCurrentCursorPos.x != -1 )
                    //return ( (config.axisCurrentCursorPos.x == posX) && (config.axisCurrentCursorPos.y == posY) ) || ( (config.axisCurrentCursorMirrorPos.x == posX) && (config.axisCurrentCursorMirrorPos.y == posY) )
                }
                else
                {
                    config.axisCurrentCursorPos = Qt.point( -1, -1 )

                    config.axisCurrentCursorMirrorPos =  Qt.point( -1, -1 )
                }
            }
        }
        
    Repeater
    {
        model: root.model

        delegate : Component
        {
            Loader
            {
                x: posX * (config.axisStep.width * config.axisScale) 

                y: posY * (config.axisStep.height * config.axisScale)
                
                width: (config.axisStepWithoutSpacing.width * config.axisScale)

                height: (config.axisStepWithoutSpacing.height * config.axisScale)
                
                Component
                {
                    id: upper

                    ViewCrossRectsDelegateUpper
                    {
                        anchors.fill: parent

                    }
                }

                Component
                {
                    id: center

                    ViewCrossRectsDelegateCenter
                    {
                        anchors.fill: parent
                    }
                }
                
                Component
                {
                    id: lower
                    
                    ViewCrossRectsDelegateLower
                    {
                        anchors.fill: parent
                    }
                }

                sourceComponent: {

                    if( flagCenter )
                        return center;
                    
                    return flagUpper ? upper : lower

                }
            }
        }

    }

        Item
        {
            id: cursorUpper

            visible: config.axisCurrentCursorPos.x >= 0
            
            x: (config.axisCurrentCursorPos.x * config.axisStep.width * config.axisScale) 

            y: (config.axisCurrentCursorPos.y * config.axisStep.height * config.axisScale)

            width: config.axisStepWithoutSpacing.width

            height: config.axisStepWithoutSpacing.height

            property variant oindex : getModelIndexFromXY( config.axisCurrentCursorPos )
            
            opacity : typeof flick1.view1.cursorUpper.oindex != 'undefined' ? 1.0 : 0.0

            Behavior on opacity { PropertyAnimation { duration: 500 } }

            Rectangle
            {
                anchors
                {
                    fill: parent

                    margins: (parent.width/2)*0.85
                }

                color: config.cursorUpperColorFg

                radius: width/2
            }


            //crossH does the job
            /*
            Text
            {
                anchors.centerIn: parent
           
                text: config.axisCurrentCursorPos.x+", "+config.axisCurrentCursorPos.y

                rotation: 45

                color: "white"
                
                font
                {
                    pointSize: config.axisStep.width*0.25
                }
            }
            */
        }

        Rectangle
        {
            id: cursorLower

            visible: config.axisCurrentCursorPos.x >= 0

            x: (config.axisCurrentCursorMirrorPos.x * config.axisStep.width * config.axisScale)

            y: (config.axisCurrentCursorMirrorPos.y * config.axisStep.height * config.axisScale)

            width: config.axisStepWithoutSpacing.width

            height: config.axisStepWithoutSpacing.height

            color: config.cursorLowerColorFg

            opacity: cursorUpper.opacity
            
            Text
            {
                rotation: 45
                
                anchors.centerIn: parent
           
                text: config.axisCurrentCursorMirrorPos.x+", "+config.axisCurrentCursorMirrorPos.y

                color: "white"

                font
                {
                    pointSize: config.axisStep.width*0.3
                }
            }
        }




    Rectangle
    {
        id: crossH

        opacity: cursorUpper.opacity

        anchors
        {
            top: parent.top

            bottom: parent.bottom
        }
        
        width: 1

        x: cursorUpper.x + (cursorUpper.width/2) - width/2

        color: config.crossFg
        
        Text
        {
            anchors
            {
                left: parent.left

                leftMargin: 8
            }

            y: cursorUpper.y + (cursorUpper.height/2) - (height*1.5)

            text: config.axisCurrentCursorPos.x+", "+config.axisCurrentCursorPos.y

            color: "white"
            
            font
            {
                pointSize: config.axisStep.width*0.25
            }
        }

    }


    Rectangle
    {
        id: crossV

        opacity: cursorUpper.opacity

        anchors
        {
            left: parent.left

            right: parent.right
        }
        
        height: 1

        y: cursorUpper.y + (cursorUpper.height/2) - height/2

        color: config.crossFg
        
    }

        

        
    }



    /*

    Rectangle
    {
        id:  cursorVerticalIndicator

        anchors
        {
            top: parent.top
            bottom: parent.bottom
        }


        width: 1

        x: cursorUpper.x
    }

    */

    
}
