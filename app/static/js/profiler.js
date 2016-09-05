
function callApi(url, method, data, onSuccess, onFail) {
    $.ajax({
        url: url,
        method: method,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),
        xhrFields: {
            withCredentials: true
	},
        success: function(data) {
            if (onSuccess) {
                onSuccess(data);
            }
        },
        error: function(err) {
            alert("Error calling API:" + JSON.stringify(err));
            if (onFail) {
                onFail(JSON.stringify(err));
            }
	}
    });
}

var chartOption = {

    ///Boolean - Whether grid lines are shown across the chart
    scaleShowGridLines : true,

    //String - Colour of the grid lines
    scaleGridLineColor : "rgba(0,0,0,.05)",

    //Number - Width of the grid lines
    scaleGridLineWidth : 1,

    //Boolean - Whether to show horizontal lines (except X axis)
    scaleShowHorizontalLines: true,

    //Boolean - Whether to show vertical lines (except Y axis)
    scaleShowVerticalLines: true,

    //Boolean - Whether the line is curved between points
    bezierCurve : true,

    //Number - Tension of the bezier curve between points
    bezierCurveTension : 0.4,

    //Boolean - Whether to show a dot for each point
    pointDot : true,

    //Number - Radius of each point dot in pixels
    pointDotRadius : 4,

    //Number - Pixel width of point dot stroke
    pointDotStrokeWidth : 1,

    //Number - amount extra to add to the radius to cater for hit detection outside the drawn point
    pointHitDetectionRadius : 20,

    //Boolean - Whether to show a stroke for datasets
    datasetStroke : true,

    //Number - Pixel width of dataset stroke
    datasetStrokeWidth : 2,

    //Boolean - Whether to fill the dataset with a colour
    datasetFill : true,

    //String - A legend template
    legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].strokeColor%>\"><%if(datasets[i].label){%><%=datasets[i].label%><%}%></span></li><%}%></ul>"

};

mapDataSets = {
    'avg': 0,
    'min': 1,
    'max': 2,
    'count': 3
};

function getNewDataSetConfig(dataset) {
    if (dataset == 'avg') {
	return {
            label: 'avg',
            fillColor: "rgba(0,255,0,0.2)",
            strokeColor: "rgba(0,255,0,1)",
            pointColor: "rgba(0,255,0,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(0,255,0,1)",
            data: []
	};
    }
    else if (dataset == 'min') {
	return {
            label: 'min',
            fillColor: "rgba(0,0,255,0.2)",
            strokeColor: "rgba(0,0,255,1)",
            pointColor: "rgba(0,0,255,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(0,0,255,1)",
            data: []
	};	
    }
    else if (dataset == 'max') {
	return {
            label: 'max',
            fillColor: "rgba(255,0,0,0.2)",
            strokeColor: "rgba(255,0,0,1)",
            pointColor: "rgba(255,0,0,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(255,0,0,1)",
            data: []
	};	
    }
    else if (dataset == 'count') {
	return {
            label: 'count',
            fillColor: "rgba(151,187,205,0.2)",
            strokeColor: "rgba(151,187,205,1)",
            pointColor: "rgba(151,187,205,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(151,187,205,1)",
            data: []
	};	
    }
}

function dateAddMinutes(date, minutes) {
    return new Date(date.getTime() + minutes*60000);
}

function dateInRange(d, start, end) {
    return (start <= d && d < end);
}

function dateCloseTo(d1, d2, interval) {
    var start = dateAddMinutes(d1, -interval);
    var end = dateAddMinutes(d1, interval);
    return dateInRange(d2, start, end);
}

function recordDataPoint(route, events, data, needMerge) {
    for (var k in data) {
	if (!(k in mapDataSets)) {
	    continue;
	}
	var curValue = data[k];

	if (!(mapDataSets[k] in events['datasets'])) {
	    events['datasets'][mapDataSets[k]] = getNewDataSetConfig(k);
	    events['datasets'][mapDataSets[k]]['label'] = route + " " + k;
	}

	var len = events['datasets'][mapDataSets[k]]['data'].length;
	if (len > 0 && needMerge) {
	    var values = events['datasets'][mapDataSets[k]]['data'];
	    if (k == 'avg') {
		var prevCount = events['datasets'][mapDataSets['count']]['data'][len - 1];
		if ('count' in data) {
		    var curCount = data['count'];
		    values[len-1] = ((values[len-1] * prevCount) + (curValue * curCount)) / (prevCount + curCount);
		}
	    }
	    else if (k == 'min') {
		values[len-1] = Math.min(values[len-1], curValue);
	    }
	    else if (k == 'max') {
		values[len-1] = Math.max(values[len-1], curValue);
	    }
	    else if (k == 'count') {
		values[len-1] += curValue;
	    }
	}
	else {
	    events['datasets'][mapDataSets[k]]['data'].push(curValue);
	}
    }
}

function createLatencyChartDatas(data, startDate, interval) {
    // separate each event into categories
    var global = "global";
    var prevDate = new Date(startDate);
    var events = {global: {'datasets': [], 'time': []}};
    events[global]['time'].push(prevDate);
    for (var i in data) {
	var route = data[i]['route'];
	if (!(route in events)) {
	    events[route] = {'datasets': [], 'time': []};
	}

	var len = events[global]['time'].length;
	var lenRoute = events[route]['time'].length;
	var curDate = new Date(data[i]['time']['$date']);

	var prevRouteDate = new Date(startDate);
	if (lenRoute > 0) {
	    prevRouteDate = events[route]['time'][lenRoute - 1];
	}
	else {
	    events[route]['time'].push(prevRouteDate);
	}

	var dateGlobalIntoInterval = dateCloseTo(prevDate, curDate, interval / 2);
	var dateRouteIntoInterval = dateCloseTo(prevRouteDate, curDate, interval / 2);

	recordDataPoint(global, events[global], data[i], dateGlobalIntoInterval);
	recordDataPoint(route, events[route], data[i], dateRouteIntoInterval);

	if (!dateRouteIntoInterval) {
	    prevRouteDate = dateAddMinutes(prevRouteDate, interval);
	    events[route]['time'].push(prevRouteDate);
	}

	if (!dateGlobalIntoInterval) {
	    prevDate = dateAddMinutes(prevDate, interval);
	    events[global]['time'].push(prevDate);
	}
    }

    return events;
}

function createApiCallChartDatas(latencyDatas)
{
    var events = {'datasets': [], 'apiCalls': []};

    var i = 0;
    for (var apiCall in latencyDatas) {
	events['apiCalls'].push(apiCall);

	var j = 0;
	for (var dataset in latencyDatas[apiCall]['datasets']) {
	    var newDataset;

	    if (i == 0) {
		newDataset = $.extend({}, latencyDatas[apiCall]['datasets'][dataset]);
		if (newDataset.label.endsWith('avg')) {
		    newDataset.label = 'avg';
		}
		if (newDataset.label.endsWith('min')) {
		    newDataset.label = 'min';
		}
		if (newDataset.label.endsWith('max')) {
		    newDataset.label = 'max';
		}
		if (newDataset.label.endsWith('count')) {
		    newDataset.label = 'count';
		}
		newDataset.data = [];
		events['datasets'].push(newDataset);
	    }
	    newDataset = events['datasets'][j];


	    var newData;
	    if (newDataset.label == 'avg') {
		newData = -1;
		var currentAvg = 0;
		var currentCount = 0;
		for (var d in latencyDatas[apiCall]['datasets'][dataset].data) {
		    var nextAvg = latencyDatas[apiCall]['datasets'][dataset].data[d];
		    var nextCount = latencyDatas[apiCall]['datasets'][3].data[d];
		    if (newData == -1) {
			newData = nextAvg;
			currentAvg = nextAvg;
			currentCount = nextCount;
		    }
		    else {
			
			newData = ((currentAvg * currentCount) + (nextAvg * nextCount)) / (currentCount + nextCount);
			currentAvg = nextAvg;
			currentCount += nextCount;
		    }
		}
	    }
	    else if (newDataset.label == 'min') {
		newData = 99999999;
		for (var d in latencyDatas[apiCall]['datasets'][dataset].data) {
		    newData = Math.min(newData, latencyDatas[apiCall]['datasets'][dataset].data[d]);
		}
	    }
	    else if (newDataset.label == 'max') {
		newData = 0;
		for (var d in latencyDatas[apiCall]['datasets'][dataset].data) {
		    newData = Math.max(newData, latencyDatas[apiCall]['datasets'][dataset].data[d]);
		}
	    }
	    else if (newDataset.label.endsWith('count')) {
		newData = 0;
		for (var d in latencyDatas[apiCall]['datasets'][dataset].data) {
		    newData += latencyDatas[apiCall]['datasets'][dataset].data[d];
		}
	    }

	    newDataset.data.push(newData);
	    j++;
	}

	i++;
    }
    return events;
}

var latencyChartDatas = null;
var apiCallsChartDatas = null;
var showDatasets = ["count", "avg", "min", "max"];
var showRoutes = ["global"];

function updateChart()
{
    var latencyDatasets = [];
    var apiCallsDatasets = [];

    for (var i in showRoutes) {
	var r = showRoutes[i];
	var routeDataset = [];
	for (var j in showDatasets) {
	    routeDataset.push(r + " " + showDatasets[j]);
	}

	for (var j in latencyChartDatas[r]['datasets']) {
	    if (routeDataset.indexOf(latencyChartDatas[r]['datasets'][j]['label']) >= 0) {
		latencyDatasets.push(latencyChartDatas[r]['datasets'][j]);
	    }
	}
    }

    for (var j in apiCallsChartDatas['datasets']) {
	if (showDatasets.indexOf(apiCallsChartDatas['datasets'][j]['label']) >= 0) {
	    apiCallsDatasets.push(apiCallsChartDatas['datasets'][j]);
	}
    }

    var latencyChartData = {
	labels: latencyChartDatas["global"]['time'],
	datasets: latencyDatasets
    };

    var apiCallsyChartData = {
	labels: apiCallsChartDatas['apiCalls'],
	datasets: apiCallsDatasets
    };

    $("#latency_chart_container").html("<canvas id=\"latency_chart\" width=\"1000\" height=\"800\"></canvas>");
    var ctx = $("#latency_chart").get(0).getContext("2d");
    var chart = new Chart(ctx).Line(latencyChartData, chartOption);
    $("#latency_chart_legend").html(chart.generateLegend());

    $("#calls_chart_container").html("<canvas id=\"calls_chart\" width=\"1000\" height=\"800\"></canvas>");
    var ctx = $("#calls_chart").get(0).getContext("2d");
    var chart = new Chart(ctx).Bar(apiCallsyChartData, chartOption);
    $("#calls_chart_legend").html(chart.generateLegend());
}

function selectDataset(showDataset) {
    showDatasets = showDataset;
    updateChart();
}

function selectRoute(showR) {
    showRoutes = showR;
    updateChart();
}

function fetchLatencyData(sid, type, period, fromDate, toDate, interval) {
    callApi('/service/profiler/history/' + sid + '/' + type, 'POST', {period: period, from: fromDate, to: toDate}, function(data) {
	latencyChartDatas = createLatencyChartDatas(data['events'], fromDate, interval);
	apiCallsChartDatas = createApiCallChartDatas(latencyChartDatas);
	updateChart();
    });
}

function refreshGraph(service, eventType) {
    var fromDate = $(".input-daterange .start").datepicker("getDate").valueOf();
    var toDate = $(".input-daterange .end").datepicker("getDate").valueOf();
    var interval = parseInt($("#interval").val());
    fetchLatencyData(service, eventType, "", fromDate, toDate, interval);
}


// set dates
$(".input-daterange .start").datepicker('update', new Date(Date.now() - (1*60*60*24*1000)));
$(".input-daterange .end").datepicker('update', new Date());
$(".input-daterange .start").datepicker('update');
$(".input-daterange .end").datepicker('update');
