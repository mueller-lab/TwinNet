/*

  Author: Murat Uenalan <murat.uenalan@uni-konstanz.de>

  Affiliation: Constance University/DE, Department for Systems Biology of Development (AG Patrick Müller)

*/

import QtQuick 2.3

import "../../..";

Rectangle
{
    id: root
    
    width: 1200

    height: 800*2

    color: debugLevel ? "red" : "white"
    
    property real bandShift : 0
    
    property real widthFromIndexScale : 1.053
    
    property point topLeftInset: Qt.point( 0, 0 )

    //property bool  playfield_candidate_flag : false

    property int debugLevel: 0
    
    property real playfield_scale_factor_x : 1.49

    property real playfield_scale_factor_y : 1.49
    
    property point playfield_candidate_p1: Qt.point( 900, 0 )

    property point playfield_candidate_p2: Qt.point( playfield_candidate_p1.x+300, 300 )

    property point roi_candidate_p1: Qt.point( 900, 0 )

    property point roi_candidate_p2: Qt.point( roi_candidate_p1.x+300, 300 )

    property point crossHairRel: Qt.point( 0, 0 )

    property int global_lo_id: 1

    property int globalImgInsetWidthVar: 0

    property int globalImgInsetWidth: 240 + globalImgInsetWidthVar

    property bool flagShowMetadata: false
    
    property bool flagSyncLoId: false

    property bool flagAtlasShow: true

    property bool flagGridShow: false

    property bool flagBands: true

    property bool flagFinal: false

    property real totalWidthGlobal : root.width * config1.viewBoundaryTotalWidthFactor

    signal signalGlobalReload();

    onSignalGlobalReload: {

	console.log( "root.signalGlobalReload()" )
    }

    
    state: "loading"
    
    states: [

	State
	{
	    name: "";

	    PropertyChanges
	    {
		target: overlayLoading

		opacity: 0.0
	    }
	},

	State
	{
	    name: "data_selection_mode";

	},

	State
	{
	    name: "loading";

	    PropertyChanges
	    {
		target: overlayLoading
		
		opacity: 1.0
	    }
	}

    ]


    function
    convertIdToTimeToMin(id_)
    {
	return id_*config1.imagingSampleTimePerFrameMin
    }

    function
    convertIdToTimeToHours(id_)
    {
	var _minutes = convertIdToTimeToMin(id_);
	
	return (_minutes/60).toFixed(1)
    }



    function
    bandsModelGetInfoOfBand(boundarymodel_, index_)
    {
	var listmodel_ = boundarymodel_ // atlasmodel //metadata.get(0).boundaries_peaks;
	
	var obj = listmodel_.get( index_ );

	var lower = 0;

	if( index_ > 0 )
	{
	    lower = listmodel_.get( index_-1 ).lo_id //.pos
	}

	var upper = obj.lo_id;

	//console.log( "bandColor: ", obj.bg );
	
	return {
	    index : index_,
	    lowerPos : lower,
	    upperPos : upper,
	    bgColor : obj.bg+""
	};
    }

    function
    findInBandsModel(boundarymodel_, model_)
    {
	var loid = model_.lo_id;
	
	var listmodel_ = boundarymodel_ //atlasmodel // metadata.get(0).boundaries_peaks;

	var result = []
	
	for( var i=0; i < listmodel_.count; i++ )
	{
	    var obj = listmodel_.get( i );

	    result.push( obj.lo_id );
	}

	for( var i=0; i < listmodel_.count; i++ )
	{
	    var obj = listmodel_.get( i );

	    var lower = 0;

	    if( i > 0 )
	    {
		lower = listmodel_.get( i-1 ).lo_id
	    }

	    var upper = obj.lo_id;

	    if( loid >= lower && loid <= upper )
	    {
		//console.log( "findInBandsModel: loid=", loid, ", lower=", lower, ", upper=", upper, ", all bands are: ", result.join(",") )
		return i;
	    }
	}

	return ""
    }

    function
    getBoundaryLimits(boundarymodel_, index_)
    {
	var lower_ = 0;
	var upper_ = 0;
	
	if( index_ > 0 )
	{
	    upper_ = boundarymodel_.get(index_).lo_id

	    lower_ = boundarymodel_.get(index_-1).lo_id
	}
	else
	{
	    upper_ = boundarymodel_.get(index_).lo_id

	    lower_ = 0
	}
	
	//		    console.log( "index_ > 0, upper_=", upper_, ", lower_=", lower_ );

	return {
	    "lower": lower_, 
	    "upper": upper_, 
	    "width": upper_ - lower_
	}
    }

    function
    getBoundaryWidthFromIndex(boundarymodel_, index_, totalWidth_)
    {
	var _boundaries = getBoundaryLimits(boundarymodel_, index_);

	var rw = (_boundaries.width / playfieldDimX)
	
	//console.log( "getWidthFromIndex(index_=", index_, ") _boundaries.lower=", _boundaries.lower, ", _boundaries.upper=", _boundaries.upper, ", _boundaries.width=", _boundaries.width, ", rw=", rw.toFixed(2) );

	return rw*totalWidth_
    }
    

    ListModelColornames
    {
	id: cnames
    }

    Rectangle
    {
	id: overlayLoading
	
	anchors
	{
	    centerIn: parent
	}

	width: tiLoadingInfo.width *1.3

	height: Math.min( parent.height*0.3, 200 )

	radius: 30

	z: 1000000

	clip: true
	
	Text
	{
	    id: tiLoadingInfo
	    
	    anchors
	    {
		centerIn: parent
	    }

	    text: "Loading... embryos n=["+model1.count+"/"+model1.sourceDataArray.length+"]. model1.running="+model1.running+", root.state="+root.state

	    color: "black"
	}
    }
	
    function
    filterMetadataPoints(x_, y_)
    {
	return Math.abs(x_ - y_) < 10;
    }


    Text
    {
	visible: false
	
	z: 100000
	
	anchors
	{
	    top: parent.top
	    horizontalCenter: parent.horizontalCenter

	    margins: 30
	}
	
	text: "Loading .."

	color: "white"

	font
	{
	    pointSize: 20

	}
    }
    
    function
    resetPoints()
    {
	playfield_candidate_p1 = Qt.point( 0, 0 )
	
	playfield_candidate_p2 = Qt.point( 1, 1 )

    	roi_candidate_p1 = Qt.point( 0, 0 )
	
	roi_candidate_p2 = Qt.point( 1, 1 )
    }

    onWidthChanged: {

	resetPoints()
	
    }
    
    onHeightChanged: {

	resetPoints()
	
    }

    function
    resetRoiModel()
    {
	roimodel_global.clear();
    }

    Keys.onEscapePressed: (event) => {

	if( event.modifiers & Qt.AltModifier )
	{
	    resetRoiModel()

	    return
	}

	resetPoints()

    }

    //focus: true

    property bool flagKeyShiftDown : false

    onFlagKeyShiftDownChanged: {

	//console.log( "ShiftDown:", flagKeyShiftDown )
    }
    
    Keys.onReleased: (event) => {

//	console.log( "Keys.onReleased, event.modifiers=", event.modifiers )
	
	//if( event.modifiers & Qt.ShiftModifier )
	    flagKeyShiftDown=false
    }
    
    Keys.onPressed: (event) => {

//	console.log( "Keys.onPressed, event.modifiers=", event.modifiers )

	if( event.modifiers & Qt.ShiftModifier )
	    flagKeyShiftDown=true

	if( event.key == Qt.Key_S )
	{
	    console.log( "# Copy files to local snapshot.." );
	    
	    var result = [];


	    
	    for( var i=0; i < lv1.model.count; i++ )
	    {
		var o = lv1.model.get(i);

		if( o.flag_selected || flagKeyShiftDown )
		{
		    var obj = {
			'index' : i,
			'embryo_id': o.embryo_id,
			'well_id': o.well_id,
			'matrix_source': o.matrix_source,
		    }



		    
		    for( var j=0; j < o.boundarymodel.count; j++ )
		    {
			var boundaries_ = getBoundaryLimits(o.boundarymodel, j);

			    if( o.metadata.count )
			    {
				var model_original = o.metadata.get(0).local_maxima_points
				
				if( 1 ) //index == 0 )
				{
				    for( var k=0; k < model_original.count; k++ )
				    {
					var obj = model_original.get(k);

					// Filter for centered points

					if( filterMetadataPoints(obj.x, obj.y) )
					{
					    //console.log( "Adding atlaspoint: x=", obj.x, ", y=", obj.y );

					    if( obj.x >= boundaries_.lower && obj.x <= boundaries_.upper )
					    {
						var _entry =  {

						    well_id : o.well_id,

						    embryo_id : o.embryo_id,

						    lo_id : Math.ceil(obj.x), 
						
						    x: Math.ceil(obj.x),

						    y: Math.ceil(obj.y),

						    delta_prev : obj.delta_prev,

						    flag_selected : false
						}

						//console.log( "append gv1, _entry.x: ", _entry.x, ", _entry.y: ", _entry.y )

						var fileSourceImage = config1.getSourceImageFromModel( { 

						    well_id: o.well_id, 

						    embryo_id: o.embryo_id, 

						    lo_id: _entry.lo_id,

						} );

						console.log( "CONFIG_NAME="+config1.configName, "ENTRY_TYPE="+"boundarymodel", "IMAGE_SOURCE="+fileSourceImage, "WELL_ID="+o.well_id, "EMBRYO_ID="+o.embryo_id, "METADATA_LOCAL_MAXIMA_N="+k, "CLASS="+"autostage", "LO_ID="+_entry.lo_id, "BOUND_LOWER="+boundaries_.lower, "BOUND_UPPER="+boundaries_.upper, "dts_helper_cmdline_tool_copy_to_snapshot" )
						
					    }
					}

				    }
				}
			    }
		    }
		}
	    }


	    
	    for( var i=0; i < lv1.model.count; i++ )
	    {
		var o = lv1.model.get(i);

		if( o.flag_selected || flagKeyShiftDown )
		{
		    var obj = {
			'index' : i,
			'embryo_id': o.embryo_id,
			'well_id': o.well_id,
			'matrix_source': o.matrix_source,
		    }

		    for( var j=0; j < o.atlasmodel.count; j++ )
		    {
			var o2 = o.atlasmodel.get(j);
			
			var fileSourceImage = config1.getSourceImageFromModel( { 

			    well_id: o.well_id, 

			    embryo_id: o.embryo_id, 

			    lo_id: o2.lo_id,

			} );


			for( var k=0; k < o.boundarymodel.count; k++ )
			{
			    var boundaries_ = getBoundaryLimits(o.boundarymodel, k);

			    if( o2.lo_id >= boundaries_.lower && o2.lo_id <= boundaries_.upper )
			    {
				console.log( "CONFIG_NAME="+config1.configName, "ENTRY_TYPE="+"atlasmodel", "IMAGE_SOURCE="+fileSourceImage, "WELL_ID="+o.well_id, "EMBRYO_ID="+o.embryo_id, "ATLAS_INDEX="+j, "LO_ID="+o2.lo_id, "TYPE="+o2.type, "CLASS="+"autostage", "BOUNDARY_INDEX="+k, "dts_helper_cmdline_tool_copy_to_snapshot" )
			    }
			}
			
		    }
					      
		}
	    }
	    
	}
	else
	if( event.key == Qt.Key_W )
	{
	    var result = [];
	    
	    for( var i=0; i < lv1.model.count; i++ )
	    {
		var o = lv1.model.get(i);

		if( o.flag_selected || flagKeyShiftDown )
		{
		    var obj = {
			'index' : i,
			'embryo_id': o.embryo_id,
			'well_id': o.well_id,
			'matrix_source': o.matrix_source,
		    }

		    var parts = [];
		    
		    Object.keys(obj).forEach( 
			function( key_ )
			{
			    parts.push( "       '%1' : '%2' ".arg( key_ ).arg( obj[key_] ) );
			}
		    );

		    result.push( "\n    {\n"+ ( parts.join( ",\n" ) ) +"\n    }" );
					      
		}
	    }

	    console.log( " json = [\n", 
			 "{\n",
			 "  'appName' : '"+root.objectName+"',\n",
			 "  'configName' : '"+config1.configName+"',\n",
			 "  'table' : [\n", result.join( ",\n" ), "\n    ]\n",
			 "}\n]"
		       );
	    
	}
	else
	if( event.key == Qt.Key_Right )
	{
	    if( flagKeyShiftDown )
	    {
		widthFromIndexScale = widthFromIndexScale + 0.01
	    }
	    else
	    bandShift = bandShift + 1
	}
	else
	if( event.key == Qt.Key_Left )
	{
	    if( flagKeyShiftDown )
	    {
		widthFromIndexScale = widthFromIndexScale - 0.01
	    }
	    else
	    bandShift = bandShift - 1
	}
	else
	if( event.key == Qt.Key_Tab )
	{
	    flagGridShow = ! flagGridShow
	}
	else
	    if( event.key == Qt.Key_Plus )
	{
	    if( event.modifiers & Qt.AltModifier )
	    {
		console.log( "ShiftModifier" )

		globalImgInsetWidthVar = globalImgInsetWidthVar + (40*0.5)
	    }
	    else
	    globalImgInsetWidthVar = globalImgInsetWidthVar + 40
	}
	else
	    if( event.key == Qt.Key_Minus )
	{
	    if( event.modifiers & Qt.AltModifier )
		globalImgInsetWidthVar = globalImgInsetWidthVar - 40*0.5
	    else
		globalImgInsetWidthVar = globalImgInsetWidthVar - 40
	}
	else
	    if( event.key == Qt.Key_R )
	{
	    if( event.modifiers & Qt.ControlModifier )
		root.signalGlobalReload()
	    else
	    gv2.visible = ! gv2.visible
	}
	else
	    if( event.key == Qt.Key_B )
	{
	    flagBands = ! flagBands
	}
	else
	    if( event.key == Qt.Key_F )
	{
	    flagFinal = ! flagFinal
	}
	else
	    if( event.key == Qt.Key_M )
	{
	    flagShowMetadata = ! flagShowMetadata
	}
	else
	    if( event.key == Qt.Key_D )
	{
	    if( debugLevel )
		debugLevel = 0;
	    else
		debugLevel = 1;
	}
	else
	    if( event.key == Qt.Key_P )
	{
	    if( root.state == "data_selection_mode" )
	    root.state = "";
	    else
	    root.state = "data_selection_mode";
	}
    }


    ListModel
    {
	id: roimodel_global

    }

    function
    roiModelFind(roimodel_, x_, y_)
    {
	for( var i=0; i < roimodel_.count; i++ )
	{
	    var model = roimodel_.get(i);
	    
	    if( x_ >= model.point1.x && x_ <= model.point2.x )
		if( y_ >= model.point1.y && y_ <= model.point2.y )
		    return i;
	}

	return -1;
    }

    //Zebrafish
    //property int playfieldDimX: 360 //230
    //property int playfieldDimY: 360 //230

    //CElegans
    property int playfieldDimX: config1.playfieldDimX // 206 //230
    property int playfieldDimY: config1.playfieldDimY // 206 //230
    
    ListModel
    {
	id: model2

	function
	initModelAll(well_id_, embryo_id_)
	{
	    clear();
	    
	    for( var i=1; i <= 360; i++ )
	    {
		if( i <= playfieldDimX )
		{
		if( ( i % 4 ) == 0 )
		{
		    append( { well_id: well_id_, embryo_id: embryo_id_, lo_id: i } );
		}
		}
	    }
	}

	Component.onCompleted: {

	}
    }

    ListView
    {
	id: lv1
	
	anchors
	{
	    top: parent.top
	    left: parent.left
	    right: parent.right
	    bottom: gv1.top
	}		

	clip: true

	focus: true
	
	model: model1

	currentIndex: 0
	
	cacheBuffer: 200000

	spacing: flagFinal ? 0 : 20

	delegate: Component
	{
	    Item
	    {
		id: lv1Entry
		
		width: lv1.width
		
		height: flagFinal ? atlasframe.height : (img.height + atlasframe.height*1.05)

		function
		appendRoiRectLocal(point1_, point2_)
		{
		    roimodel.append( {

			id : "roi_local."+((Math.random()+1.0).toFixed(4)),
			
			type : "rect",

			point1 : point1_,

			point2 : point2_,

			bgcolor: Qt.rgba( Math.random(), Math.random(), 0.2 )+""

		    } );
		}

		function
		appendRoiRectGlobal(point1_, point2_)
		{
		    roimodel_global.append( {

			id : "roi_global."+((Math.random()+1.0).toFixed(4)),
			
			type : "rect",

			point1 : point1_,

			point2 : point2_,

			bgcolor: Qt.rgba( Math.random(), Math.random(), 0.2 )+""

		    } );
		}

		function
		currentLoIdFromCoord(mx1_, my1_)
		{
		    return Math.max( mx1_.toFixed(0), my1_.toFixed(0) )
		}
		
	    /*
	    MouseArea
	    {
		id: maIndex

		anchors
		{
		    fill: parent
		}

		onClicked: {
		    
		    if( lv1.currentIndex != index )
			lv1.currentIndex = index
		}

	    }
	    */
	    
	    Rectangle
	    {
		id: sep

		z: 10
		
		anchors
		{
		    top: parent.top
		    
		    left: parent.left
		    
		    right: parent.right
		}

		height: 2

		color: "black"

		visible: !flagFinal 
	    }
	    
	    FocusScope
	    {
		id: atlasframe

		anchors
		{
//		    left: parent.left
//		    right: parent.right
		    top: imgFrame.bottom
		    horizontalCenter: parent.horizontalCenter
		}		

		height : col.height

		width: Math.min( parent.width, lvatlas1.contentWidth )

		Column
		{
		    id: col
		    
		    anchors
		    {
			left: parent.left
			right: parent.right
		    }



		    ViewBoundariesRow
		    {
			id: viewboundariesrow

			anchors
			{
			    horizontalCenter: parent.horizontalCenter
			}

			height: 30
			
		        totalWidth: totalWidthGlobal

			playfieldDimX: config1.playfieldDimX

			model: boundarymodel

			modelMarkers: atlasmodel

			onSignalMouseAreaClicked: {

			    //console.log( "Band/Autostage clicked: ", index_, ", boundaries: ", boundaries_ );

			    gv1bar.color = model.get(index_).bg;
			    
			    gv1barti.text = "Selected: "+well_id+"/"+embryo_id+", autostage "+(index_+1);

			    if( metadata.count )
			    {
				var model_original = metadata.get(0).local_maxima_points

				model2.clear()
				
				if( 1 ) //index == 0 )
				{
				    for( var i=0; i < model_original.count; i++ )
				    {
					var obj = model_original.get(i);

					// Filter for centered points

					if( filterMetadataPoints(obj.x, obj.y) )
					{
					    //console.log( "Adding atlaspoint: x=", obj.x, ", y=", obj.y );

					    if( obj.x >= boundaries_.lower && obj.x <= boundaries_.upper )
					    {
						var _entry =  {

						    well_id : well_id,

						    embryo_id : embryo_id,

						    lo_id : Math.ceil(obj.x), 
						
						    x: Math.ceil(obj.x),

						    y: Math.ceil(obj.y),

						    delta_prev : obj.delta_prev,

						    flag_selected : false
						}
						
						//console.log( "append gv1, _entry.x: ", _entry.x, ", _entry.y: ", _entry.y )
							     
						model2.append( _entry );
					    }
					}

				    }
				}
			    }


			}
		    }

		    Item
		    {
			anchors
			{
			    left: parent.left
			    right: parent.right
			}

			height: 20
		    }
		    
	    ListView
	    {
		id: lvatlas1

		orientation: ListView.Horizontal

		visible: ! flagFinal
		
		anchors
		{
		    left: parent.left
		    right: parent.right
		}

		ListModel
		{
		    id: model_local_maxima_points_filtered
		}

		model: model_local_maxima_points_filtered

		
		Component.onCompleted: {

		    if( metadata.count )
		    {
		    var model_original = metadata.get(0).local_maxima_points

		    if( 1 ) //index == 0 )
		    {
			for( var i=0; i < model_original.count; i++ )
			{
			    var obj = model_original.get(i);

			    // Filter for centered points

			    if( filterMetadataPoints(obj.x, obj.y) )
			    {
				//console.log( "Adding atlaspoint: x=", obj.x, ", y=", obj.y );
				
				model_local_maxima_points_filtered.append( {

				    index_metadata : i,
				    
				    x: obj.x,

				    y: obj.y,

				    delta_prev : obj.delta_prev

				} );
			    }

			}
		    }
		    }

		}

		height: 100

		cacheBuffer: 20000000

		delegate: Component
		{
		    FocusScope
		    {
			anchors
			{
			    top: parent ? parent.top : undefined
			    bottom: parent ? parent.bottom : undefined
			}

			width: height

			opacity: 0
			
			Behavior on opacity { PropertyAnimation { duration: 400 } }
			
			Component.onCompleted: {

			    opacity = 1.0
			}

			property variant currentLoIdFromPoint : currentLoIdFromCoord( model.x, model.y )
			
			Rectangle
			{
			    anchors.fill: parent

			    opacity: debugLevel ? 1 : 0
				
			    color: Qt.rgba( Math.random(), Math.random(), 0.2 )
			}

			Image
			{
			    id: img

			    height: parent.height

			    width: parent.width

			    fillMode: Image.PreserveAspectFit

			    asynchronous: true

			    source: {

				return config1.getSourceImageFromModel( { 

				    well_id: well_id, 

				    embryo_id: embryo_id, 

				    lo_id: currentLoIdFromPoint
				} )


			    }

			    
			    function
			    slotLocalReload()
			    {
				source = "";

				source = config1.getSourceImageFromModel(model);
			    }
			    
			    Component.onCompleted: {

				root.signalGlobalReload.connect( slotLocalReload );

			    }

			    opacity: 0.78
			}

			Text
			{
			    anchors
			    {
				bottom: parent.bottom

				right: parent.right

				margins: 4
			    }

			    text: currentLoIdFromPoint

			    color: "white"
			}


			Text
			{
			    anchors
			    {
				top: parent.top

				left: parent.left

				margins: 4
			    }

			    text: index+"="+model.x+", "+model.y

			    color: "blue"

			    font 
			    {
				pointSize: 6
			    }
			}
			
		    }
		}
	    }




		    Rectangle
		    {
			id: statusbar_atlas1

			visible: !flagFinal && (lvatlas1.contentWidth > 1)

			anchors
			{
			    left: parent.left
			    right: parent.right
			}		

			height: 20

			Text
			{
			    anchors
			    {
				centerIn: parent
			    }

			    font
			    {
				pointSize: 7
			    }

			    text: "Atlas1 legend | .."
			}
		    }

		    
	    ListView
	    {
		id: lvatlas2

		orientation: ListView.Horizontal

		anchors
		{
//		    left: parent.left
		    //		    right: parent.right
		    horizontalCenter: parent.horizontalCenter
		}

		width: contentWidth ? Math.min( parent.width, contentWidth ) : parent.width

		height: 120

		model: atlasmodel

		spacing: 1
		
		Timer
		{
		    id: tiAtlasModel

		    interval: 5000

		    repeat: false

		    running: bandsModel.count > 0
		    
		    onTriggered: {

			var peak_model = metadata.get(0).boundaries_peaks; //bandsModel;

			atlasmodel.append( { flag_selected: false, well_id: well_id, embryo_id: embryo_id, lo_id: 1, type: "cap", bg: Qt.rgba( Math.random(), Math.random(), 0.2 )+"" } );

			var lasto;
			
			for( var i=peak_model.count-1; i >= 0; i-- )
			{
			    var o = peak_model.get( i );

			    var opos = playfieldDimX - o.pos
			    
			    if( lasto )
			    {
				//console.log( "append boundary i=", i, ", opos=", opos );
				
				var oprevpos = playfieldDimX - lasto.pos

				var mid = Math.floor( oprevpos + ((opos - oprevpos)/2) )
				
				//console.log( "oprev.pos=",  oprevpos, ", o.pos=",  opos, ", mid=", mid );

				var obj = { flag_selected: false, well_id: well_id, embryo_id: embryo_id, lo_id: mid, type: "mid", bg: Qt.rgba( Math.random(), Math.random(), 0.2 )+"" }  ;

				atlasmodel.append( obj );
			    }

			    var obj = { flag_selected: false, well_id: well_id, embryo_id: embryo_id, lo_id: opos, type: "boundary", bg: Qt.rgba( Math.random(), Math.random(), 0.2 )+"" }

			    atlasmodel.append( obj );

			    boundarymodel.append( obj );

			    lasto = o
			}


			if( 1 )
			{
			    var oprevpos = playfieldDimX - lasto.pos

			    var opos = playfieldDimX-1
			    
			    var mid = Math.floor( oprevpos + ((opos - oprevpos)/2) )

			    var obj = { flag_selected: false, well_id: well_id, embryo_id: embryo_id, lo_id: mid, type: "mid", bg: Qt.rgba( Math.random(), Math.random(), 0.2 )+"" }  ;

			    atlasmodel.append( obj );
			}


			var obj = { flag_selected: false, well_id: well_id, embryo_id: embryo_id, lo_id: playfieldDimX-1, type: "cap", bg: Qt.rgba( Math.random(), Math.random(), 0.2 )+"" }
			    
			atlasmodel.append( obj );

			boundarymodel.append( obj );

			running = false
		    }
		    
		}

		Component.onCompleted: {
		}

		cacheBuffer: 20000000

		delegate: Component
		{
		    FocusScope
		    {
			id: item

			anchors
			{
			    verticalCenter: parent.verticalCenter
			}

			height: parent ? parent.height : 0

			width: parent ? parent.height-70 : 0

			opacity: 0
			
			Behavior on opacity { PropertyAnimation { duration: 400 } }
			
			Component.onCompleted: {

			    opacity = 1.0
			}

			Rectangle
			{
			    anchors.fill: parent

			    opacity: debugLevel ? 1 : 0
				
			    color: Qt.rgba( Math.random(), Math.random(), 0.2 )
			}

			property variant bandInfo

			bandInfo: {

			    if( bandsModel.count )
			    {
				var result = bandsModelGetInfoOfBand( boundarymodel, findInBandsModel(boundarymodel, model) )

				return result
			    }

			    return {}
			}

			Column
			{
			    id: col
			    
			    anchors
			    {
				left: parent.left
				right: parent.right
			    }

			    spacing: 2

			    Text
			    {
				anchors
				{
				    horizontalCenter: parent.horizontalCenter
				}
				
				text: {

				    return index+"/"+model.lo_id+"="+( convertIdToTimeToHours(model.lo_id) )+" "+config1.timeHourTitle

				}

				color: "grey"

				font
				{
				    pointSize: 5
				}
			    }
			    
			    Rectangle
			    {
				height: 10

				anchors
				{
				    left: parent.left
				    right: parent.right
				}

				color: bandInfo.bgColor
			    }

			Image
			{
			    id: img
			    
			    height: parent.width

			    width: height

			    fillMode: Image.PreserveAspectFit

			    asynchronous: true

			    source: config1.getSourceImageFromModel(model)

			    
			    function
			    slotLocalReload()
			    {
				source = "";

				source = config1.getSourceImageFromModel(model);
			    }
			    
			    Component.onCompleted: {

				root.signalGlobalReload.connect( slotLocalReload );

			    }

			    opacity: 0.78
			}

			Text
			{
			    text: {

				if( debugLevel )
				    return model.lo_id + ", ("+( convertIdToTimeToHours(model.lo_id) )+" "+config1.timeHourTitle+", band: "+bandInfo.lowerPos+"-"+bandInfo.upperPos+"):"+model.type

				if( model.type == 'mid' )
				{
				    var dur = convertIdToTimeToHours(bandInfo.upperPos)-convertIdToTimeToHours(bandInfo.lowerPos);
				    
				    return "duration "+(dur).toFixed(1)+" h\nautostage: "+(bandInfo.index+1)
				}
				    
				return model.type //+"\nautostage: "+(bandInfo.index+1)+""
			    }

			    color: "black"

			    font
			    {
				pointSize: 5
			    }
			}

			}
		    }
		}
	    }


		    Rectangle
		    {
			id: statusbar_atlas2

			visible: lvatlas2.contentWidth > 1
			
			anchors
			{
			    left: parent.left
			    right: parent.right
			}		

			height: 20

			Text
			{
			    anchors
			    {
				centerIn: parent
			    }

			    font
			    {
				pointSize: 7
			    }

			    text: "Atlas2 ("+well_id  + "/" + embryo_id+") legend | .."
			}

			MouseArea
			{
			    anchors.fill: parent

			    onClicked: {

				if( lv1.currentIndex != index )
				    lv1.currentIndex = index
			    }
			}
		    }
		    
		}
	    }

            property real mx1 : flagKeyShiftDown ? 0 : (ma2.mouseX/ma2.width)*playfieldDimX

	    onMx1Changed: {

		crossHairRel.x = mx1
	    }

	    property real my1 : playfieldDimY - ((ma2.mouseY/ma2.height)*playfieldDimY)

	    onMy1Changed: {

		crossHairRel.y = my1
	    }

	    property int current_lo_id: currentLoIdFromCoord(mx1, my1)

	    property int loId: ( flagSyncLoId ) ? global_lo_id : current_lo_id

	    onCurrent_lo_idChanged: {

		global_lo_id = current_lo_id
	    }


	    FocusScope
	    {
		id: imgFrame

		anchors
		{
		    left: parent.left
		    right: parent.right
		}

		height: flagFinal ? 0 : img.height

		//clip: true
		
	    Image
	    {
		id: img

		visible: !flagFinal

		width: parent.width

		fillMode: Image.PreserveAspectFit

//		asynchronous: true

                function
                getImageSourceCurrent(imageBaseName_)
                {
                    return [ model1.rootDirImagePNG, model1.metadataSubdirs()[ model1.metadataSubdirsCurrentIndex ], imageBaseName_ ].join( "/" )
                }
                
		source:  getImageSourceCurrent( model.algorithm1_local_maxima_image_source )

		opacity: lv1.currentIndex == index ? 1.0 : 0.4

		Image
		{
		    id: imgInset

		    opacity: lv1.currentIndex == index ? 1.0 : 0.0

		    x: topLeftInset.x
		    y: topLeftInset.y

		    width: globalImgInsetWidth
		    
		    fillMode: Image.PreserveAspectFit

		    //asynchronous: true

		    source: {

			return config1.getSourceImageFromModel( { 

			well_id: well_id, 

			embryo_id: embryo_id, 

			lo_id: loId
			} )

		    }



		function
		slotLocalReload()
		    {
			// Skip, to not break the dynamic nature
			
			return;

			/*
		    source = "";

		    source = config1.getSourceImageFromModel( { 

			well_id: well_id, 

			embryo_id: embryo_id, 

			lo_id: loId
			} )
			*/
		}
		
		Component.onCompleted: {

		    root.signalGlobalReload.connect( slotLocalReload );

		}
		    
		    //smooth: true

		    onXChanged: {

			topLeftInset.x = x
		    }

		    onYChanged: {

			topLeftInset.y = y
		    }

		    Text
		    {
			anchors
			{
			    bottom: parent.bottom

			    right: parent.right

			    margins: 4
			}

			text: loId

			color: "white"
		    }

		    MouseArea
		    {
			anchors.fill: parent

			drag.target: parent

		    }
		}

		Rectangle
		{
		    id: playfield

		    color: "transparent"
		    //color: Qt.rgba( 1, 1, 1, 0.3 )

		    border.color: "green"
		    border.width: 2

		    x: playfield_candidate_p1.x
		    y: playfield_candidate_p1.y

		    width: playfield_candidate_p2.x - playfield_candidate_p1.x
		    height: playfield_candidate_p2.y - playfield_candidate_p1.y

		    function
		    diagonalLength()
		    {
			//var m = Math.max( width, height )
			//return Math.sqrt( m*m + m*m ) 
			
			return Math.sqrt( width*width + height*height ) 
		    }
		    //visible: ma.containsMouse

		    //clip: true

			Text
			{
			    anchors
			    {
				bottom: parent.bottom
				left: parent.left

				margins: 20
			    }

			    color: "white"

			    text: "Bands: "+lvBands.model.count

			    font
			    {
				pointSize: 9
			    }
			}

		    
		    Column
		    {
			id: lvBands

			visible: flagBands
			
			//interactive: false

			anchors
			{
			    centerIn: parent
			}
			
			width: parent.width
//			height: parent.height
/*
			header: Component
			{
			    Item
			    {
			    height: bandShift
			    width: playfield.width
			    }
			}
*/
			property real scaleXY: 1.5
			
			transform: [

			    Scale 
			    {
				origin
				{
				    x: playfield.width/2
				    y: playfield.height/2
				}

				xScale: lvBands.scaleXY
				yScale: lvBands.scaleXY
				   
			    },

			    Rotation
			    {
				angle: -90-45

				origin
				{
				    x: playfield.width/2
				    y: playfield.height/2
				}
			    }
			]

			ListModel
			{
			    id: test_peaks

			    ListElement { pos: 160 }
			}

			Component.onCompleted : {

			    var result = []

//			    var peak_model = test_peaks;

			    var peak_model = metadata.get(0).boundaries_peaks;

			    for( var i=0; i < peak_model.count; i++ )
			    {
				var o = peak_model.get( i );

				//result.push( playfieldDimX - o.pos );
				result.push( playfieldDimX - o.pos );
			    }

			    var result_reversed = result.reverse();

			    for( var i=0; i < result_reversed.length; i++ )
			    {
				bandsModel.append( { pos: result_reversed[i] } );
			    }

			    bandsModel.append( { pos: playfieldDimX } );
			}

			ListModel
			{
			    id: bandsModel
			}

			//cacheBuffer: 20000

			property variant model: bandsModel


			Item
			{
			    id: headerItem
			    
			    height: bandShift
			    width: playfield.width
			}
			
			Repeater
			{
			    anchors
			    {
				left: parent.left
				right: parent.right
			    }

			    model: lvBands.model
			    
			delegate: Component
			{
			    Rectangle
			    {
				id: band
				
				color: Qt.rgba( Math.random(), Math.random(), Math.random() ) //cnames.get(index) // model.name

				border.color: "white"
				border.width: (index%2==0)?1:0
				
				opacity: 0.8 //ma.containsMouse ? 0.8 : 0.2

				function
				getWidthFromIndex(index_)
				{
				    if( index_ > 0 )
				    {
					var result = model.pos - lvBands.model.get(index-1).pos

					return (result / playfieldDimY )*playfield.diagonalLength();
				    }

				    return (model.pos / playfieldDimY )*playfield.diagonalLength();

				}
				
				height: {

				    return (getWidthFromIndex(index) * widthFromIndexScale) /  lvBands.scaleXY;
				}

				width: playfield.width

				/*
				MouseArea
				{
				    id: ma

				    anchors
				    {
					fill: parent
				    }

				    preventStealing: true
				    
				    hoverEnabled: true

				    onClicked: console.log( ma, "clicked" )
				}
				*/
				
				Text
				{
				    id: ti
				    
				    anchors.centerIn: parent
				    
				    color: "white"

				    text: "height:"+parent.height.toFixed(1)+"pos:"+model.pos+", "+index+"/"+lvBands.model.count+"; prevPos: "+(index>0?lvBands.model.get(index-1).pos:0)

				    transform: [

					Rotation
					{
					    angle: 180

					    origin
					    {
						x: ti.width/2
						y: ti.height/2
					    }
					}
				    ]
				    
				    font
				    {
					pointSize: 5
					//bold: ma.containsMouse
				    }
				}
			    }
			}
			}
		    }

		    ListModel
		    {
			id: metadataModelSelection

			Component.onCompleted: {

			    for( var i=0; i < metadata.count; i++ )
			    {
				append( { index : i, flagSelected: false } );
			    }
			}
		    }

		    ListView
		{
		    id: lvMetadata
		    
		    anchors
		    {
			top: parent.top
			left: parent.left

			margins: 10
		    }

		    model: flagShowMetadata && (playfield.height > 0 && playfield.width > 0 ) ? metadata : []

		    width: contentWidth

		    height: contentHeight

		    spacing: 5
		    
		    delegate : Component
		    {
			FocusScope
			{
			    width: markerFrame.width

			    height: markerFrame.height

			    opacity : metadataModelSelection.get(index).flagSelected ? 1.0 : 0.4
			    
				MouseArea
				{
				    anchors.fill: parent

				    hoverEnabled: true

				    preventStealing: true

				    onContainsMouseChanged: {

					console.log( parent, "containsMouse=", containsMouse )				    
				    }

				    onClicked: {

					console.log( parent, "Clicked" )

					metadataModelSelection.setProperty( index, "flagSelected", !metadataModelSelection.get(index).flagSelected );
				    }
				}
				
			    
			Row
			{
			    id: markerFrame

			    anchors
			    {
				centerIn: parent
			    }

			    height: 10

			    spacing: 5
			    
			    Rectangle
			    {
				id: markerProper

				anchors
				{
				    verticalCenter: parent.verticalCenter
				}

				width: parent.height
				height: width

				radius: width/2

				color: cnames.get(index).name
				
				border.color: Qt.lighter( color, 1.3 )

				border.width: 1

				Rectangle
				{
				    anchors
				    {
					centerIn: parent
				    }

				    height: 1
				    width: 1
				}
			    }

			    Text
			    {
				anchors
				{
				    verticalCenter: parent.verticalCenter
				}

				text: index + " | " + subdir + " ( n=" + local_maxima_points.count + " )"

				color: "white"

				font
				{
				    pointSize: 7
				}
			    }
			}
			}
		    }
		}




		    // MARKERS
		    
		Repeater
		{
		    id: repMetadata
		    
		    anchors
		    {
			fill: parent
		    }

		    model: flagShowMetadata && (playfield.height > 0 && playfield.width > 0 ) ? metadata : []

		Repeater
		    {
			id: repMarkers

		    anchors
		    {
			fill: parent
		    }

		    property int indexParent: index
		    
  	            model: metadataModelSelection.get(index).flagSelected ? local_maxima_points : []

		    delegate : Component
		    {
			Item
			{
			    id: markerFrame

			    property bool flagFiltered: filterMetadataPoints(model.x, model.y) 

			    width: 10
			    height: 10

			    x:                    (model.x*playfield_scale_factor_x) - (width/2)

			    y: playfield.height - (model.y*playfield_scale_factor_y) - (height/2)

			    Rectangle
			    {
				id: markerProper

				anchors
				{
				    fill: parent
				}

				radius: width/2

				color: {

				    var found = roiModelFind( roimodel_global, markerFrame.x+markerFrame.width/2, markerFrame.y+markerFrame.height/2 );

				    if( found == -1 )
					return cnames.get(repMarkers.indexParent).name;
				    
				    return roimodel_global.get(found).bgcolor
				}
				
				border.color: Qt.lighter( color, 1.3 )

				border.width: 1

				opacity: flagFiltered ? 1.0 : 0.2
			    }

			    Rectangle
			    {
				visible: flagFiltered
				
				anchors
				{
				    centerIn: parent
				}

				height: 1
				width: 1
			    }
			    
			    
			    Text
			    {
				anchors
				{
				    horizontalCenter: parent.horizontalCenter

				    top: parent.bottom

				    topMargin: 4
				}

				text: index

				color: "white"

				opacity: flagFiltered ? 1.0 : 0.2

				font
				{
				    pointSize: 7
				}
			    }
			}
		    }
		}
		}
		    


		Repeater
		{
		    anchors
		    {
			fill: parent
		    }

		    model: roimodel_global
		    
		    delegate : Component
		    {
			RoiRectangle
			{
			    point1: Qt.point( model.point1.x, model.point1.y )

			    point2: Qt.point( model.point2.x, model.point2.y )

			    border.color: model.bgcolor
			}
		    }
		}

		Repeater
		{
		    anchors
		    {
			fill: parent
		    }

		    model: roimodel // local
		    
		    delegate : Component
		    {
			RoiRectangle
			{
			    point1: Qt.point( model.point1.x, model.point1.y )

			    point2: Qt.point( model.point2.x, model.point2.y )

			    border.color: model.bgcolor
			}
		    }
		}

		    
		    Rectangle
		    {
			id: crossHairH

			visible: root.state != "data_selection_mode"

			anchors
			{
			    left: parent.left
			    right: parent.right
			}

			height: 1

			y: ((playfieldDimY-crossHairRel.y)/playfieldDimY) * parent.height

			opacity: ma2.containsMouse ? 1.0 : 0.2
		    }

		    Rectangle
		    {
			id: crossHairV

			visible: root.state != "data_selection_mode"

			anchors
			{
			    top: parent.top
			    bottom: parent.bottom
			}
			
			width: 1

			x: (crossHairRel.x/playfieldDimX) * parent.width

			opacity: ma2.containsMouse ? 1.0 : 0.2
		    }


		    MouseArea
		    {
			id: ma2

			enabled: root.state != "data_selection_mode"
			
			anchors
			{
			    fill: parent
			}

			hoverEnabled: true

			//MUE: Qt6
			// see also: http://osr600doc.sco.com/en/SDK_qt3/qcursor.html
			
			cursorShape: enabled ? Qt.BlankCursor : Qt.ArrowCursor // CrossCursor

			acceptedButtons: Qt.LeftButton | Qt.RightButton


			
			onClicked: (mouse) => {

                        console.log( "Licked mouse: ", mouse );
                        
			    if( lv1.currentIndex != index )
				lv1.currentIndex = index

			    if( mouse.modifiers & Qt.AltModifier )
			    {
				console.log( "Alt clicked" )

				if( mouse.button == Qt.RightButton )
				{
				    console.log( "Alt Right clicked" )

				    roi_candidate_p2.x = mouse.x
				    roi_candidate_p2.y = mouse.y

				    appendRoiRectGlobal(roi_candidate_p1, roi_candidate_p2)

				    var _lo_id_abs =  ( (  ( (roi_candidate_p2.x) - (roi_candidate_p1.x) ) / 2  ) + roi_candidate_p1.x )

				    var _lo_id = ( (  _lo_id_abs / playfield.width ) * playfieldDimX ).toFixed(0)

				    console.log( "roi yield, lo_id=", _lo_id )

				    for( var i=0; i < lv1.model.count; i++ )
				    {
					var _obj = lv1.model.get(i);

					_obj.atlasmodel.append( { well_id: _obj.well_id, embryo_id: _obj.embryo_id, lo_id: _lo_id, type : "manual" } );
				    }
				    
				}
				else
				{
				    roi_candidate_p1.x = mouse.x
				    roi_candidate_p1.y = mouse.y
				}
			    }
			    else
			    {
				console.log( "Adding lo_id: ", current_lo_id )
				
				atlasmodel.append( { well_id: well_id, embryo_id: embryo_id, lo_id: current_lo_id, type : "manual" } );
			    }

			}
/*
			Rectangle
			{
			    anchors.fill: parent

			    color: "green"

			    opacity: 0.3
			}
*/
		    }


		    
		    Text
		    {
			anchors
			{
			    right: parent.right

			    bottom: parent.bottom
			}

			color: "white"

			text: {
			    
			    return mx1.toFixed(2)+", "+my1.toFixed(2)

			}
		    }
		}

		Rectangle
		{
		    id: marker

		    color: "transparent"
		    
		    border.color: "red"
		    border.width: 3
		    
		    width: 10
		    height: 10


		    visible: ma.containsMouse
		    
		    Rectangle
		    {
			anchors
			{
			    centerIn: parent
			}
			
			color: "transparent"

			width: 4
			height: 4
		    }

		}

		MouseArea
		{
		    id: ma

		    z: -2
		    
		    anchors
		    {
			fill: parent
		    }

		    hoverEnabled: ! ma2.containsMouse

		    /*
		    onContainsMouseChanged: {

			if( containsMouse )
			    lv1.currentIndex = index
		    }
		    */

		    onPositionChanged: (mouse) => {

			marker.x = mouse.x - marker.width/2

			marker.y = mouse.y - marker.width/2
		    }

		    acceptedButtons: Qt.LeftButton | Qt.RightButton
		    
		    onClicked: (mouse) => {

			if( mouse.modifiers & Qt.ControlModifier )
			    console.log( "..Control modifier" )

			if( mouse.modifiers & Qt.AltModifier )
			    console.log( "..Alt modifier" )

			if( mouse.modifiers & Qt.ShiftModifier )
			    console.log( "..Shift modifier" )

			if( mouse.modifiers & Qt.MetaModifier )
			    console.log( "..Meta modifier" )

			if( mouse.modifiers & Qt.ControlModifier )
			{
			    if( mouse.button == Qt.RightButton )
			    {
				console.log( "..Right mouse" )

				playfield_candidate_p2.x = mouse.x
				playfield_candidate_p2.y = mouse.y
			    }
			    else
			    {
				playfield_candidate_p1.x = mouse.x
				playfield_candidate_p1.y = mouse.y
			    }
			}
			else
			{
			    if( lv1.currentIndex != index )
				lv1.currentIndex = index

			    //model2.initModelAll( well_id, embryo_id )
			}
			

		    }
		}

	    }

		FocusScope
		{
		    anchors
		    {
			top: parent.top

			left: parent.left

			margins: flagFinal ? 0 : 15
		    }

		    height: 30

		    width: row2.width
		    
		    z: parent.z + 1000

		    Rectangle
		    {
			anchors.fill: parent

			color: "transparent"
		    }
			
		    Row
		    {
			id: row2
			
			anchors
			{
			    top: parent.top
			    bottom: parent.bottom
			}
			
			spacing: 2

			WidgetCheckBox
			{
			    anchors
			    {
				verticalCenter: parent.verticalCenter
			    }

			    height: parent.height
			    width: parent.height

			    Component.onCompleted: flagSelected = model.flag_selected
			    
			    onFlagSelectedChanged: {

				lv1.model.setProperty( index, 'flag_selected',  flag_selected?0:1 )
			    }
			}
			

			Text
			{
			    //visible: ! flagFinal
			    
			    anchors
			    {
				verticalCenter: parent.verticalCenter
			    }

			    text: well_id  + "/" + embryo_id
			}
		    }
		}
	    }

	}

	}
    }

    Rectangle
    {
	id: gv1line1
	
	color: "black"

	anchors
	{
	    left: parent.left
	    right: parent.right
	    bottom: gv1bar.top
	}

	height: 1
    }

    Rectangle
    {
	id: gv1bar
	
	color: "lightgrey"

	anchors
	{
	    left: parent.left
	    right: parent.right
	    bottom: gv1.top
	}

	height: 20

	Text
	{
	    id: gv1barti
	    
	    anchors
	    {
		left: parent.left
		leftMargin: 4
		
		verticalCenter: parent.verticalCenter
	    }


	    color: "white"
	}

    }

    GridView
    {
	id: gv1
	
	anchors
	{
	    bottom: statusbar.top
	    left: parent.left
	    right: parent.right
	}		

	height: flagGridShow ? parent.height * 0.25 : 0
	
	model: model2

	cacheBuffer: 2000000
	
	cellWidth: (width/14)

	cellHeight: cellWidth + 20
	
	clip: true
	
	delegate: Component
	{
	    Item
	{
	    id: gv1Item
	    
	    width: gv1.cellWidth

	    height: gv1.cellHeight

	    property bool flagCurrent: global_lo_id == model.lo_id

	    onFlagCurrentChanged: {

		if( flagCurrent )
		    gv1.currentIndex = index
	    }

	    Column
	    {
		anchors
		{
		    left: parent.left
		    right: parent.right
		}

		spacing: 2

		/*
	    Rectangle
	    {
		id: bandIndicator

		anchors
		{
		    left: parent.left
		    right: parent.right
		}

		height: 10
	    }
		*/
		
	    Image
	    {
		id: img

		height: gv1.cellHeight

		width: gv1.cellWidth

		fillMode: Image.PreserveAspectFit

		asynchronous: true

		source: config1.getSourceImageFromModel(model)

		function
		slotLocalReload()
		{
		    source = "";

		    source = config1.getSourceImageFromModel(model);
		}
		
		Component.onCompleted: {

		    root.signalGlobalReload.connect( slotLocalReload );

		}

		//smooth: true

		Rectangle
		{
		    anchors.fill: parent

		    border.color: "green"

		    border.width: 2

		    color: "transparent"
		    
		    opacity: parent.parent.flagCurrent ? 1.0 : 0.0
		}
	    }




	    Text
	    {
		anchors
		{
		    right: parent.right
		}

		text: model.lo_id+"/"+global_lo_id

		color: "black"

		font
		{
		    pointSize: 6
		    bold: flagCurrent
		}
	    }

		
	    }

			WidgetCheckBox
			{
			    anchors
			    {
				top: parent.top
				left: parent.left

				margins: 10
			    }

			    height: 15
			    width: 15

			    Component.onCompleted: flagSelected = model.flag_selected
			    
			    onFlagSelectedChanged: {

				gv1.model.setProperty( index, 'flag_selected',  flag_selected )
			    }
			}
			
	}	    
	    
	}
	
    }














    Rectangle
    {
	color: "black"

	anchors
	{
	    top: parent.top
	    bottom: parent.bottom
	    right: gv2.left
	}

	height: 1
	visible: gv2.visible
    }

    

    Rectangle
    {
	anchors.fill: gv2
	opacity: 0.7
	visible: gv2.visible
    }

    GridView
    {
	id: gv2
	
	anchors
	{
	    top: parent.top
	    
	    bottom: gv1line1.top
	    right: parent.right
	}		

	width: flagAtlasShow ? parent.width * 0.15 : 0
	
	model: (lv1.model.count==1 || lv1.model.get(lv1.currentIndex)) ? lv1.model.get(lv1.currentIndex).atlasmodel : []

	cacheBuffer: 2000000
	
	cellWidth: (width) * 0.97
	
	cellHeight: cellWidth
	
	clip: true
	
	delegate: Component
	{
	    Item
	{
	    width: gv2.cellWidth

	    height: gv2.cellHeight

	    MouseArea
	    {
		anchors.fill: parent

		acceptedButtons: Qt.LeftButton | Qt.RightButton

		onClicked: (mouse) => {

		    if( mouse.button == Qt.RightButton )
		    {
			gv2.model.remove( index )
		    }

		}
	    }

	    /*
	    property bool flagCurrent: global_lo_id == model.lo_id

	    onFlagCurrentChanged: {

		if( flagCurrent )
		    gv2.currentIndex = index
	    }
	    */

	    Image
	    {
		id: img

		height: gv2.cellHeight

		width: gv2.cellWidth

		fillMode: Image.PreserveAspectFit

		asynchronous: true

		source: config1.getSourceImageFromModel(model)

		
		function
		slotLocalReload()
		{
		    source = "";

		    source = config1.getSourceImageFromModel(model);
		}
		
		Component.onCompleted: {

		    root.signalGlobalReload.connect( slotLocalReload );

		}

		//smooth: true

		/*
		Rectangle
		{
		    anchors.fill: parent

		    opacity: parent.parent.flagCurrent ? 0.0 : 0.4
		}
		*/
	    }

	    Text
	    {
		anchors
		{
		    bottom: parent.bottom

		    right: parent.right

		    margins: 4
		}

		color: "white"

		text: model.lo_id

		//font.bold: flagCurrent
	    }

	    Text
	    {
		anchors
		{
		    left: parent.left
		    top: parent.top
		    margins: 4
		    
		}

		color: "white"
		
		text: well_id  + "/" + embryo_id
	    }
	}
	}
	
    }

    

    
    Rectangle
    {
	color: "black"

	anchors
	{
	    left: parent.left
	    right: parent.right
	    bottom: statusbar.top
	}

	height: 1
    }
    
    Rectangle
    {
	id: statusbar
	
	anchors
	{
	    bottom: parent.bottom
	    left: parent.left
	    right: parent.right
	}		

	height: 20

	Flickable
	{
	    anchors
	    {
		fill: parent
	    }

	    contentWidth: tiStatus.width

	    contentHeight: parent.height
	    
	Text
	    {
		id: tiStatus

	    anchors
	    {
		verticalCenter: parent.verticalCenter
	    }

	    font
	    {
		pointSize: 7
	    }

	    text: "DevTimeStudio (V036), Keys: RightPanelToggle=<R>, ShowGridTimelineView=<Tab>, ResetMouseArea=<Esc>, ResetRois=<Esc+Alt>, Set-MouseArea-topLeft=<Control>+<Mouse-Left>, Set-MouseArea-bottomRight=<Control>+<Mouse-Right>, Set-Roi-topLeft=<Alt>+<Mouse-Left>, Set-Roi-bottomRight=<Alt>+<Mouse-Right>, IncreaseInsetSize=<Plus> | DecreaseInsetSize=<Minus> (+<Shift> for fine steps), ShowMetadat=<M> ToggleDebugLevel=<D>, ToggleBands=<B>, ToggleDataSelectionMode=<P>, LiveMode-XFixed=<Shift>, <FinalVersion>=<F>, ConsoleOutSelectionReport=<W>, ConsoleOutReport=<Shift+W>, ConsoleOutSelectedFileCopy=<S>, ConsoleOutFileCopy=<Shift+S>"
	    }
	}
    }
}
		
