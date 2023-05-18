import QtQuick 2.6

FocusScope
{
    id: root

    property int totalWidth: 200

    property int playfieldDimX: 400
    
    property alias model: rep.model

    property alias modelMarkers: rep2.model
    
    width: row.width

    property alias bgrect: bgrect

    signal signalMouseAreaClicked( int index_, variant mouse_, variant boundaries_);
    
    Rectangle
    {
	id: bgrect

	visible: false
	
	color: "grey"

	anchors.fill: parent
    }

    Row
    {
	id: row
	
	anchors
	{
	    top: parent.top
	    bottom: parent.bottom
	    bottomMargin: root.height * 0.2
	    horizontalCenter: parent.horizontalCenter
	}
	
//	spacing: 3

    Repeater
    {
	id: rep
	
	anchors
	{
	    top: parent.top

	    bottom: parent.bottom
	}

	delegate: Component
	{
	    Rectangle
	    {
		id: band

		anchors
		{
		    top: parent.top
		    bottom: parent.bottom

		    margins: (index%2==0)?-1:0
		}
		
		color: model.bg

		border.color: "white"

		border.width: (index%2==0)?1:0
		
		opacity: 0.8 //ma.containsMouse ? 0.8 : 0.2

		width: {

		    return getBoundaryWidthFromIndex(rep.model, index, totalWidth)
		}

		Text
		{
		    id: ti
		    
		    anchors.centerIn: parent
		    
		    color: "white"

		    text: "autostage "+(index+1) //"width:"+parent.height.toFixed(1)+"pos:"+model.lo_id+", "+index+"/"+root.model.count+"; prevPos: "+(index>0?root.model.get(index-1).lo_id:0)

		    font
		    {
			pointSize: 6
			//bold: ma.containsMouse
		    }
		}

		MouseArea
		{
		    anchors
		    {
			fill: parent
		    }

		    onDoubleClicked: {

			var newcolor = Qt.rgba( Math.random(), Math.random(), Math.random() ) //cnames.get(index) // model.name

			root.model.setProperty( index, "bg", newcolor+"" );
		    }
		    
		    onClicked: {

			signalMouseAreaClicked(index, mouse, getBoundaryLimits(rep.model, index) );

		    }
		}
	    }
	}
    }
    }




    Repeater
    {
	id: rep2
	
	anchors
	{
	    top: parent.top

	    bottom: parent.bottom
	}

	delegate: Component
	{
	    Item
	    {
		id: markerFrame

		anchors
		{
		    top: row.bottom
		    bottom: parent.bottom

		    margins: (index%2==0)?-1:0
		}

		width: ti.width

		function
		getPosFromIndex(index_)
		{
		    return ( rep2.model.get(index_).lo_id / playfieldDimX )*root.width //totalWidth
		}

		x: getPosFromIndex(index) - (width/2)

		/*
		  MouseArea
		  {
		  id: ma

		  anchors
		  {
		  fill: parent
		  }

		  preventStealing: true
		  
		  hoverEnabled: true

		  onClicked: console.log( ma, "clicked" )
		  }
		*/

		Rectangle
		{
		    id: tick
		    
		    anchors
		    {
			top: parent.top

			horizontalCenter: parent.horizontalCenter
		    }

		    color: "grey"

		    height: 4

		    width: 1
		}

		Text
		{
		    id: ti
		    
		    anchors
		    {
			top: tick.bottom
			topMargin: 3

			horizontalCenter: parent.horizontalCenter
		    }
		    
		    color: "grey"

		    text: rep2.model.get(index).lo_id

		    font
		    {
			pointSize: 6
			//bold: ma.containsMouse
		    }
		}
	    }
	}
    }
    

}
