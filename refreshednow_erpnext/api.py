import frappe
from frappe import _
import json
import calendar
#from datetime import date, datetime, timedelta


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
	
	print "Get Weekly Events: Filters", filters

	filters = json.loads(filters)

	slots = []

	if filters.get("service_type"):
		service_item = frappe.get_doc("Item", filters["service_type"])
		service_date = frappe.utils.data.get_datetime(filters["scheduled_date"]) or frappe.utils.datetime.datetime.today()

		date_range = get_date_range(service_date)
		
		days = (date_range[1] - date_range[0]).days
		
		iter_date = date_range[0]

		for x in xrange(0, days):
			start_time = iter_date
			start_time = start_time.replace(hour=int(service_item.rn_start_time_hours), minute=int(service_item.rn_start_time_minutes), second=0, microsecond=0)

			end_time = iter_date
			end_time = end_time.replace(hour=int(service_item.rn_end_time_hours), minute=int(service_item.rn_end_time_minutes), second=0, microsecond=0)

			daily_slots = get_slots(hours=[start_time, end_time])

			for slot in daily_slots:
				daily_available_slots = get_available_teams_for_slot(service_item, slot["start"])

				slot.update( {"id": frappe.generate_hash(length=5), "title": daily_available_slots, "className": "rn-team" })

			slots = slots + daily_slots

			#print iter_date

			iter_date = iter_date + frappe.utils.datetime.timedelta(days=1)


	return slots

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
def get_rn_daily_resources(filters):
	# resources = [] 
	# resources = [
	# 	{ "id": 'a', "title": 'Team 1' },
	# 	{ "id": 'b', "title": 'Team 2', "eventColor": 'green' },
	# 	{ "id": 'c', "title": 'Team 3', "eventColor": 'orange' },
	# 	{ "id": 'd', "title": 'Team 4', "eventColor": 'red' }
	# ]
	# return resources
	print "Get Daily Resources: Filters", filters

	filters = json.loads(filters)

	# for x in xrange(1,10):
	# 	print "Filters for resources:", filters

	out_teams = []
	teams_by_service = frappe.get_all("RN Team", filters={ "service_type": filters["service_type"] }, fields=['name'])

	for team in teams_by_service:
		out_teams.append({"id":team.name, "title":team.name})

	return out_teams


@frappe.whitelist()
def get_rn_daily_events(start, end, filters=None):
	filters = json.loads(filters)

	out_services = []

	scheduled_services = frappe.get_all("RN Scheduled Service", filters={"service_type": filters["service_type"], "scheduled_date": frappe.utils.data.getdate(filters["scheduled_date"])}, fields=['*'])

	print "Get Daily Events: Filters", filters
	print "Scheduled Services", scheduled_services

	for service in scheduled_services:
		out_services.append({"id": service.name, 
			"resourceId": service.team,
			"start": service.starts_on.isoformat(),
			"end": service.ends_on.isoformat() })

	print out_services
	return out_services

	# events = [
	# 	{ "id": '1', "resourceId": 'a', "start": '2016-12-09', "end": '2016-12-08', "title": 'event 1' },
	# 	{ "id": '2', "resourceId": 'a', "start": '2016-12-21T09:00:00', "end": '2016-12-21T10:00:00', "title": 'event 2' },
	# 	{ "id": '3', "resourceId": 'b', "start": '2016-12-22T11:30:00', "end": '2016-12-22T12:30:00', "title": 'event 3' },
	# 	{ "id": '4', "resourceId": 'c', "start": '2016-12-22T11:30:00', "end": '2016-12-22T12:30:00', "title": 'event 4' },
	# 	{ "id": '5', "resourceId": 'd', "start": '2016-12-09T10:00:00', "end": '2016-12-09T10:00:00', "title": 'event 5' }
	# ]
	# return events


#Datasource for weekly grid. Available people
@frappe.whitelist()
def get_available_teams_for_slot(service_item, start_time):
	#Get list of scheduled services for week.
	#scheduled_services_for_date = frappe.get_all("RN Scheduled Service", filters={"service_type": service_type, "scheduled_date": ref_date})

	#Get teams by service.
	teams_by_service = frappe.get_all("RN Team", filters={"service_type" : service_item.name })
	no_of_teams_by_service = len(teams_by_service)

	#Get Scheduled Services for time by team
	no_of_teams_for_service = int(frappe.db.count("RN Team", filters={"service_type": service_item.name})) or 0

	# team_count_by_service = [t.teams for t in get_service_wise_count_of_teams() if t["service_type"] = service_type]
	no_of_booked_services = int(frappe.db.count("RN Scheduled Service", 
							filters={ "service_type": service_item.name, "starts_on": start_time }))

	available_teams_for_slot = (no_of_teams_for_service - no_of_booked_services)
	
	return available_teams_for_slot


def get_service_wise_total_count_of_teams():
	out = []

	service_items = frappe.get_all("Item", 
		filters={"item_group": get_settings("rn_service_item_group")}, 
		fields=["name", "item_code"])

	for item in service_items:
		no_of_teams = int(frappe.db.count("RN Team", filters={"service_type": item.name})) or 0
		out.append(frappe._dict({ "service_type": item.name, "teams": no_of_teams }))

	return out

def get_week_range(date):
    """Find the first/last day of the week for the given day.
    Assuming weeks start on Sunday and end on Saturday.

    Returns a tuple of ``(start_date, end_date)``.

    """
    # isocalendar calculates the year, week of the year, and day of the week.
    # dow is Mon = 1, Sat = 6, Sun = 7
    year, week, dow = date.isocalendar()

    # Find the first day of the week.
    if dow == 7:
        # Since we want to start with Sunday, let's test for that condition.
        start_date = date
    else:
        # Otherwise, subtract `dow` number days to get the first day
        start_date = date - frappe.utils.datetime.timedelta(dow)

    # Now, add 6 for the last day of the week (i.e., count up to Saturday)
    end_date = start_date + frappe.utils.datetime.timedelta(7)

    return [start_date, end_date]

def get_month_range(scheduled_date):
   	year = scheduled_date.year
	month = scheduled_date.month

	num_days = calendar.monthrange(year, month)[1]
	days = [frappe.utils.datetime.datetime(year, month, day) for day in range(1, num_days+1)]

	out = [min(days),max(days)]
	return out 

def get_date_range(scheduled_date, days_delta=7):
	return [scheduled_date - frappe.utils.datetime.timedelta(days=days_delta), scheduled_date + frappe.utils.datetime.timedelta(days=days_delta)]

 