import QtQuick 2.6

FocusScope
{
    property bool flagEnabled: true

    property bool flagSelected: false

    property variant colorSelected: "green"
    
    opacity: flagEnabled ? 1.0 : 0.5
    
	Rectangle
    {
	anchors.centerIn: parent
	
	width: 12
	height: 12

	color: "grey"
	
	Rectangle
	{
	    visible: flagEnabled
	    
	    anchors
	    {
		fill: parent
	    }

	    color: flagSelected  ? colorSelected : "transparent"
	}

	MouseArea
	{
	    anchors.fill: parent

	    enabled: flagEnabled

	    onClicked: {

		
		flagSelected = ! flagSelected
	    }
	}
    }

}
