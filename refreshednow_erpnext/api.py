import frappe
from frappe import _
import json


@frappe.whitelist()
def get_cleaner_availability(date, service_item):
	# events = [
	#   { "id": '1', "start": '2016-12-20', "end": '2016-12-20', "title": 'event 1'},
	#   { "id": '2', "start": '2016-12-20T09:00:00', "end": '2016-12-20T14:00:00', "title": 'event 2'},
	#   { "id": '3', "start": '2016-12-21T11:30:00', "end": '2016-12-21T12:00:00', "title": 'event 3' },
	#   { "id": '4', "start": '2016-12-22T07:30:00', "end": '2016-12-22T09:30:00', "title": 'event 4' },
	#   { "id": '5', "start": '2016-12-23T10:00:00', "end": '2016-12-23T15:00:00', "title": 'event 5' }
	# ]
	pass


@frappe.whitelist()
def rn_events_test(start, end, filters=None):
	events = [
		{ "id": '1', "start": '2016-12-20', "end": '2016-12-20', "title": 'event 1'},
		{ "id": '2', "start": '2016-12-20T09:00:00', "end": '2016-12-20T14:00:00', "title": 'event 2'},
		{ "id": '3', "start": '2016-12-21T11:30:00', "end": '2016-12-21T12:00:00', "title": 'event 3' },
		{ "id": '4', "start": '2016-12-22T07:30:00', "end": '2016-12-22T09:30:00', "title": 'event 4' },
		{ "id": '5', "start": '2016-12-23T10:00:00', "end": '2016-12-23T15:00:00', "title": 'event 5' },
		{ "id": '6', "start": '2016-12-24T10:00:00', "end": '2016-12-24T15:00:00', "title": filters }
	]
	return events

@frappe.whitelist()
def rn_events(start, end, filters=None):
	service_item = None

	filters = json.loads(filters)

	slots = []

	if filters.get("service_type"):

		service_item = frappe.get_doc("Item", filters["service_type"])
		service_date = frappe.utils.data.get_datetime(filters["scheduled_date"]) or frappe.utils.datetime.datetime.today()

		week_start = service_date.replace(day=(service_date.day - (service_date.weekday() + 1)))
		week_end = service_date.replace(day=(service_date.day + (7 - (service_date.weekday() + 1))))
		iter_date = week_start
		days = (week_end - week_start).days + 1


		# print "Week Start: ", str(week_start)
		# print "Week End: ",  str(week_end)
		# print "Days: ",  days

		for x in xrange(0, days):
			#print "Week Start: ", str(week_start)
			start_time = iter_date
			start_time = start_time.replace(hour=int(service_item.rn_start_time_hours), minute=int(service_item.rn_start_time_minutes), second=0, microsecond=0)

			end_time = iter_date
			end_time = end_time.replace(hour=int(service_item.rn_end_time_hours), minute=int(service_item.rn_end_time_minutes), second=0, microsecond=0)

			# print "Start Time: ", start_time
			# print "End Time: ", end_time

			daily_slots = get_slots(hours=[start_time, end_time])

			for slot in daily_slots:
				slot.update( {"id": frappe.generate_hash(length=5), "title": '10', "className": "rn-team" })

			slots = slots + daily_slots

			iter_date = iter_date.replace(day=(iter_date.day + 1))

	return slots




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
		out = frappe._dict({"name":c.name,
								"display_name": c.customer_name,
								"mobile_number":caller_number,
								"phone":frappe.db.get_value("Contact",{"mobile_no":caller_number},"phone"),
								"caller_type":"Customer",
								"email_id":frappe.db.get_value("Contact",{"mobile_no":caller_number},"email_id")})
		return out
	lname = frappe.db.get_value("Lead",{"mobile_no":caller_number},"name")
	if lname:
		l = frappe.get_doc("Lead",lname)
		out = frappe._dict({"name":l.name,
							"display_name": l.lead_name,
							"mobile_number":caller_number,
							"phone":l.phone,
							"email_id":l.email_id,
							"caller_type":"Lead"
			})
		return out
	
	return frappe._dict({"name": "", 
						 "display_name": "New Lead", 
						 "caller_type":"New Lead"})


@frappe.whitelist()
def create_lead(caller_number):
		#Create stub lead if lead is not found.
		ld = frappe.new_doc("Lead")
		ld.mobile_no = caller_number
		ld.lead_name = "New Lead ({m})".format(m=caller_number)

		#Set mandatory custom fields.
		# ld.lead_owner = agent_id
		# ld.owner = agent_id
		# frappe.set_user(agent_id)
		ld.insert(ignore_permissions=True)
		frappe.db.commit()
		return ld.name

def get_slots(hours, duration=frappe.utils.datetime.timedelta(hours=1)):
	"""
	Generate Timeslots based on list of hours and duration

	:param hours: list of hours = [frappe.utils.datetime.datetime(2016, 12, 14, 9),
																frappe.utils.datetime.datetime(2016, 12, 14, 18)]
	:param duration: default duration of one hour.
	"""
	out = []
	slots = sorted([(hours[0], hours[0])] + [(hours[1], hours[1])])
	for start, end in ((slots[i][1], slots[i+1][0]) for i in range(len(slots)-1)):
			assert start <= end, "Start time should be before end time"
			while start + duration <= end:
					out.append(frappe._dict({"start":start.isoformat(), "end":(start + duration).isoformat()}))
					start += duration
	return out


@frappe.whitelist()
def create_contact(customer_name, caller_number):
		cd = frappe.new_doc("Contact")
		cd.mobile_no = caller_number
		cd.first_name = "{m}".format(m=caller_number)
		cd.customer = customer_name
		cd.insert(ignore_permissions=True)
		frappe.db.commit()
		return cd.name


@frappe.whitelist()
def get_settings(fieldname):
	try:
		out = frappe.db.get_value("RN Settings", "RN Settings", fieldname)
	except Exception as e:
		out = ""

	return out


@frappe.whitelist()
def get_service_item_timings():
	service_items = frappe.get_all("Item", 
		filters={"item_group": get_settings("rn_service_item_group")}, 
		fields=["name", "item_code", "rn_start_time_hours", "rn_start_time_minutes", "rn_end_time_hours", "rn_end_time_minutes"])

	out = []
	for item in service_items:
		out.append(
			frappe._dict({
				"item_code": item.get("item_code"),
				"start_time": "{0}:{1}:00".format(item.get("rn_start_time_hours"), item.get("rn_start_time_minutes")),
				"end_time": "{0}:{1}:00".format(item.get("rn_end_time_hours"), item.get("rn_end_time_minutes")),
			})
		)

	return out

@frappe.whitelist()
def get_rn_daily_resources():
	resources = [] 
	resources = [
		{ "id": 'a', "title": 'Team 1' },
		{ "id": 'b', "title": 'Team 2', "eventColor": 'green' },
		{ "id": 'c', "title": 'Team 3', "eventColor": 'orange' },
		{ "id": 'd', "title": 'Team 4', "eventColor": 'red' }
	]
	return resources

@frappe.whitelist()
def get_rn_daily_events(start, end, filters=None):
	events = [
		{ "id": '1', "resourceId": 'a', "start": '2016-12-09', "end": '2016-12-08', "title": 'event 1' },
		{ "id": '2', "resourceId": 'a', "start": '2016-12-21T09:00:00', "end": '2016-12-21T10:00:00', "title": 'event 2' },
		{ "id": '3', "resourceId": 'b', "start": '2016-12-22T11:30:00', "end": '2016-12-22T12:30:00', "title": 'event 3' },
		{ "id": '4', "resourceId": 'c', "start": '2016-12-22T11:30:00', "end": '2016-12-22T12:30:00', "title": 'event 4' },
		{ "id": '5', "resourceId": 'd', "start": '2016-12-09T10:00:00', "end": '2016-12-09T10:00:00', "title": 'event 5' }
	]
	return events
