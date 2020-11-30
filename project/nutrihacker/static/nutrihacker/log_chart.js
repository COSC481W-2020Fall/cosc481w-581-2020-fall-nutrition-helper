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
			backgroundColor: '#008000',
			borderColor: '#008000',
			pointBorderWidth: 0,
			pointRadius: 4,
			pointHoverRadius: 5,
			fill: false,
			lineTension: 0,
			data: null
		}] 
	},
	options: {
		responsive: true,
		legend: {
			display: false
			},
			layout: {
            padding: {
                left: 30,
                right: 50,
                top: 40,
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
			chart.update();

			// update chart dataset
			update_data(saved_data['past7']['nutrients']);
		}
	});
});

// retrieves data and updates chart when timerange field changes
$("#timerange").change(function() {
	var timerange = $(this).val();

	$.ajax({
		url: url,
		data: {
			'user': user,
			'timerange': timerange
		},
		dataType: 'json',
		success: function(data) {
			// assign to saved_data if timerange hasn't been retrieved before
			if (saved_data[timerange] == null)
				saved_data[timerange] = data;
			
			// get the saved_data of timerange
			var chart_data = saved_data[timerange];
			
			// update chart labels
			chart.data.labels = chart_data['labels'];
			chart.update();

			// update chart dataset
			update_data(chart_data['nutrients']);

			if (timerange == "month" || timerange == "year") {
				chart.options.scales.xAxes[0].scaleLabel.display = true;
				chart.options.scales.xAxes[0].scaleLabel.labelString = chart_data['title'];
				chart.update();
			} else {
				chart.options.scales.xAxes[0].scaleLabel.display = false;
				chart.update();
			}
		}
	});

});

// updates chart when nutrient field changes
$("#nutrient").change(function() {
	var timerange = $("#timerange").val();
	update_data(saved_data[timerange]['nutrients'], nutrient);
	update_yaxis_label();
});

// updates chart dataset
function update_data(nutrients) {
	var dataset = [];
	var nutrient = $("#nutrient").val();
	
	// build dataset from specified nutrient value of each object in nutrients array
	for (var i = 0; i < nutrients.length; i++)
		dataset.push(nutrients[i][nutrient])
	
	// update chart
	chart.data.datasets[0].data = dataset;
	chart.update();
}

function update_yaxis_label() {
	var nutrient = $("#nutrient").val();
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

// opens log detail page of clicked point
$("#myChart").click(function(e) {
	var point = chart.getElementAtEvent(e);
	var timerange = $("#timerange").val();
	
	// doesn't do anything if didn't click a point or if year graph
	if (!point.length || timerange == "year")
		return;
	
	var index = point[0]._index;
	var dl_id = saved_data[timerange]['ids'][index];
	
	window.open("/nutrihacker/log_detail/" + dl_id);
});