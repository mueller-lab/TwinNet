import QtQuick 2.6

FocusScope
{
    property bool flagCursor

    Behavior on scale { PropertyAnimation {} }

    property alias rect1: rect1

    Rectangle
    {
        id: rect1
        
        anchors
        {
            fill: parent

//            leftMargin: config.axisSpacing.x

//            topMargin: config.axisSpacing.y
        }

        color: config.lutLower( model )
    }

    Text
    {
        visible: config.flagLowerText
        
        rotation: 45
        
        anchors.centerIn: parent
        
        text: model.value.toFixed(2)

        color: "white"

        font
        {
            pointSize: config.axisStep.width*0.3
        }
    }
    
    /*
      Image
      {
      anchors
      {
      fill: parent
      }

      source: "http://bioimages.vanderbilt.edu/lq/baskauf/wzfish-1cell30547.jpg"

      fillMode: Image.PreserveAspectFit

          opacity: Math.random() 
      }
    */

}

