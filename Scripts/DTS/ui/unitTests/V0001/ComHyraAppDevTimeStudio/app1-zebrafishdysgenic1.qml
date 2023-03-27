import QtQuick 2.6

import "../../..";

ViewSummarize
{
	id: root

    objectName: "app1-zebrafishdysgenic1.qml"

    ConfigZebrafishDysgenic1
    {
	id: config1
    }


    ListModelExperimentComparisonZebrafish1
    {
	id: model1

	interval: 750

	filterExperimentParams : config1.filterExperimentParams()

	sourceDataArrayLimit: config1.listModelLimit

	onRunningChanged: {

	    root.state = running ? "loading" : ""
	}
	
    }   

}
