import QtQuick 2.6

import "../../..";

import "../../../../cache/QML";

ViewSummarize
{
    id: root

    objectName: "app1-celegans.qml"

    ConfigCElegans1
    {
	id: config1
    }

    ListModelExperimentComparisoncelegans1
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
