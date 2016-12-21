
frappe.provide("refreshednow_erpnext.rn_calendar");

frappe.pages['rn-weekly-resource'].on_page_load = function(wrapper) {	
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Weekly Availability of Cleaners',
		single_column: true
	});

	frappe.require(["assets/refreshednow_erpnext/js/lib/fullcalendar.min.js", 
		"assets/refreshednow_erpnext/js/lib/fullcalendar.min.css"], 
		function() {
			var options = prepare_options(); 
			var cal = new refreshednow_erpnext.RNCalendar(options, page) //, "refreshednow_erpnext.api.get_cleaner_availability");
			console.log(cal);
			cal.filters = [
							{
								"fieldtype": "Link",
								"fieldname": "service_type",
								"options": "Item",
								"label": __("Service Type")
							},
							{
								"fieldtype": "Date",
								"fieldname": "scheduled_date",
								"label": __("Date")
							},
							{
								"fieldtype": "Link",
								"fieldname": "customer",
								"options": "Customer",
								"label": __("Customer")
							},
						];
			cal.get_events_method = "refreshednow_erpnext.api.rn_events";
			cal.add_filters();
			cal.set_filters_from_route_options();
			$(this.parent).on("show", function() {
				me.$cal.fullCalendar("refetchEvents");
			});
			page.fields_dict["service_type"].get_query = function() {
				return {
					"filters": {
						"item_group": "Services"
					}
				}
			}


			// frappe.call({
			// 	args: {
			// 		date: "2016-12-07"
			// 	},
			// 	method: "refreshednow_erpnext.api.get_cleaner_availability",
			// 	callback: function(r) {

			// 		console.log(r);

			// 		var resources = r.message;
			// 		//var options = prepare_options(resources);

			// 		cal = new refreshednow_erpnext.RNCalendar(options, page, "refreshednow_erpnext.api.get_cleaner_availability");
			// 		cal.filters = [
			// 						{
			// 							"fieldtype": "Link",
			// 							"fieldname": "service_type",
			// 							"options": "Item",
			// 							"label": __("Service Type")
			// 						},
			// 						{
			// 							"fieldtype": "Date",
			// 							"fieldname": "scheduled_date",
			// 							"label": __("Date")
			// 						},
			// 						{
			// 							"fieldtype": "Link",
			// 							"fieldname": "customer",
			// 							"options": "Customer",
			// 							"label": __("Customer")
			// 						},
			// 					];
			// 		//cal.get_events_method = "refreshednow_erpnext.api.get_timeslots";
			// 		cal.add_filters();
			// 		cal.set_filters_from_route_options();
			// 		$(this.parent).on("show", function() {
			// 			me.$cal.fullCalendar("refetchEvents");
			// 		});
			// 		page.fields_dict["service_type"].get_query = function() {
			// 			return {
			// 				"filters": {
			// 					"item_group": "Services"
			// 				}
			// 			}
			// 		}
			// 	}
			// });
		});
	}


function prepare_options() {
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
		defaultView: "agendaWeek",
		selectAllow: function(selectInfo) {
			console.log(selectInfo);
		},
		// minTime: "10:00:00",
		// maxTime: "16:00:00",
		eventStartEditable: true,
		eventDurationEditable: true,
		eventClick: function(calEvent, jsEvent, view) {

			// alert('Event: ' + calEvent.title);
			// alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
			// alert('View: ' + view.name);

			// // change the border color just for fun
			// $(this).css('border-color', 'green');
			frappe.set_route("rn-daily-allocation");

		}
	}
}





// frappe.pages['rn-weekly-resource'].on_page_load = function(wrapper) {

// 	frappe.require(["assets/frappe/js/lib/fullcalendar/fullcalendar.min.js", "assets/frappe/js/lib/fullcalendar/fullcalendar.min.css"], 
// 			function() { console.log("require")});

// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Available Cleaners by Week',
// 		single_column: true
// 	});

// 	var content = null;

// 	frappe.call({
// 		method: "refreshednow_erpnext.api.get_available_cleaners",
// 		callback: function(r) {
// 			console.log(r);

// 			content = page.wrapper.find(".page-content");
// 			content.append(frappe.render_template("available_cleaners", {"available_cleaners": r.message}))
			
// 			wireup_fullcalendar(content);
// 		}
// 	});
// }

// function wireup_fullcalendar(content) {
// 	var calendarhost = content.find('#calendarhost');

// 	var calendar_options = {
// 		header: {
// 			left: 'prev,next today',
// 			center: 'title',
// 			right: 'month,agendaWeek,agendaDay'
// 		},
// 		//editable: true,
// 		//selectable: true,
// 		selectHelper: true,
// 		forceEventDuration: true,
// 		defaultView: "agendaWeek",
// 		minTime: "10:00:00",
// 		maxTime: "16:00:00",
// 		eventStartEditable: true,
// 		eventDurationEditable: true,
// 		schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
// 		eventClick: function(calEvent, jsEvent, view) {

// 			alert('Event: ' + calEvent.title);
// 			alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
// 			alert('View: ' + view.name);

// 			// change the border color just for fun
// 			$(this).css('border-color', 'green');

// 		}
// 	}

// 	console.log(calendarhost);
// 	calendarhost.fullCalendar(calendar_options);

// }