
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
		method: "refreshednow_erpnext.api.get_service_item_timings",
		callback: function(r) {
			page.service_item_data = r.message;
		}
	});

	//Add filter field and restrict to service items.
	page.add_field(
		{
			fieldtype: "Link",
			fieldname: "service_type",
			options: "Item",
			default: frappe.get_route()[2] || "RN-PLUS",
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
					build_route(wrapper, true);
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
			default: frappe.datetime.user_to_obj(frappe.get_route()[1]) || frappe.datetime.get_today(),
			input_css: {"z-index": 1},
			change: function() {
				var selected = $(this).val();
				if (selected) {
					build_route(wrapper, false);
				}
			},
		}
	);
}

frappe.pages['rn-team-scheduling'].on_page_show = function(wrapper) {
	//render_weekly_calendar(wrapper);
	var route = frappe.get_route();

	var scheduled_date = route[1];
	var service_type = route[2];

	render_calendars(wrapper, service_type, scheduled_date);
}

function prepare_weekly_options(minTime="07:00:00", maxTime="17:00:00", defaultDate, filters, wrapper) {
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
		eventClick: function(calEvent, jsEvent, view) {
			wrapper.page.fields_dict['scheduled_date'].set_input(calEvent.start.toDate());
			build_route(wrapper, true);
		}, 
		defaultDate: defaultDate,
		/* Fetch events via a callback function*/
		events: function(start, end, timezone, callback) {
			return frappe.call({
				method: "refreshednow_erpnext.api.rn_events",
				type: "GET",
				args: {"start": minTime, "end": maxTime, "filters": filters},
				callback: function(r) {
					var events = r.message || [];
					callback(events);
				}
			})
		},
		displayEventTime: false
	}
}

function prepare_daily_options(minTime="07:00:00", maxTime="17:00:00", defaultDate, filters, wrapper) {
	return	{
		header:{
			left: null,
			center: 'title',
			right: null
		},
		schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
		allDaySlot: false,
		selectHelper: true,
		forceEventDuration: true,
		defaultView: "agendaDay",
		snapDuration: "01:00:00",
		minTime: minTime,
		maxTime: maxTime,
		eventStartEditable: true,
		eventDurationEditable: true,
		defaultDate: defaultDate,
		selectAllow: function(selectInfo) {
			console.log(selectInfo);
		},
		eventClick: function(calEvent, jsEvent, view) {

			alert('Event: ' + calEvent.title);
			alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
			alert('View: ' + view.name);

			// change the border color just for fun
			$(this).css('border-color', 'green');
		},
		events: function(start, end, timezone, callback) {
			return frappe.call({
				method: "refreshednow_erpnext.api.get_rn_daily_events",
				type: "GET",
				args: {"start": minTime, "end": maxTime, "filters": filters},
				callback: function(r) {
					var events = r.message || [];
					callback(events);
				}
			})
		},
		resources: function(callback) {
			return frappe.call({
				method: "refreshednow_erpnext.api.get_rn_daily_resources",
				args: { "filters": filters },
				type: "GET",
				callback: function(r) {
					var resources = r.message || [];
					callback(resources);
				}
			})
		},
	}
}

// function render_weekly_calendar(wrapper, service_type, scheduled_date) {
// 	var page = wrapper.page;
// 	frappe.require(["assets/refreshednow_erpnext/js/lib/fullcalendar.min.js", 
// 	"assets/refreshednow_erpnext/js/lib/fullcalendar.min.css"], 
	
// 	function() {
// 		var minTime = ""; var maxTime = "";

// 		$.each(page.service_item_data, function (k,v) { 
// 			if (v["item_code"] == service_type) {
// 				minTime = v["start_time"];
// 				maxTime = v["end_time"];
// 			}
// 		});

// 		//Prepare Date Filter
// 		if (scheduled_date) {
// 			scheduled_date = frappe.datetime.user_to_obj(scheduled_date);
// 		} else {
// 			scheduled_date = frappe.datetime.get_today();
// 		}

// 		var options = prepare_weekly_options(minTime, 
// 			maxTime, 
// 			scheduled_date, 
// 			{"service_type": service_type, "scheduled_date": scheduled_date},
// 			wrapper
// 		);
		
// 		//Dispose previous instance.
// 		if (page.weekly_calendar) {
// 			page.weekly_calendar.$cal.fullCalendar('destroy');
// 			page.weekly_calendar = null;	
// 		}
// 		page.weekly_calendar = new refreshednow_erpnext.RNCalendar(options, page);
// 	});
// }

function render_calendars(wrapper, service_type, scheduled_date) {
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

		var weekly_options = prepare_weekly_options(minTime, 
			maxTime, 
			scheduled_date, 
			{"service_type": service_type, "scheduled_date": scheduled_date},
			wrapper
		);

		var daily_options = prepare_daily_options(minTime, 
			maxTime, 
			scheduled_date, 
			{"service_type": service_type, "scheduled_date": scheduled_date},
			wrapper
		);

		//Dispose previous instance.
		if (page.weekly_calendar) {
			page.weekly_calendar.$cal.fullCalendar('destroy');
			page.weekly_calendar = null;	
		}
		page.weekly_calendar = new refreshednow_erpnext.RNCalendar(weekly_options, page);
		
		//Dispose previous instance.
		if (page.daily_calendar) {
			page.daily_calendar.$cal.fullCalendar('destroy');
			page.daily_calendar = null;	
		}
		
		page.daily_calendar = new refreshednow_erpnext.RNCalendar(daily_options, wrapper.page);	
	});
}

function build_route(wrapper, show_daily=false) {
	var scheduled_date = wrapper.page.fields_dict['scheduled_date'].$input.val();
	var service_type = wrapper.page.fields_dict['service_type'].$input.val();

	frappe.set_route("rn-team-scheduling", scheduled_date, service_type);
}