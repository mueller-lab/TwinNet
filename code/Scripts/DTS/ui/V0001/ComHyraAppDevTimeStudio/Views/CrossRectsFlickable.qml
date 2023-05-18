import QtQuick 2.6

import "../../..";

Flickable
{
    id: flick1
    
    contentWidth: zone.width

    contentHeight: zone.height

    clip: true

    property alias config1: view1.config
    
    property alias view1: view1
    
    Item
    {
        id: helper

        width: Math.max( flick1.width, zone.width )

        height: Math.max( flick1.height, zone.height )
        
        Item
        {
            id: zone

            anchors
            {
                centerIn: parent
            }
            
            width: 4*1200 * view1.scale + Math.abs(config1.rotAngle%90)

            height: 800 * view1.scale + Math.abs(config1.rotAngle%90)

            
            Rectangle
            {
                visible: config1.debugLevel > 1
                
                anchors
                {
                    fill: parent
                }

                color: "blue"
            }

            ViewCrossRects
            {
                id: view1

                anchors.centerIn: parent
                
                Behavior on scale { PropertyAnimation {} }
                
                model: ListModel
                {
                }
            }
        }

    }




    Keys.onPressed: (event) => {

        if( event.key == Qt.Key_D )
        {
            config1.debugLevel = config1.debugLevel +1 
        }
        else
        if( event.key == Qt.Key_M )
        {
            console.log( "flagMini=", config1.flagMini )
            
            config1.flagMini = ! config1.flagMini
        }
        else
        if( event.key == Qt.Key_S )
        {
            if( config1.debugLevel > 0 )
            config1.debugLevel = config1.debugLevel -1 
        }
        else
        if( event.key == Qt.Key_Z )
        {
            config1.rotAngleReset()
        }
        else
        if( event.key == Qt.Key_R )
        {
            if( config1.rotAngle >= 360 )
                config1.rotAngle = 0
            
            config1.rotAngle = config1.rotAngle + (15)
        }
        else
            if( event.key == Qt.Key_L )
        {
            if( config1.rotAngle < 15 )
            {
                config1.rotAngle = 0
            }
            else
            {
                config1.rotAngle = config1.rotAngle - (15)
            }
        }
        else
        {
            if( event.key == Qt.Key_Plus )
                flick1.view1.scale = flick1.view1.scale + 0.15
            else
                if( event.key == Qt.Key_Minus )
                    flick1.view1.scale = flick1.view1.scale - 0.15
        }
    }
    
}
