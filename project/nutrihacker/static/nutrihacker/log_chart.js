var timerange = "past7";
var nutrient = "calories";

var ctx  = document.getElementById('myChart').getContext('2d');
var saved_data = {
	'past7': null,
	'past30': null,
	'week': null,
	'month': null,
	'year': null
};

var chart = new Chart(ctx, {
	type: 'line',
	data: {
		labels: [],
		datasets: [{
			label: null,
			data: null,
			backgroundColor: '#008000',
			borderColor: '#008000',
			pointRadius: 4,
			pointHoverRadius: 5,
			fill: false,
			lineTension: 0
			
		}, {
			label: 'Daily average: ',
			data: null,
			backgroundColor: Samples.utils.transparentize('rgb(52, 152, 219)'),
			borderColor: 'rgb(52, 152, 219)',
			pointRadius: 0,
			pointHitRadius: 0,
			pointHoverRadius: 0,
			fill: false,
			hidden: false
		}, {
			label: 'Calorie goal: ' + goal,
			data: null,
			backgroundColor: Samples.utils.transparentize('rgb(236, 112, 99)'),
			borderColor: 'rgb(236, 112, 99)',
			pointRadius: 0,
			pointHitRadius: 0,
			pointHoverRadius: 0,
			fill: false, //'+1' // used for goal range
			hidden: false
		}, 
		// { // used for goal range
		// 	label: null,
		// 	data: null,
		// 	borderColor: 'rgb(171, 235, 198)',
		// 	pointRadius: 0,
		// 	pointHitRadius: 0,
		// 	pointHoverRadius: 0,
		// 	fill: false
		// }
		]
	},
	options: {
		responsive: true,
		legend: {
			display: true,
			position: 'top',
			align: 'end',
			labels: {
				filter: function(item, chart) {
					// always hides the data label in the legend
					// shows the calorie goal dataset if calories is selected
					if (nutrient == "calories")
						return item.datasetIndex !== 0;
					else
						return item.datasetIndex !== 0 && item.datasetIndex !== 2;
				}
			}
		},
		layout: {
            padding: {
                left: 30,
                right: 50,
                top: 10,
                bottom: 15
            }
        },
        scales: {
        	xAxes: [{
        		scaleLabel: {
        			display: false,
        			labelString: ''
        		}
        	}],
        	yAxes: [{
        		scaleLabel: {
        			display: true,
        			labelString: "Calories (kcal)"
        		},
        		ticks: {
        			beginAtZero: true
        		}
        	}]
        }
	}
});

// when paged is loaded, retrieves data for past seven days and updates chart
$(document).ready(function() {
	$.ajax({
		url: url,
		data: {
			'user': user,
			'timerange': 'past7'
		},
		dataType: 'json',
		success: function(data) {
			saved_data['past7'] = data;

			// update chart labels
			chart.data.labels = saved_data['past7']['labels'];
			
			// update chart dataset
			update_data(saved_data['past7']['nutrients']);

			// show calorie goal
			show_goal(true);

			// update daily average
			update_average();

			// apply all changes
			chart.update();
		}
	});
});

// update chart data according to timerange
function timerange_change() {
	// update chart labels
	chart.data.labels = saved_data[timerange]['labels'];

	// update chart dataset
	update_data(saved_data[timerange]['nutrients']);

	// show calorie goal
	show_goal(nutrient == "calories");

	// update daily average
	update_average();

	// show/hide the x-axis title, only visible for month and year
	if (timerange == "month" || timerange == "year") {
		chart.options.scales.xAxes[0].scaleLabel.display = true;
		chart.options.scales.xAxes[0].scaleLabel.labelString = saved_data[timerange]['title'];
	} else {
		chart.options.scales.xAxes[0].scaleLabel.display = false;
	}

	// apply all changes
	chart.update();
}

// retrieves data and updates chart when timerange field changes
$("#timerange").change(function() {
	timerange = $(this).val();

	// if the data for this timerange hasn't been retrieved yet, ajax call
	if (saved_data[timerange] == null) {
		$.ajax({
			url: url,
			data: {
				'user': user,
				'timerange': timerange
			},
			dataType: 'json',
			success: function(data) {
				// assign to saved_data
				saved_data[timerange] = data;
				
				// update chart
				timerange_change();
			}
		});
	} else {
		// update chart
		timerange_change();
	}
});

// updates chart when nutrient field changes
$("#nutrient").change(function() {
	// update data to match nutrient
	update_data(saved_data[timerange]['nutrients'], nutrient);

	// show calorie goal if calories selected
	show_goal(nutrient == "calories");

	// change y-axis label according to nutrient
	update_yaxis_label();

	// update daily average
	update_average();

	// apply all changes
	chart.update();
});

// updates chart dataset
function update_data(nutrients) {
	var dataset = [];
	nutrient = $("#nutrient").val();
	
	// build dataset from specified nutrient value of each object in nutrients array
	for (var i = 0; i < nutrients.length; i++)
		dataset.push(nutrients[i][nutrient])
	
	// update chart
	chart.data.datasets[0].data = dataset;
}

// update the y-axis label depending on which nutrient is selected
function update_yaxis_label() {
	switch (nutrient) {
		case "calories":
			chart.options.scales.yAxes[0].scaleLabel.labelString = "Calories (kcal)";
			break;
		case "totalFat":
			chart.options.scales.yAxes[0].scaleLabel.labelString = "Total Fat (g)";
			break;
		case "cholesterol":
			chart.options.scales.yAxes[0].scaleLabel.labelString = "Cholesterol (mg)";
			break;
		case "sodium":
			chart.options.scales.yAxes[0].scaleLabel.labelString = "Sodium (mg)";
			break;
		case "totalCarb":
			chart.options.scales.yAxes[0].scaleLabel.labelString = "Total Carbohydrates (g)";
			break;
		case "protein":
			chart.options.scales.yAxes[0].scaleLabel.labelString = "Protein (g)";
			break;
	}
}

// create array of same values
function straight_line(timerange, value) {
	var len = saved_data[timerange]['labels'].length;
	var arr = new Array(len);

	for (var i = 0; i < len; i++)
		arr[i] = value;

	return arr;
}

// update the goal range
// function update_range(lower, upper) {
// 	timerange = $("#timerange").val();

// 	chart.data.datasets[1].data = straight_line(timerange, upper);
// 	chart.data.datasets[2].data = straight_line(timerange, lower);
// 	chart.update();
// }

// display the calorie goal
function show_goal(is_calories) {
	timerange = $("#timerange").val();

	if (goal && is_calories) {
		chart.data.datasets[2].data = straight_line(timerange, goal);
		chart.data.datasets[2].hidden = false;
	} else {
		chart.data.datasets[2].data = straight_line(timerange, 0);
		chart.data.datasets[2].hidden = true;
	}
}

function update_average() {
	var avg = saved_data[timerange]['average'][nutrient];

	if (avg) {
		chart.data.datasets[1].label = "Daily average: " + avg;
		chart.data.datasets[1].data = straight_line(timerange, avg);
	} else {
		chart.data.datasets[1].label = "Daily average: N/A";
	}
}

// opens log detail page of clicked point
$("#myChart").click(function(e) {
	var point = chart.getElementAtEvent(e);
	timerange = $("#timerange").val();
	
	// doesn't do anything if didn't click a point or if year graph
	if (!point.length || timerange == "year")
		return;
	
	var index = point[0]._index;
	var dl_id = saved_data[timerange]['ids'][index];
	
	window.open("/nutrihacker/log_detail/" + dl_id);
});