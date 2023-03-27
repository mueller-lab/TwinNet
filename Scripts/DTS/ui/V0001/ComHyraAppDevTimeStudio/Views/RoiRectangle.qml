import QtQuick 2.3

Rectangle
{
    id: root
    
    property point point1: Qt.point( 0, 0 )
    property point point2: Qt.point( 0, 0 )

    color: "transparent"

    border.color: Qt.rgba( Math.random(), Math.random(), 0.2 )
    border.width: 2

    x: point1.x
    y: point1.y

    width: point2.x - point1.x
    height: point2.y - point1.y

    Rectangle
    {
	color: parent.border.color

	width: 4
	height: 4

	x: parent.width/2 - width/2
	y: parent.height/2 - height/2
    }
}

