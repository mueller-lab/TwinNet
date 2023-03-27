
import QtQuick 2.3;

ListModel
{
   id: root

   property variant sourceDataArray: []

   property bool running: true
    
   property int interval: 100

   property int currentIndex: 0
    
   property variant timer1: Timer
   {
       running: root.running

       interval: root.interval

       repeat: true
       
       onTriggered: {

       //	   console.log( root, "currentIndex=", currentIndex, " < (sourceDataArray.length=", sourceDataArray.length, ")" );
	   
	   if( currentIndex < (sourceDataArray.length) )
	   {
	       var obj = sourceDataArray[currentIndex];

	       root.append( obj );
	   }
	   else
	   {
	       root.running=false
	   }

	   currentIndex = currentIndex + 1
       }
   }

    property int sourceDataArrayLimit: 30


//    property bool flagLoaded: false
    
    property variant filterExperimentParams;

    function
    filterExperimentModelEntry(model_)
    {
	if( typeof filterExperimentParams != 'undefined' )
	{
	    for( var i=0; i < filterExperimentParams.table.length; i++ )
	    {
		var rec_ = filterExperimentParams.table[i];
		
		if( rec_.well_id+"/"+rec_.embryo_id == model_.well_id+"/"+model_.embryo_id )
		{
		    return true;
		}
	    }

	    return false;
	}
	
	return true;
    }

   function
   sourceDataAppend(_entry)
    {
	if( (sourceDataArray.length < sourceDataArrayLimit) )
	{
	    if( filterExperimentModelEntry(_entry) )
	    {
		var arr = sourceDataArray;

	    	arr.push( _entry );

	    	sourceDataArray = arr;
            }
	}
   }
	

   Component.onCompleted: {

   }

}

