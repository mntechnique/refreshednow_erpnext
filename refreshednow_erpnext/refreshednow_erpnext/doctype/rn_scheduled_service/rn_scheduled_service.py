# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate
#from frappe.utils.datetime import datetime
from frappe import _
from refreshednow_erpnext.api import send_sms

class RNScheduledService(Document):
	def validate(self):
		self.validate_address()
		self.check_overlap()
		self.validate_schedule_days(allow_scheduling_after_days=0)
		self.check_no_of_vehicles()
		self.validate_team_availability()

	def on_submit(self):
		if not self.sales_invoice:
			self.sales_invoice = self.create_si()
		fire_sms_on_submit(self.service_type,self.starts_on,self.contact_phone)


	def on_cancel(self):
		linked_si = frappe.db.get_value("Sales Invoice", filters={"rn_scheduled_service": self.name}, fieldname="name")

		if linked_si:
			osi = frappe.get_doc("Sales Invoice", linked_si)
			osi.cancel()
			frappe.db.commit()

	def create_si(self):
		defaults_temp = frappe.defaults.get_defaults()

		#Create a sales order if customer is selected.
		si = frappe.new_doc("Sales Invoice")
		si.transaction_date = self.starts_on

		if self.bill_to:
			si.rn_bill_to = self.bill_to

		si.company = defaults_temp.get("company")
		si.customer = self.customer


		#si.rn_service_time_slot = self.starts_on + ", " + self.starts_on + " - " + self.ends_on
		starts_on = frappe.utils.get_datetime(self.starts_on)
		ends_on = frappe.utils.get_datetime(self.ends_on)

		si.rn_service_time_slot = frappe.utils.datetime.datetime.strftime(starts_on, "%d-%m-%Y") + '<br>' + frappe.utils.datetime.datetime.strftime(starts_on, "%H:%M %p") + ' - ' + frappe.utils.datetime.datetime.strftime(ends_on, "%H:%M %p")

		if self.billing_address:
			si.customer_address = self.billing_address
		else:
			si.customer_address = self.service_address

		si.delivery_date = add_days(si.transaction_date, 10)
		si.currency = defaults_temp.get("currency")
		si.selling_price_list = defaults_temp.get("selling_price_list")
		si.rn_scheduled_service = self.name

		si.append("items", {
			"item_code": self.service_type,
			"qty": float(self.vehicle_count),
			"rate": frappe.db.get_value("Item Price", filters={"price_list":si.selling_price_list}, fieldname="price_list_rate"),
			"conversion_factor": 1.0
		})

		try:
			si.save()
			si.submit()
		except Exception, e:
			frappe.throw(_("Sales Invoice was not saved. <br/> %s" % (e)))
		else:
			return si.name

	def create_so(self):
		defaults_temp = frappe.defaults.get_defaults()

		#Create a sales order if customer is selected.
		so = frappe.new_doc("Sales Order")
		so.transaction_date = self.starts_on


		so.company = defaults_temp.get("company")
		so.customer = self.customer
		so.delivery_date = add_days(so.transaction_date, 10)
		so.currency = defaults_temp.get("currency")
		so.selling_price_list = defaults_temp.get("selling_price_list")
		so.rn_scheduled_service = self.name

		so.append("items", {
			"item_code": self.service_type,
			"qty": 1.0,
			"rate": frappe.db.get_value("Item Price", filters={"price_list":so.selling_price_list}, fieldname="price_list_rate"),
			"conversion_factor": 1.0
		})

		try:
			so.save()
		except Exception, e:
			frappe.throw(_("Sales Order was not saved. <br/> %s" % (e)))
		else:
			return so.name

	def check_overlap(self):
		existing_services = frappe.get_all("RN Scheduled Service", filters={"team": self.team, "docstatus" : 1}, fields=["name", "starts_on", "ends_on", "team"])
		for ss in existing_services:
			starts_on = frappe.utils.data.get_datetime(self.starts_on)
			ends_on = frappe.utils.data.get_datetime(self.ends_on)

			# if ss.team == self.team:
			# 	frappe.throw("Team {0} is already scheduled for <a href='/desk#Form/{1}/{2}'>{2}</a>. Please select another team.".format(self.team, self.doctype, ss.name))

			if (starts_on > ss.starts_on and starts_on < ss.ends_on) or \
				(ends_on > ss.starts_on and ends_on < ss.ends_on) or \
				(starts_on <= ss.starts_on and ends_on >= ss.ends_on):
				frappe.throw("This service overlaps with {0}".format(ss.name))

	def validate_schedule_days(self, allow_scheduling_after_days=1, allow_scheduling_after_hours=14):
		#days=1 ---> disallow scheduling of a service before tomorrow.
		allow_scheduling_after_date = frappe.utils.datetime.datetime.today() + frappe.utils.datetime.timedelta(days=allow_scheduling_after_days)

		if frappe.utils.getdate(self.starts_on) < allow_scheduling_after_date.date():
			frappe.throw("Services can be scheduled after {0}".format(frappe.utils.datetime.datetime.strftime(frappe.utils.data.getdate(allow_scheduling_after_date), "%d %b %Y")))

	def check_no_of_vehicles(self):
		if self.vehicle_count <= 0:
			frappe.throw("Must have at least one vehicle for a service.")

	def validate_team_availability(self):
		allocations = frappe.get_all("RN Team Day Employee", filters={"team": self.team, "day_of_week": frappe.utils.get_datetime(self.starts_on).strftime("%A")})
		if len(allocations) == 0:
			frappe.throw("No allocations for this team. <br> Please allocate members to this team using Team Allocation Tool.")

	def validate_address(self):
		if not self.billing_address_same_as_service and not self.billing_address:
			frappe.throw("Please set the billing address.")

# searches for customer
@frappe.whitelist()
def customer_query(doctype, txt, searchfield, start, page_len, filters):
	# cust_master_name = frappe.defaults.get_user_default("cust_master_name")

	# if cust_master_name == "Customer Name":
	# 	fields = ["name", "customer_group", "territory"]
	# else:
	# 	fields = ["name", "customer_name", "customer_group", "territory"]

	# meta = frappe.get_meta("Customer")
	# fields = fields + [f for f in meta.get_search_fields() if not f in fields]

	# fields = ", ".join(fields)

	return frappe.db.sql("""select cust.name, cont.name, cont.phone, cont.mobile_no from `tabCustomer` as cust inner join `tabContact` as cont
		on cust.name = cont.customer
		where docstatus < 2
			and ({key} like %(txt)s
				or cust.name like %(txt)s
				or cont.phone like %(txt)s
				or cont.mobile_no like %(txt)s)
				and disabled=0
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, cust.name), locate(%(_txt)s, cust.name), 99999),
			idx desc,
			name, cust.name
		limit %(start)s, %(page_len)s""".format(**{
			"fields": fields,
			"key": searchfield,
			"mcond": get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})

def fire_sms_on_submit(service_type, starts_on, contact_phone):
		sms_message = "Thank you for contacting Refreshed Car Care. "
		sms_message += "We have taken your booking for "
		sms_message += service_type
		sms_message += " on "
		sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d 'at' HH:m a")
		# send_sms(self.contact_phone, sms_message)

		note = frappe.new_doc("Note")
		note.title = "SMS Log"+ frappe.utils.nowdate() + frappe.utils.nowtime()
		note.public = 1
		note.content = "Sending message to " +  contact_phone + "<hr>" + sms_message
		note.save()
		frappe.db.commit()