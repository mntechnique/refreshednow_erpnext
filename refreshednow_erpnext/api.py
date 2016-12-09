import frappe
from frappe import _

@frappe.whitelist()
def get_cleaner_availability():
	events = [
		{ "id": '1', "start": '2016-12-09', "end": '2016-12-08', "title": 'event 1'},
		{ "id": '2', "start": '2016-12-07T09:00:00', "end": '2016-12-07T14:00:00', "title": 'event 2'},
		{ "id": '3', "start": '2016-12-08T11:30:00', "end": '2016-12-08T12:00:00', "title": 'event 3' },
		{ "id": '4', "start": '2016-12-09T07:30:00', "end": '2016-12-09T09:30:00', "title": 'event 4' },
		{ "id": '5', "start": '2016-12-10T10:00:00', "end": '2016-12-10T15:00:00', "title": 'event 5' }
	]

	return events

@frappe.whitelist()
def get_cleaners(date):
	resources = [] #resources = cleaners, events = allocations
	
	resources = [
		{ "id": 'a', "title": 'Team 1' },
		{ "id": 'b', "title": 'Team 2', "eventColor": 'green' },
		{ "id": 'c', "title": 'Team 3', "eventColor": 'orange' },
		{ "id": 'd', "title": 'Team 4', "eventColor": 'red' }
	]

	return resources

@frappe.whitelist()
def get_timeslots(start, end, filters=None):
	events = [
		{ "id": '1', "resourceId": 'a', "start": '2016-12-09', "end": '2016-12-08', "title": 'event 1' },
		{ "id": '2', "resourceId": 'a', "start": '2016-12-09T09:00:00', "end": '2016-12-09T14:00:00', "title": 'event 2' },
		{ "id": '3', "resourceId": 'b', "start": '2016-12-09T11:30:00', "end": '2016-12-09T12:00:00', "title": 'event 3' },
		{ "id": '4', "resourceId": 'c', "start": '2016-12-09T07:30:00', "end": '2016-12-09T09:30:00', "title": 'event 4' },
		{ "id": '5', "resourceId": 'd', "start": '2016-12-09T10:00:00', "end": '2016-12-09T15:00:00', "title": 'event 5' }
	]

	return events

