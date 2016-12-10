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

@frappe.whitelist()
def get_caller_number(caller_number):
	cname = frappe.db.get_value("Contact",{"mobile_no":caller_number},"customer")
	if cname:
		#Create stub lead if lead is not found.
		c = frappe.get_doc("Customer",cname)
		out = frappe._dict({"name":c.customer_name,
								"mobile_number":caller_number,
								"phone":frappe.db.get_value("Contact",{"mobile_no":caller_number},"phone"),
								"caller_type":"Customer",
								"email_id":frappe.db.get_value("Contact",{"mobile_no":caller_number},"email_id")})
		return out
	lname = frappe.db.get_value("Lead",{"mobile_no":caller_number},"name")
	if lname:
		l = frappe.get_doc("Lead",lname)
		out = frappe._dict({"name":l.lead_name,
							"mobile_number":caller_number,
							"phone":l.phone,
							"email_id":l.email_id,
							"caller_type":"Lead"
			})
		return out
	return frappe._dict({"name":"New Lead","caller_type":"New Lead"})
