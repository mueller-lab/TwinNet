import QtQuick 2.6

import "../../..";

ViewSummarize
{
	id: root

    objectName: "app1-zebrafish.qml"

    ConfigZebrafish1
    {
	id: config1
    }


    ListModelExperimentComparisonZebrafish1
    {
	id: model1

	interval: 1000

	filterExperimentParams : config1.filterExperimentParams()

	sourceDataArrayLimit: config1.listModelLimit

	onRunningChanged: {

	    root.state = running ? "loading" : ""
	}
	
    }   

}
