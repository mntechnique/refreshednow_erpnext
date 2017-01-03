# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate
from frappe import _

class RNScheduledService(Document):
	def validate(self):
		self.check_overlap()
		self.validate_schedule_days()

	def on_update_after_submit(self):
		if self.workflow_state == "To Bill":
			self.create_si()

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

		si.company = defaults_temp.get("company")
		si.customer = self.customer
		si.delivery_date = add_days(si.transaction_date, 10)
		si.currency = defaults_temp.get("currency")		
		si.selling_price_list = defaults_temp.get("selling_price_list")
		si.rn_scheduled_service = self.name

		si.append("items", {
			"item_code": self.service_type,
			"qty": 1.0,
			"rate": frappe.db.get_value("Item Price", filters={"price_list":si.selling_price_list}, fieldname="price_list_rate"),
			"conversion_factor": 1.0
		})

		try:
			si.save()
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
		existing_services = frappe.get_all("RN Scheduled Service", filters={"team": self.team, "docstatus":1}, fields=["name", "starts_on", "ends_on"])
		for ss in existing_services:
			starts_on = frappe.utils.data.get_datetime(self.starts_on)
			ends_on = frappe.utils.data.get_datetime(self.ends_on)

			if (starts_on > ss.starts_on and starts_on < ss.ends_on) or \
				(ends_on > ss.starts_on and ends_on < ss.ends_on) or \
				(starts_on <= ss.starts_on and ends_on >= ss.ends_on):
				frappe.throw("This service overlaps with {0}".format(ss.name))


	def validate_schedule_days(self, allow_scheduling_after_days=1, allow_scheduling_after_hours=14):
		#days=1 => disallow scheduling of a service before tomorrow.
		allowed_date = frappe.utils.datetime.datetime.today() + frappe.utils.datetime.timedelta(days=allow_scheduling_after_days)

		for x in xrange(1,10):
			print allowed_date

		if frappe.utils.data.get_datetime(self.starts_on) < allowed_date: #frappe.utils.datetime.datetime.today() + frappe.utils.datetime.timedelta(days=allow_scheduling_after_days):
			frappe.throw("Services can be scheduled after {0}".format(frappe.utils.data.getdate(allowed_date)))

