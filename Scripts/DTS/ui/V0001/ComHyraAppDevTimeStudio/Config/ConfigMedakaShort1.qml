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

		/*
		{
		    'well_id' : 'A001' ,
		    'embryo_id' : 'E001' ,
		},


		{
		    'well_id' : 'A001' ,
		    'embryo_id' : 'E004' ,
		},
		
		{
		    'well_id' : 'A001' ,
		    'embryo_id' : 'E005' ,
		},

		{
		    'well_id' : 'A001' ,
		    'embryo_id' : 'E009' ,
		},
*/

		
	    ]
	}
    }

    //property string pngRoot: "/media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/MedakaShort/unified/PNGs"

    property string pngRoot: args[ "pngRoot" ]
    
    property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-A001--PO01--LO%2--CO6--%3.png"


    function
    getSourceImageFromModel(model_)
    {
//	var loidstr = ("000" + model_.lo_id).substr(-3,3)
	var loidstr = ("0000" + model_.lo_id).substr(-4,4)

/*
	console.log( "getSourceImageFromModel(model_).. root.pngImageFormat=", root.pngImageFormat )
	console.log( "getSourceImageFromModel(model_).. %1 model_.well_id=", model_.well_id )
	console.log( "getSourceImageFromModel(model_).. %2 loidstr=", loidstr )
	console.log( "getSourceImageFromModel(model_).. %3 model_.embryo_id=", model_.embryo_id )
*/

	var filepath = [ root.pngRoot, root.pngImageFormat.arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );

//	console.log( "getSourceImageFromModel(model_)=", filepath )
	
	return filepath;
	//return [ root.pngRoot, root.pngImageFormat.arg(loidstr) ].join( "/" );
    }

    property int playfieldDimX: 300 //450 //206 //230
    property int playfieldDimY: 300 //450 //206 //230

    property int listModelLimit: 8

    property real imagingSampleTimePerFrameMin: 2

    timeHourTitle: "hpf"
}
