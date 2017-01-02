# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate
from frappe import _

class RNScheduledService(Document):
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
