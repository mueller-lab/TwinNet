import QtQuick 2.6

import "../../..";

import "../../../../cache/QML";

ViewSummarize
{
    id: root

    objectName: "app1-medakashort.qml"
    
    ConfigMedakaShort1
    {
	id: config1
    }

    ListModelExperimentComparisonmedakashort1
    {
	id: model1

	interval: 1000

	sourceDataArrayLimit: config1.listModelLimit

	filterExperimentParams : config1.filterExperimentParams()
	
	onRunningChanged: {

	    root.state = running ? "loading" : ""
	}
	
    }   

}
