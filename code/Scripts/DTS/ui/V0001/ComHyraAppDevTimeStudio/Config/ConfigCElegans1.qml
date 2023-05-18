import QtQuick 2.3

ConfigBase
{
    id: root

    configName : "ConfigElegans1"

    function
    filterExperimentModelEntry(model_)
    {
	return true;
    }

    property string pngRoot: args[ "pngRoot" ]

    property string pngImageFormat : "-XY01--PO01/embryos/-XY01--PO01--E001/-XY01--PO01--LO%1--CO6--E001.png"

    property int playfieldDimX: 110 //230
    property int playfieldDimY: 110 //230

    property int listModelLimit: 1

    function
    getSourceImageFromModel(model_)
    {
	var loidstr = ("0000" + model_.lo_id).substr(-4,4)

	return [ root.pngRoot, root.pngImageFormat.arg(loidstr) ].join( "/" );
    }

    property real imagingSampleTimePerFrameMin: 17.5
}
