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

    // /media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/CElegans/unified/TIFs/-XY01--PO01/embryos/-XY01--PO01--E001/-XY01--PO01--LO0206--CO6--E001.tif
    
//    property string pngRoot: "/media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/CElegans/unified/PNGs"

    property string pngRoot: args[ "pngRoot" ]

//    property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png"
    // /media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/CElegans/unified/TIFs/-XY01--PO01/embryos/-XY01--PO01--E001/-XY01--PO01--LO0206--CO6--E001.tif
    // /media/sf_Mueller/Documents/GOR-robustness_embryogenesis/Manuscripts/Siamese-networks/data/CElegans/unified/TIFs/-XY01--PO01/embryos/-XY01--PO01--E130/-XY01--PO01--LOA001--CO6--E130.tif
    //                                -XY01--PO01/embryos/-XY01--PO01--E001/-XY01--PO01--LO0001--CO6--E001.png
    property string pngImageFormat : "-XY01--PO01/embryos/-XY01--PO01--E001/-XY01--PO01--LO%1--CO6--E001.png"

    property int playfieldDimX: 110 //230
    property int playfieldDimY: 110 //230

    property int listModelLimit: 1

    function
    getSourceImageFromModel(model_)
    {
//	var loidstr = ("000" + model_.lo_id).substr(-3,3)
	var loidstr = ("0000" + model_.lo_id).substr(-4,4)

//	var filepath = [ root.pngRoot, root.pngImageFormat.arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );
//	return filepath;

	return [ root.pngRoot, root.pngImageFormat.arg(loidstr) ].join( "/" );
    }

    property real imagingSampleTimePerFrameMin: 17.5
}
