
frappe.provide("refreshednow_erpnext.rn_calendar");

frappe.pages['rn-weekly-resource'].on_page_load = function(wrapper) {	
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Weekly Availability of Cleaners',
		single_column: true
	});

	wrapper.service_item_data = [];

	frappe.call({
		async:false,
		method: "refreshednow_erpnext.api.get_service_item_timings",
		callback: function(r) {
			wrapper.service_item_data = r.message;
		}
	})

	//Add filter field and restrict to service items.
	page.add_field(
		{
			fieldtype: "Link",
			fieldname: "service_type",
			options: "Item",
			label: __("Service Type"),
			//default: "RN-PLUS",
			reqd: 1,
			input_css: {"z-index": 1},
			change: function() {
				var selected = $(this).val();
				console.log(selected);
				render_calendar(wrapper);
			}
		}
	)
	page.fields_dict["service_type"].get_query = function() {
		return {
			"filters": {
				"item_group": "Services"
			}
		}
	}

	//Add filter field date
	page.add_field(
		{
			fieldtype: "Date",
			fieldname: "scheduled_date",
			options: "Item",
			label: __("Scheduled Date"),
			default: frappe.datetime.get_today(),
			input_css: {"z-index": 1},
			change: function() {
				var selected = $(this).val();
				console.log(selected);
				render_calendar(wrapper);
			}
		}
	)

	if (page.fields_dict["service_type"].$input.val() && page.fields_dict["scheduled_date"].$input.val()) {;
		render_calendar(wrapper);
	}
}

function render_calendar(wrapper) {
	frappe.require(["assets/refreshednow_erpnext/js/lib/fullcalendar.min.js", 
		"assets/refreshednow_erpnext/js/lib/fullcalendar.min.css"], 

		function() {

			//Prepare Service Item filter.			
			var service_item_name = wrapper.page.fields_dict["service_type"].$input.val();
			var minTime = ""; 
			var maxTime = "";

			$.each(wrapper.service_item_data, function (k,v) { 
				if (v["item_code"] == service_item_name) {
					minTime = v["start_time"];
					maxTime = v["end_time"];
				}
			});

			//Prepare Date Filter
			var scheduled_date = wrapper.page.fields_dict["scheduled_date"].$input.val();
			if (scheduled_date) {
				scheduled_date = frappe.datetime.user_to_obj(scheduled_date);
			}

			var options = prepare_options(minTime, maxTime, scheduled_date); 
			if (wrapper.rn_calendar) {
				wrapper.rn_calendar.$cal.remove();
				wrapper.rn_calendar.footnote_area.remove();
			}
			wrapper.rn_calendar = new refreshednow_erpnext.RNCalendar(options, wrapper.page, "refreshednow_erpnext.api.rn_events");
	});
}

function prepare_options(minTime="07:00:00", maxTime="17:00:00", defaultDate) {
	return	{
		header:{
			left: null,
			center: 'title',
			right: null
		},
		allDaySlot: false,
		selectHelper: true,
		forceEventDuration: true,
		defaultView: "agendaWeek",
		selectAllow: function(selectInfo) {
		},
		minTime: minTime,
		maxTime: maxTime,
		eventStartEditable: true,
		eventDurationEditable: true,
		eventClick: function(calEvent, jsEvent, view) {
			frappe.set_route("rn-daily-allocation");
		}, 
		defaultDate: defaultDate || frappe.datetime.get_today()
	}
}
