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
		# existing = frappe.db.sql("""select name from `tabRN Scheduled Service` as rnss where
		# 		(
		# 			('{starts_on}' > rnss.starts_on and '{starts_on}' < rnss.ends_on) or
		# 			('{ends_on}' > rnss.starts_on and '{ends_on}' < rnss.ends_on) or
		# 			('{starts_on}' <= rnss.starts_on and '{ends_on}' >= rnss.ends_on)
		# 		)
		# 	and rnss.name!='{name}'""".format(
		# 		starts_on=self.starts_on,
		# 		ends_on=self.ends_on,
		# 		name=self.name
		# 	), as_dict=True)

		# if len(existing) > 0:
		# 	frappe.throw("This service will overlap with {0} other service(s).".format(len(existing)))sta
		print "-----"
		print self.team
		print "-----"
		existing_services = frappe.get_all("RN Scheduled Service", filters={"team": self.team}, fields=["name", "starts_on", "ends_on"])
		print existing_services
		print "-----"

		for ss in existing_services:
			starts_on = frappe.utils.data.get_datetime(self.starts_on)
			ends_on = frappe.utils.data.get_datetime(self.ends_on)

			if (starts_on > ss.starts_on and starts_on < ss.ends_on) or \
				(ends_on > ss.starts_on and ends_on < ss.ends_on) or \
				(starts_on <= ss.starts_on and ends_on >= ss.ends_on):
				frappe.throw("This service overlaps with {0}".format(ss.name))

