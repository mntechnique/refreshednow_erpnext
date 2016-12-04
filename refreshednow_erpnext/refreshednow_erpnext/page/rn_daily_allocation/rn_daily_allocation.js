frappe.pages['rn-daily-allocation'].on_page_load = function(wrapper) {

	frappe.require(["assets/refreshednow_erpnext/js/lib/fullcalendar.min.js", 
		"assets/refreshednow_erpnext/js/lib/fullcalendar.min.css"], 
			function() { console.log("calendar")});

	frappe.require(["assets/refreshednow_erpnext/js/lib/scheduler.min.js", 
		"assets/refreshednow_erpnext/js/lib/scheduler.min.css"], 
			function() { console.log("scheduler")});

	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Daily Allocation',
		single_column: true
	});

	var content = null;

	frappe.call({
		method: "refreshednow_erpnext.api.get_daily_allocation",
		callback: function(r) {
			console.log(r);

			content = page.wrapper.find(".page-content");
			content.append(frappe.render_template("daily_allocation", {"daily_allocation": r.message}))
			
			wireup_fullcalendar(content);
		}
	});
}

function wireup_fullcalendar(content) {
	var calendarhost = content.find('#calendarhost');

	var scheduler_options = {
		//editable: true,
		//selectable: true,
		allDaySlot: false,
		selectHelper: true,
		forceEventDuration: true,
		defaultView: "agendaDay",
		minTime: "10:00:00",
		maxTime: "16:00:00",
		eventStartEditable: true,
		eventDurationEditable: true,
		schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
		events:  [
			{ id: '1', resourceId: 'a', start: '2016-09-06', end: '2016-09-08', title: 'event 1' },
			{ id: '2', resourceId: 'a', start: '2016-09-07T09:00:00', end: '2016-09-07T14:00:00', title: 'event 2' },
			{ id: '3', resourceId: 'b', start: '2016-09-07T12:00:00', end: '2016-09-08T06:00:00', title: 'event 3' },
			{ id: '4', resourceId: 'c', start: '2016-09-07T07:30:00', end: '2016-09-07T09:30:00', title: 'event 4' },
			{ id: '5', resourceId: 'd', start: '2016-09-07T10:00:00', end: '2016-09-07T15:00:00', title: 'event 5' }
		],
		resources: [
			{ id: 'a', title: 'Room A' },
			{ id: 'b', title: 'Room B', eventColor: 'green' },
			{ id: 'c', title: 'Room C', eventColor: 'orange' },
			{ id: 'd', title: 'Room D', eventColor: 'red' }
		],
		eventClick: function(calEvent, jsEvent, view) {

			alert('Event: ' + calEvent.title);
			alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
			alert('View: ' + view.name);

			// change the border color just for fun
			$(this).css('border-color', 'green');

		}
	}
	calendarhost.fullCalendar(scheduler_options);
}


