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

        color: config.lutUpper( model )

        //opacity: 0.4

        //radius: 4
        
        //border.width: 1
        //border.color: "white"
        

//        opacity: 0.5

    Rectangle
    {
        id: rectBg
        
        anchors
        {
            fill: rect1
        }

        color: model.colorBg

        opacity: 0.4
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

      //opacity: 0.7
      }
    */
}

