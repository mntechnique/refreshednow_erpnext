

frappe.pages['rn-weekly-resource'].on_page_load = function(wrapper) {

	frappe.require(["assets/frappe/js/lib/fullcalendar/fullcalendar.min.js", "assets/frappe/js/lib/fullcalendar/fullcalendar.min.css"], 
			function() { console.log("require")});

	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Available Cleaners by Week',
		single_column: true
	});

	var content = null;

	frappe.call({
		method: "refreshednow_erpnext.api.get_available_cleaners",
		callback: function(r) {
			console.log(r);

			content = page.wrapper.find(".page-content");
			content.append(frappe.render_template("available_cleaners", {"available_cleaners": r.message}))
			
			wireup_fullcalendar(content);
		}
	});
}

function wireup_fullcalendar(content) {
	var calendarhost = content.find('#calendarhost');

	var calendar_options = {
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		//editable: true,
		//selectable: true,
		selectHelper: true,
		forceEventDuration: true,
		defaultView: "agendaWeek",
		minTime: "10:00:00",
		maxTime: "16:00:00",
		eventStartEditable: true,
		eventDurationEditable: true,
		schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
		eventClick: function(calEvent, jsEvent, view) {

			alert('Event: ' + calEvent.title);
			alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
			alert('View: ' + view.name);

			// change the border color just for fun
			$(this).css('border-color', 'green');

		}
	}

	console.log(calendarhost);
	calendarhost.fullCalendar(calendar_options);

}