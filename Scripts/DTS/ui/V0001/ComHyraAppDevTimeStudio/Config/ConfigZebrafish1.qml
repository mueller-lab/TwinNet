import QtQuick 2.3

ConfigBase
{
    id: root

    configName : "ConfigZebrafish1"

    property string pngRoot: args[ "pngRoot" ] //"/media/muenalan/share/GOR-robustness_embryogenesis/data/Acquifer/0089-210420-ACQUIFER-mezzo/PNGs"
//    property string pngRoot: "/Volumes/MUE_USB_01/Manuscripts/Siamese-networks/data/Zebrafish/PNGs"

    property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png"

    property int playfieldDimX: 355
    property int playfieldDimY: 355

    property int listModelLimit: 230

    function
    filterExperimentParams()
    {
	return {

	    'appName' : 'app1-zebrafish.qml',
	    'configName' : 'ConfigZebrafish1',
	    'table' : [
		{
		    'well_id' : 'A004' ,
		    'embryo_id' : 'E002'
		},

		{
		    'well_id' : 'A006' ,
		    'embryo_id' : 'E001'
		},

		{
		    'well_id' : 'A003' ,
		    'embryo_id' : 'E002'
		},

		{
		    'well_id' : 'A003' ,
		    'embryo_id' : 'E003'
		},

		{
		    'well_id' : 'A005' ,
		    'embryo_id' : 'E001'
		},

		{
		    'well_id' : 'A005' ,
		    'embryo_id' : 'E003'
		},

		{
		    'well_id' : 'A006' ,
		    'embryo_id' : 'E001'
		}
	    ]
	}
    }

    function
    getSourceImageFromMousePosition(mouse_)
    {
	//return [ config1.pngRoot, config1.pngImageFormat.arg(model_.well_id).arg(model_.lo_id).arg(model_.embryo_id) ].join( "/" );
	return [ config1.pngRoot, config1.pngImageFormat.arg(model_.lo_id) ].join( "/" );
    }

    function
    getSourceImageFromModel(model_)
    {
	var loidstr = ("000" + model_.lo_id).substr(-3,3)
//	var loidstr = ("0000" + model_.lo_id).substr(-4,4)

	var filepath = [ config1.pngRoot, config1.pngImageFormat.arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );

//	console.log( "getSourceImageFromModel(model_)=", filepath )
	
	return filepath;
	//return [ config1.pngRoot, config1.pngImageFormat.arg(loidstr) ].join( "/" );
    }

    property real imagingSampleTimePerFrameMin: 4

    viewBoundaryTotalWidthFactor: 0.75

    timeHourTitle: "hpf"

}
