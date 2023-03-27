import QtQuick 2.3

ConfigBase
{
    id: root

    configName : "ConfigStickleback1"


    function
    filterExperimentParams()
    {
	return {

	    'appName' : 'app1-medakashort.qml',
	    'configName' : 'ConfigMedakaShort1',
	    'table' : [
		{
		    'well_id' : 'XY10' ,
		    'embryo_id' : 'E002' ,
		},
		
		{
		    'well_id' : 'XY15' ,
		    'embryo_id' : 'E002' ,
		},

	    ]
	}
    }

    // /media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/CElegans/unified/TIFs/-XY01--PO01/embryos/-XY01--PO01--E001/-XY01--PO01--LO0206--CO6--E001.tif
    
//    property string pngRoot: "/media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/Stickleback/unified/PNGs"
    property string pngRoot: args[ "pngRoot" ]

//  property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png"

//  "/media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/Stickleback/unified/PNGs/-XY20--PO01/embryos/-XY20--PO01--E001/-XY20--PO01--LO1350--CO6--E001.png"

//                                    -XY20--PO01/embryos/-XY20--PO01--E001/-XY20--PO01--LO0001--CO6--E001.png
    property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png"


    property int playfieldDimX: 1350 //206 //230
    property int playfieldDimY: 1350 //206 //230

    property int listModelLimit: 7

    function
        getSourceImageFromModel(model_)
    {
//	var loidstr = ("000" + model_.lo_id).substr(-3,3)
	var loidstr = ("0000" + model_.lo_id).substr(-4,4)

	console.log( "getSourceImageFromModel(model_), loidstr=", loidstr );
	
	var filepath = [ root.pngRoot, root.pngImageFormat.arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );

	console.log( "getSourceImageFromModel(model_)=", filepath )
	
	return filepath;
	//return [ root.pngRoot, root.pngImageFormat.arg(loidstr) ].join( "/" );
    }

    property real imagingSampleTimePerFrameMin: 5

    viewBoundaryTotalWidthFactor: 0.75
}
