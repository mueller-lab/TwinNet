import QtQuick 2.6

FocusScope
{
    property bool flagCursor

    Behavior on scale { PropertyAnimation {} }

    Rectangle
    {
        anchors
        {
            fill: parent


//            leftMargin: config.axisSpacing.x

//            topMargin: config.axisSpacing.y
        }

        color: config.lutCenter( model )

        opacity: 0.5

        Text
        {
                id: ti

            anchors
            {
                centerIn: parent
            }

            text: posX+","+posY //index

            rotation: 45
            
            visible: flagCursor
            
            font
            {
                pointSize: 10
            }
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

