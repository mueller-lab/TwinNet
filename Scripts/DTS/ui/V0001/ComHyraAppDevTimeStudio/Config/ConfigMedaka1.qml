import QtQuick 2.3

ConfigBase
{
    id: root

    configName : "ConfigMedaka1"

    function
    filterExperimentModelEntry(model_)
    {
	return true;
    }

    // /media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/CElegans/unified/TIFs/-XY01--PO01/embryos/-XY01--PO01--E001/-XY01--PO01--LO0206--CO6--E001.tif
    
    property string pngRoot: "/media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/Medaka/unified/PNGs"

//    property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png"

//  /media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/Medaka/unified/PNGs/-A001--PO01/embryos/-A001--PO01--E010/-A001--PO01--LO0442--CO6--E010.png"


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

    property int playfieldDimX: 450 //206 //230
    property int playfieldDimY: 450 //206 //230

    property int listModelLimit: 8

    property real imagingSampleTimePerFrameMin: 2
}
