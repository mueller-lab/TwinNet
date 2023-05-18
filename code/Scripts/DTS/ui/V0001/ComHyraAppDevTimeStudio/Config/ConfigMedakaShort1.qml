import QtQuick 2.3

ConfigBase
{
    id: root

    configName : "ConfigMedakaShort1"

    function
    filterExperimentParams()
    {
	return {

	    'appName' : 'app1-medakashort.qml',
	    'configName' : 'ConfigMedakaShort1',
	    'table' : [
		{
		    'well_id' : 'A001' ,
		    'embryo_id' : 'E002' ,
		},
		
		{
		    'well_id' : 'A001' ,
		    'embryo_id' : 'E003' ,
		},
		
	    ]
	}
    }

    property string pngRoot: args[ "pngRoot" ]
    
    property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-A001--PO01--LO%2--CO6--%3.png"


    function
    getSourceImageFromModel(model_)
    {
	var loidstr = ("0000" + model_.lo_id).substr(-4,4)

	var filepath = [ root.pngRoot, root.pngImageFormat.arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );

	return filepath;
    }

    property int playfieldDimX: 300 //450 //206 //230
    property int playfieldDimY: 300 //450 //206 //230

    property int listModelLimit: 8

    property real imagingSampleTimePerFrameMin: 2

    timeHourTitle: "hpf"
}
