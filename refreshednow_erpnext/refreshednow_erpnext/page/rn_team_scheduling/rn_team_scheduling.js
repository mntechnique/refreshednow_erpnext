
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

	//Set default route.
	if (frappe.get_route().length == 1) {
		frappe.set_route("rn-team-scheduling", "weekly", frappe.datetime.obj_to_user(frappe.datetime.get_today()), "Refreshed Go");
	}


	//Add filter field and restrict to service items.
	page.add_field(
		{
			fieldtype: "Link",
			fieldname: "service_type",
			options: "Item",
			default: frappe.get_route()[3],
			label: __("Service Type"),
			reqd: 1,
			input_css: {"z-index": 1},
			change: function(event) {
				var selected = $(this).val();
				var items = [];	
				$.each(wrapper.page.service_item_data, function(k,v) {
					items.push(v["item_code"]);
				});

				if ((selected) || items.includes(selected)) {
					build_route(wrapper); //, frappe.get_route()[1] || "weekly");
				}
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
			default: frappe.datetime.user_to_obj(frappe.get_route()[2]),
			input_css: {"z-index": 1},
			change: function() {
				var selected = $(this).val();
				if (selected) {
					build_route(wrapper);//, frappe.get_route()[1] || "weekly");
				}
			},
		}
	);
	page.btn_daily_view = page.add_field(
		{
			fieldtype: "Button",
			fieldname: "daily_view",
			label: __("Daily View"),
			input_css: {"z-index": 1},
			click: function() {
				// page.main.find("#weekly").fadeOut('slow');
				// page.main.find("#daily").fadeIn('slow');
				localStorage.setItem("rn_scheduling_view", "daily");
				build_route(wrapper);//, frappe.get_route()[1] || "daily");
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
				// page.main.find("#weekly").fadeIn('slow');
				// page.main.find("#daily").fadeOut('slow');
				localStorage.setItem("rn_scheduling_view", "weekly");
				build_route(wrapper);//, frappe.get_route()[1] || "weekly");
			},
		}
	);

}

frappe.pages['rn-team-scheduling'].on_page_show = function(wrapper) {
	//render_weekly_calendar(wrapper);
	var route = frappe.get_route();

	var scheduled_date = route[2];
	var service_type = route[3];
	var scheduled_time = route[4] ? route[4] : null;

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
		minTime: minTime,
		maxTime: maxTime,
		eventStartEditable: false,
		eventDurationEditable: false,
		disableDragging: true,
		editable: false,
		//firstDay: frappe.datetime.str_to_obj(defaultDate).getDay(), 
		eventClick: function(calEvent, jsEvent, view) {
			
			wrapper.page.selected_event_info = {"calEvent": calEvent, "jsEvent": jsEvent, "view": view};
			wrapper.page.fields_dict['scheduled_date'].set_input(calEvent.start.toDate());

			localStorage.setItem("rn_scheduling_view", "daily");

			build_route(wrapper); //, frappe.get_route()[1] || "daily");
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
		snapDuration: "01:00:00", //Replace with service duration
		minTime: minTime,
		maxTime: maxTime,
		eventStartEditable: false,
		eventDurationEditable: false,
		defaultDate: defaultDate,
		disableDragging: true,
		editable: false,
		dayClick: function(date, jsEvent, view, resourceObj) {
			show_prompt(date, page_filters["service_type"], resourceObj.id);
		},
		eventClick: function(calEvent, jsEvent, view) {
			frappe.db.get_value("RN Scheduled Service", filters={"name": calEvent.id.toString()}, fieldname="name", callback=function(r) {
				if (!r) {
					show_prompt(calEvent.start, page_filters["service_type"], calEvent.resourceId);
				} else {
					frappe.set_route("Form", "RN Scheduled Service", r.name);
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

		//Prepare Date Filter
		if (scheduled_date) {
			//scheduled_date = frappe.datetime.user_to_obj(scheduled_date); One Day Prior in Python anomaly.
			scheduled_date = frappe.datetime.user_to_str(scheduled_date);
		} else {
			scheduled_date = frappe.datetime.get_today();
		}

		if(scheduled_time) {
			scheduled_time = moment(scheduled_time, "hhmm").format("hh:mm:ss");
		}

		var weekly_options = prepare_weekly_options(minTime, 
			maxTime, 
			scheduled_date, 
			{"service_type": service_type, "scheduled_date": scheduled_date},
			wrapper
		);

		var daily_options = prepare_daily_options(minTime, 
			maxTime, 
			scheduled_date, 
			{"service_type": service_type, "scheduled_date": scheduled_date, "scheduled_time": scheduled_time},
			wrapper
		);

		//Dispose previous instance.

		if (page.weekly_calendar) {
			page.weekly_calendar.$cal.fullCalendar('destroy');
			page.weekly_calendar = null;	
		}
		
		if (frappe.get_route().indexOf("weekly") != -1) {
			page.weekly_calendar = new refreshednow_erpnext.RNCalendar(weekly_options, page, "weekly");
		}
		
		//Dispose previous instance.
		if (page.daily_calendar) {
			page.daily_calendar.$cal.fullCalendar('destroy');
			page.daily_calendar = null;	
		}
		
		if (frappe.get_route().indexOf("daily") != -1) {
			page.daily_calendar = new refreshednow_erpnext.RNCalendar(daily_options, page, "daily");
		}
	
	});
}

function build_route(wrapper) { //, show_daily="daily") {
	var scheduled_date = wrapper.page.fields_dict['scheduled_date'].$input.val();
	var service_type = wrapper.page.fields_dict['service_type'].$input.val();

	if (wrapper.page.selected_event_info) {
		var timeslot = wrapper.page.selected_event_info.calEvent.start.format("HHmm");
	}

	var initial_route = frappe.get_route();

	if (localStorage.getItem("rn_scheduling_view") == "daily") {
		frappe.set_route("rn-team-scheduling", "daily", scheduled_date, service_type, timeslot);
	} else if (localStorage.getItem("rn_scheduling_view") == "weekly") {
		frappe.set_route("rn-team-scheduling", "weekly", scheduled_date, service_type, timeslot);
	}
	
	if (frappe.get_route() == initial_route) {
		frappe.set_route(frappe.get_route());
	};
	//frappe.set_re_route(frappe.get_route());
}

function on_day_click(date, service_type, team, customer) {
	var rnss = frappe.model.make_new_doc_and_get_name('RN Scheduled Service');
	rnss = locals["RN Scheduled Service"][rnss];
	rnss.service_type = service_type;
	rnss.scheduled_date = frappe.datetime.obj_to_str(date);
	rnss.scheduled_time = date.format("HH:mm:ss");
	rnss.team = team;
	rnss.customer = customer;
	rnss.starts_on = date.format("Y-M-D HH:mm:ss");
	rnss.ends_on = date.add(1,'h').format("Y-M-D HH:mm:ss"); //Replace with service duration.
	
	frappe.set_route("Form", "RN Scheduled Service", rnss.name);
}

function render_daily_event_row(r, wrapper, page_filters) {

	var events = r.message || [];
				
	var service_item = wrapper.page.service_item_data.filter(function(item) { return item.item_code == page_filters['service_type']})[0];
	var teams = service_item.teams;

	if (wrapper.page.selected_event_info) {
		var selected_start_time = wrapper.page.selected_event_info.calEvent.start.toISOString();
		var selected_end_time =  wrapper.page.selected_event_info.calEvent.end.toISOString();

		console.log(events);
		
		//Find an Event under the Resource column which starts at 'selected_start_time'
		//If such an event is not found, render. 
		$.each(teams, function(i, v) {
			//Find event for resource v["name"]
			var event_in_slot_under_resource = events.filter(function(event) {
				return (event["resourceId"] == v["name"]) && (event["start"] == selected_start_time)
			});
			
			console.log("event under resource:", event_in_slot_under_resource);

			if (event_in_slot_under_resource.length == 0) {
				events.push({
					"id": i,
					"resourceId":v["name"],
					"start": selected_start_time,
					"end": selected_end_time,
					"color":"grey"
				});
			}
		});
	}

	return events;
}


function show_prompt(date, service_type, resource_id) {
	frappe.prompt([
		{'fieldname': 'customer', 'fieldtype': 'Link', 'options':'Customer','label':'Customer', 'default': localStorage.getItem("customer_name") || ""}
	],
	function(values){
		if (values) {
			on_day_click(date, service_type, resource_id, values.customer);
		}
	},
	'Select Customer',
	'Select'
	)
}