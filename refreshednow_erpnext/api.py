import frappe
from frappe import _

@frappe.whitelist()
def get_available_cleaners():
	return "Hanumant Shinde"

@frappe.whitelist()
def get_cleaners(date):
	resources = [] #resources = cleaners, events = allocations
	
	resources = [
		{ "id": 'a', "title": 'Room A' },
		{ "id": 'b', "title": 'Room B', "eventColor": 'green' },
		{ "id": 'c', "title": 'Room C', "eventColor": 'orange' },
		{ "id": 'd', "title": 'Room D', "eventColor": 'red' }
	]

	return frappe._dict({"resources": resources})

@frappe.whitelist()
def get_timeslots(start, end, filters=None):
	events = [
		{ "id": '1', "resourceId": 'a', "start": '2016-12-07', "end": '2016-12-08', "title": 'event 1' },
		{ "id": '2', "resourceId": 'a', "start": '2016-12-07T09:00:00', "end": '2016-12-07T14:00:00', "title": 'event 2' },
		{ "id": '3', "resourceId": 'b', "start": '2016-12-07T11:30:00', "end": '2016-12-07T12:00:00', "title": 'event 3' },
		{ "id": '4', "resourceId": 'c', "start": '2016-12-07T07:30:00', "end": '2016-12-07T09:30:00', "title": 'event 4' },
		{ "id": '5', "resourceId": 'd', "start": '2016-12-07T10:00:00', "end": '2016-12-07T15:00:00', "title": 'event 5' }
	]

	return frappe._dict({"events": events})

