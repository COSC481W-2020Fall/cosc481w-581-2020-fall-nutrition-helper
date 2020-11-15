var extra_food_count = Number(document.getElementById("id_extra_food_count").value);
var extra_recipe_count = Number(document.getElementById("id_extra_recipe_count").value);

var food_number = extra_food_count + 2;
var recipe_number = extra_recipe_count + 2;
var row_number = 2 * (food_number + recipe_number) - 1;

// assign event listener to initial remove buttons
var r_btns = document.getElementsByClassName("rmvbtn");
for (var i = 0; i < r_btns.length; i++)
	r_btns[i].addEventListener("click", function(){ remove(this.id); });

// assign event listener to add buttons
document.getElementById("add_food").addEventListener("click", function(){ add_fields("food"); });
document.getElementById("add_recipe").addEventListener("click", function(){ add_fields("recipe"); });

// adds another food and portions field to the form
function add_fields(item_type) {
	// hide error
	var error_row = document.getElementById("error");
	if (error_row)
		error_row.style.display = "none";

	// determine if food or recipe
	var food;
	if (item_type === "food")
		food = true;
	else
		food = false;
	
	var item_number;
	if (food)
		item_number = food_number;
	else
		item_number = recipe_number;
	
	create_rows(item_type, item_number, row_number);

	// increment counters and update hidden value
	row_number += 2;

	if (food) {
		food_number++;
		extra_food_count++;
		document.getElementById("id_extra_food_count").value = extra_food_count;
	} else {
		recipe_number++;
		extra_recipe_count++;
		document.getElementById("id_extra_recipe_count").value = extra_recipe_count;
	}
}

// removes indicated food and portions field from form
function remove(clicked_id) {
	// get rows
	var s_row = document.getElementById("row" + clicked_id);
	var i_row = document.getElementById("row" + (Number(clicked_id) + 1));

	// get select and input elements
	var s_select = s_row.getElementsByTagName("select")[0];
	var i_input = i_row.getElementsByTagName("input")[0];

	// disable them
	s_select.disabled = true;
	i_input.disabled = true;
	
	// hide them
	s_row.style.display = "none";
	i_row.style.display = "none";
}

function create_rows(item_type, item_number, row_number) {
	// create elements
	var s_row = document.createElement("tr");
	var i_row = document.createElement("tr");
	var s_th = document.createElement("th");
	var i_th = document.createElement("th");
	var s_label = document.createElement("label");
	var i_label = document.createElement("label");
	var s_td1 = document.createElement("td");
	var s_td2 = document.createElement("td");
	var i_td = document.createElement("td");
	var s_select = document.createElement("select");
	var s_button = document.createElement("button");
	var i_input = document.createElement("input");

	// set element attributes
	s_row.id = "row" + row_number;
	s_th.className = "formlabel";
	s_label.setAttribute("for", "id_" + item_type + item_number);
	s_label.innerHTML = "Choose a " + item_type + ":";
	s_select.setAttribute("name", item_type + item_number);
	s_select.required = true;
	s_select.id = "id_" + item_type + item_number;
	s_select.setAttribute("data-autocomplete-light-language", "en");
	s_select.setAttribute("data-autocomplete-light-url", "/nutrihacker/" + item_type + "_autocomplete/");
	s_select.setAttribute("data-autocomplete-light-function", "select2");
	s_select.setAttribute("data-select2-id", "id_" + item_type + item_number);
	s_select.setAttribute("tabindex", "-1");
	s_select.className = "select2-hidden-accessible";
	s_select.setAttribute("aria-hidden", "true");
	s_select.value = "";
	s_button.innerHTML = "−";
	s_button.id = row_number;
	s_button.className = "rmvbtn";
	s_button.type = "button";
	
	i_row.id = "row" + (row_number + 1);
	i_th.className = "formlabel";
	i_label.setAttribute("for", "id_" + item_type + "_portions" + item_number);
	i_label.innerHTML = "Portions:";
	i_input.type = "number";
	i_input.setAttribute("name", item_type + "_portions" + item_number);
	i_input.value = "1";
	i_input.setAttribute("min", "0");
	i_input.setAttribute("max", "99");
	i_input.setAttribute("step", "any");
	i_input.style.width = "48px";
	i_input.required = true;
	i_input.id = "id_" + item_type + "_portions" + item_number;
	
	// add event listener to remove button
	s_button.addEventListener("click", function(){ remove(this.id); });

	// append elements to rows
	s_th.appendChild(s_label);
	s_td1.appendChild(s_select);
	s_td2.appendChild(s_button);
	s_row.appendChild(s_th);
	s_row.appendChild(s_td1);
	s_row.appendChild(s_td2);

	i_th.appendChild(i_label);
	i_td.appendChild(i_input);
	i_row.appendChild(i_th);
	i_row.appendChild(i_td);

	// get the first hidden row
	var h_row = document.getElementById("id_extra_food_count").parentElement.parentElement;
	// get the tbody
	var tbody = h_row.parentElement;

	// append rows to the table
	tbody.insertBefore(s_row, h_row);
	tbody.insertBefore(i_row, h_row);
}