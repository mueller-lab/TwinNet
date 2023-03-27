import QtQuick 2.6

Item
{
    id: root

    property string configName : "ConfigBase"

    function
    filterExperimentParams()
    {
	return;
    }
    
    function
    getSourceImageFromMousePosition(mouse_)
    {
	//return [ root.pngRoot, root.pngImageFormat.arg(model_.well_id).arg(model_.lo_id).arg(model_.embryo_id) ].join( "/" );
	return [ root.pngRoot, root.pngImageFormat.arg(model_.lo_id) ].join( "/" );
    }

    function
    getSourceImageFromModel(model_)
    {
//	var loidstr = ("000" + model_.lo_id).substr(-3,3)
	var loidstr = ("0000" + model_.lo_id).substr(-4,4)

	var filepath = [ root.pngRoot, root.pngImageFormat.arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );

	//	console.log( "getSourceImageFromModel(model_)=", filepath )
	
	return filepath;
	//return [ root.pngRoot, root.pngImageFormat.arg(loidstr) ].join( "/" );
    }

    property real viewBoundaryTotalWidthFactor: 1.0

    property string timeHourTitle: "h"

    property variant args: { }

    function
    parseArgs(prefix_)
    {
//	console.log( "Qt.application.arguments: ", Qt.application.arguments )

	var temp = {};
	
	for( var i=0; i < Qt.application.arguments.length; i++ )
	{
	    var str = Qt.application.arguments[i];
	    
//            console.log( "Qt.application.arguments[", i, "]: ", str )

	    var found = str.match( new RegExp( "--"+prefix_+"\/([^=]+)=(.*)" ) );

	    if( found )
	    {
		temp[ found[1] ] = found[2];

		console.log( "ARG ", prefix_, ": ", found[1], "=", found[2] );
	    }
	}

	args = temp;
    }
    
    Component.onCompleted: {

	parseArgs( "config" )
	
    }

}
