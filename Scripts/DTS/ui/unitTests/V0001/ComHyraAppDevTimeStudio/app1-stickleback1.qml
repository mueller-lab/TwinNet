import QtQuick 2.6

import "../../..";

import "../../../../cache/QML";

ViewSummarize
{
	id: root

    objectName: "app1-stickleback.qml"

    ConfigStickleback1
    {
	id: config1
    }

    ListModelExperimentComparisonstickleback1
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
