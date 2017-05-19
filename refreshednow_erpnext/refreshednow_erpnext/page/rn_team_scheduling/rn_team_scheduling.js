
frappe.pages['rn-team-scheduling'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Team Scheduling',
		single_column: true
	});

	//Load service items and timings for setting time slots
	page.service_item_data = [];
	frappe.call({
		async:false,
		method: "refreshednow_erpnext.api.get_service_item_data",
		callback: function(r) {
			page.service_item_data = r.message;
		}
	});


	// //Set default route.
	// if (frappe.get_route().length == 1) {
	// 	frappe.set_route("rn-team-scheduling", "weekly", frappe.datetime.obj_to_user(frappe.datetime.get_today()), "Refreshed Go");
	// }

	//Add filter field and restrict to service items.
	page.add_field(
		{
			fieldtype: "Link",
			fieldname: "service_type",
			options: "Item",
			label: __("Service Type"),
			input_css: {"z-index": 1},
			change: function(event) {
				var selected = $(this).val();
				var items = [];
				$.each(wrapper.page.service_item_data, function(k,v) {
					items.push(v["item_code"]);
				});

				//if ((selected) || items.includes(selected)) {
				build_route(wrapper, frappe.get_route()[1] || "weekly");
				//}
			},
		}
	)
	page.fields_dict["service_type"].get_query = function() {
		return {
			"filters": {
				"item_group": "Services"
			}
		}
	}
	//Add filter field and restrict to service items.
	page.add_field(
		{
			fieldtype: "Date",
			fieldname: "scheduled_date",
			options: "Item",
			label: __("Scheduled Date"),
			input_css: {"z-index": 1},
			change: function() {
				var selected = $(this).val();
				if (selected) {
					build_route(wrapper, frappe.get_route()[1] || "weekly");
				}
			},
		}
	);
	page.btn_weekly_view = page.add_field(
		{
			fieldtype: "Button",
			fieldname: "weekly_view",
			label: __("Weekly View"),
			input_css: {"z-index": 1},
			click: function() {
				//localStorage.setItem("rn_scheduling_view", "weekly");
				build_route(wrapper, "weekly");//, frappe.get_route()[1] || "weekly");
			},
		}
	);

	//Set default scheduled_date
	if ([undefined, ""].indexOf(page.fields_dict["scheduled_date"].$input.val()) != -1) {
		page.fields_dict["scheduled_date"].$input.val(frappe.datetime.str_to_user(frappe.datetime.get_today()));
	}
}

frappe.pages['rn-team-scheduling'].on_page_show = function(wrapper) {
	var route = frappe.get_route();

	var scheduled_date = route[2];
	var service_type = route[3];
	var scheduled_time = route[4];

	render_calendars(wrapper, service_type, scheduled_date, scheduled_time);
}

function prepare_weekly_options(minTime="07:00:00", maxTime="17:00:00", defaultDate, page_filters, wrapper) {
	return	{
		header:{
			left: null,
			center: 'title',
			right: null
		},
		schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
		allDaySlot: false,
		selectHelper: true,
		forceEventDuration: false,
		defaultView: "agendaWeek",
		minTime: minTime||"07:00:00",
		maxTime: maxTime||"17:00:00",
		eventStartEditable: false,
		eventDurationEditable: false,
		disableDragging: true,
		editable: false,
		columnFormat: "ddd D/M",
		eventClick: function(calEvent, jsEvent, view) {

			wrapper.page.selected_event_info = {"calEvent": calEvent, "jsEvent": jsEvent, "view": view};
			wrapper.page.fields_dict['scheduled_date'].set_input(calEvent.start.toDate());

			if (calEvent.title == "Break") {
				frappe.msgprint("Cannot schedule a service during break time.");
			} else if (calEvent.title == "-") {
				frappe.msgprint("No teams available for this slot.");
			} else {
				localStorage.setItem("rn_scheduling_view", "daily");
				build_route(wrapper, "daily");
			}
		},
		defaultDate: defaultDate,
		/* Fetch events via a callback function*/
		events: function(start, end, timezone, callback) {
			return frappe.call({
				method: "refreshednow_erpnext.api.rn_events",
				type: "GET",
				args: {"start": minTime, "end": maxTime, "filters": page_filters},
				callback: function(r) {
					var events = r.message || [];
					callback(events);
				}
			})
		},
		displayEventTime: false
	}
}

function prepare_daily_options(minTime="07:00:00", maxTime="17:00:00", defaultDate, page_filters, wrapper) {
	return	{
		header:{
			left: null,
			center: 'title',
			right: null
		},
		schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
		allDaySlot: false,
		selectHelper: false,
		forceEventDuration: true,
		defaultView: "agendaDay",
		minTime: minTime||"07:00:00",
		maxTime: maxTime||"17:00:00",
		eventStartEditable: false,
		eventDurationEditable: false,
		defaultDate: defaultDate,
		disableDragging: true,
		editable: false,
		dayClick: function(date, jsEvent, view, resourceObj) {
			on_day_click(date, page_filters["service_type"], resourceObj.id, wrapper);
		},
		eventClick: function(calEvent, jsEvent, view) {
			frappe.call({
				method: "refreshednow_erpnext.api.get_availability_for_team_dow",
				args: {
					"team": calEvent.resourceId,
					"day_of_week": calEvent.start.format("dddd")
				},
				callback: function(r) {
					if (r.message && r.message.exc) {
						frappe.msgprint(r.message.exc)
					} else {
						on_event_click(calEvent, page_filters, wrapper);
					}
				}
			});
		},
		events: function(start, end, timezone, callback) {
			return frappe.call({
				method: "refreshednow_erpnext.api.get_rn_daily_events",
				type: "GET",
				args: {"start": minTime, "end": maxTime, "filters": page_filters},
				callback: function(r) {
					var events = render_daily_event_row(r, wrapper, page_filters);
					callback(events);
				}
			});
		},
		resources: function(callback) {
			return frappe.call({
				method: "refreshednow_erpnext.api.get_rn_daily_resources",
				args: { "filters": page_filters },
				type: "GET",
				callback: function(r) {
					var resources = r.message || [];
					callback(resources);
				}
			})
		},
	}
}

function render_calendars(wrapper, service_type, scheduled_date, scheduled_time=null) {
	frappe.require(["assets/refreshednow_erpnext/js/lib/fullcalendar.min.js",
	"assets/refreshednow_erpnext/js/lib/fullcalendar.min.css",
	"assets/refreshednow_erpnext/js/lib/scheduler.min.js",
	"assets/refreshednow_erpnext/js/lib/scheduler.min.css"],

	function() {
		var page = wrapper.page;
		var minTime = ""; var maxTime = "";

		$.each(page.service_item_data, function (k,v) {
			if (v["item_code"] == service_type) {
				minTime = v["start_time"];
				maxTime = v["end_time"];
			}
		});

		//Dispose previous instances.
		if (page.weekly_calendar) {
			page.weekly_calendar.$cal.fullCalendar('destroy');
			page.weekly_calendar = null;
		}
		if (page.daily_calendar) {
			page.daily_calendar.$cal.fullCalendar('destroy');
			page.daily_calendar = null;
		}
		page.wrapper.find(".alert-danger").remove();

		if (service_type && scheduled_date && scheduled_time) {
			//Daily
			scheduled_date = frappe.datetime.user_to_str(scheduled_date);
			//scheduled_time = moment(scheduled_time, "hhmm").format("hh:mm:ss");
			scheduled_time = moment(scheduled_time, "hhmm").format("H:mm:ss");

			var daily_options = prepare_daily_options(minTime,
				maxTime,
				scheduled_date,
				{"service_type": service_type, "scheduled_date": scheduled_date, "scheduled_time": scheduled_time},
				wrapper
			);
			if (frappe.get_route().indexOf("daily") != -1) {
				page.daily_calendar = new refreshednow_erpnext.RNCalendar(daily_options, page, "daily");
			}
		} else if (service_type && scheduled_date) {
			//Weekly
			scheduled_date = frappe.datetime.user_to_str(scheduled_date);
			var weekly_options = prepare_weekly_options(minTime,
				maxTime,
				scheduled_date,
				{"service_type": service_type, "scheduled_date": scheduled_date},
				wrapper
			);
			if (frappe.get_route().indexOf("weekly") != -1) {
				page.weekly_calendar = new refreshednow_erpnext.RNCalendar(weekly_options, page, "weekly");
			}
		} else {
			page.main.after('<div class="alert alert-danger" role="alert">Please select both Service Type and Scheduled Date.</div>');
		}
	});
}

// function render_calendars(wrapper, service_type, scheduled_date, scheduled_time=null) {
// 	frappe.require(["assets/refreshednow_erpnext/js/lib/fullcalendar.min.js",
// 	"assets/refreshednow_erpnext/js/lib/fullcalendar.min.css",
// 	"assets/refreshednow_erpnext/js/lib/scheduler.min.js",
// 	"assets/refreshednow_erpnext/js/lib/scheduler.min.css"],

// 	function() {
// 		var page = wrapper.page;

// 		if (service_type) && ((scheduled_date) || (scheduled_time)) {
// 			var minTime = ""; var maxTime = "";

// 			$.each(page.service_item_data, function (k,v) {
// 				if (v["item_code"] == service_type) {
// 					minTime = v["start_time"];
// 					maxTime = v["end_time"];
// 				}
// 			});

// 			//Prepare Date Filter
// 			if (scheduled_date) {
// 				//scheduled_date = frappe.datetime.user_to_obj(scheduled_date); One Day Prior in Python anomaly.
// 				scheduled_date = frappe.datetime.user_to_str(scheduled_date);
// 			}

// 			if(scheduled_time) {
// 				scheduled_time = moment(scheduled_time, "hhmm").format("hh:mm:ss");
// 			}

// 			var weekly_options = prepare_weekly_options(minTime,
// 				maxTime,
// 				scheduled_date,
// 				{"service_type": service_type, "scheduled_date": scheduled_date},
// 				wrapper
// 			);

// 			var daily_options = prepare_daily_options(minTime,
// 				maxTime,
// 				scheduled_date,
// 				{"service_type": service_type, "scheduled_date": scheduled_date, "scheduled_time": scheduled_time},
// 				wrapper
// 			);

// 			//Dispose previous instance.

// 			if (page.weekly_calendar) {
// 				page.weekly_calendar.$cal.fullCalendar('destroy');
// 				page.weekly_calendar = null;
// 			}

// 			if (frappe.get_route().indexOf("weekly") != -1) {
// 				page.weekly_calendar = new refreshednow_erpnext.RNCalendar(weekly_options, page, "weekly");
// 			}

// 			//Dispose previous instance.
// 			if (page.daily_calendar) {
// 				page.daily_calendar.$cal.fullCalendar('destroy');
// 				page.daily_calendar = null;
// 			}

// 			if (frappe.get_route().indexOf("daily") != -1) {
// 				page.daily_calendar = new refreshednow_erpnext.RNCalendar(daily_options, page, "daily");
// 			}
// 		} else {
// 			//Please select.
// 		}
// 	});
// }

function build_route(wrapper, rn_view) { //, show_daily="daily") {
	var scheduled_date = wrapper.page.fields_dict['scheduled_date'].$input.val();
	var service_type = wrapper.page.fields_dict['service_type'].$input.val();

	if (wrapper.page.selected_event_info) {
		var timeslot = wrapper.page.selected_event_info.calEvent.start.format("HHmm");
	}

	var initial_route = frappe.get_route();

	if (rn_view == "daily") {
		frappe.set_route("rn-team-scheduling", "daily", scheduled_date, service_type, timeslot);
	} else if (rn_view == "weekly") {
		frappe.set_route("rn-team-scheduling", "weekly", scheduled_date, service_type);
	}

	//Force page refresh
	if (frappe.get_route() == initial_route) {
		frappe.set_route(frappe.get_route());
	};
}


function on_day_click(date, service_type, team, wrapper) {
	console.log("ONDAYCLICK Date", date);

	var service_item = wrapper.page.service_item_data.filter(function(item) { return item.item_code == service_type})[0]
    
	var rnss = frappe.model.make_new_doc_and_get_name('RN Scheduled Service');
	rnss = locals["RN Scheduled Service"][rnss];
	rnss.naming_series = "REF-.#####";
	rnss.service_type = service_type;
	rnss.scheduled_date = frappe.datetime.obj_to_str(date);
	rnss.scheduled_time = date.format("HH:mm:ss");
	rnss.team = team;
	
	rnss.starts_on = date.format("Y-MM-DD HH:mm:ss");
	rnss.reporting_time = date.format("Y-MM-DD HH:mm:ss");
	rnss.ends_on = date.add(service_item.service_duration,'m').format("Y-MM-DD HH:mm:ss"); //Replace with service duration.
	frappe.set_route("Form", "RN Scheduled Service", rnss.name);
}

function on_event_click(calEvent, page_filters, wrapper) {
	frappe.db.get_value("RN Scheduled Service", filters={"name": calEvent.id.toString()}, fieldname="name", callback=function(r) {
		if (!r) {
			on_day_click(calEvent.start, page_filters["service_type"], calEvent.resourceId, wrapper);
		} else {
			frappe.set_route("Form", "RN Scheduled Service", r.name);
		}
	});
}

function render_daily_event_row(r, wrapper, page_filters) {

	var events = r.message || [];

	var service_item = wrapper.page.service_item_data.filter(function(item) { return item.item_code == page_filters['service_type']})[0];
	var teams = service_item.teams;

	if (wrapper.page.selected_event_info) {
		var selected_start_time = wrapper.page.selected_event_info.calEvent.start.toISOString();
		var selected_end_time =  wrapper.page.selected_event_info.calEvent.end.toISOString();

		//Find an Event under the Resource column which starts at 'selected_start_time'
		//If such an event is not found, render.
		$.each(teams, function(i, v) {
			//Find event for resource v["name"]
			var event_in_slot_under_resource = events.filter(function(event) {
				return (event["resourceId"] == v["name"]) && (event["start"] == selected_start_time)
			});


			if (event_in_slot_under_resource.length == 0) {
				events.push({
					"id": i,
					"resourceId":v["name"],
					"start": selected_start_time,
					"end": selected_end_time,
					"className": "rn-team",
					"color":"grey"
				});
			}
		});
	}

	return events;
}


// function show_service_form(date, service_type, resource_id) {
// 	// frappe.prompt([
// 	// 	{'fieldname': 'customer', 'fieldtype': 'Link', 'options':'Customer','label':'Customer', 'default': localStorage.getItem("customer_name") || ""}
// 	// ],
// 	// function(values){
// 	// 	if (values) {
// 	// 		on_day_click(date, service_type, resource_id, values.customer);
// 	// 		on_day_click(date, service_type, resource_id, values.customer);
// 	// 	}
// 	// },
// 	// 'Select Customer',
// 	// 'Select'
// 	// )
// }