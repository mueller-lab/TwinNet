import QtQuick 2.6

import "../../..";

ViewSummarize
{
    id: root

    objectName: "app1-medaka.qml"

    ConfigMedaka1
    {
	id: config1
    }

    ListModelExperimentComparisonMedaka1
    {
	id: model1

	interval: 1000

	sourceDataArrayLimit: config1.listModelLimit

	onRunningChanged: {

	    root.state = running ? "loading" : ""
	}
	
    }   

}
