# Copyright (c) 2013, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_service_data(filters)
	return columns, data

def get_columns(filters):
	"""return columns based on filters"""

	return [
		_("Type") + "::90",
		_("Time") + ":Datetime:150",
		_("ID") + ":Link/RN Scheduled Service:75",
		_("Name") + "::120",
		_("Contact No") + "::100",
		_("Address") + "::300",
		_("Notes") + "::150",
		_("Car") + "::75",
		_("Cleaner Name") + "::75",
		_("Payment") + "::75",
	]


def get_service_data(filters):
	data = []
	services = frappe.get_all("RN Scheduled Service", filters=[["docstatus", "=", "1"]], fields=["*"], order_by="service_type, starts_on")

	if filters:
		if "starts_on" in filters:
			services = [ss for ss in services if frappe.utils.getdate(ss.starts_on) == frappe.utils.getdate(filters["starts_on"])]
		if "service_type" in filters:
			services = [ss for ss in services if ss.service_type == filters["service_type"]]

	for service in services:
		row = []
		row.append(service.service_type)
		row.append(service.starts_on)
		row.append(service.name)
		row.append(service.customer)
		row.append(service.contact_phone)
		addr = service.service_address_display.replace(",<br>", ",")
		addr = addr.replace("<br>", ",", 5)
		addr = addr.replace("<br>", ".")
		row.append(addr)
		row.append(service.notes)
		row.append(" ")
		row.append(" ")
		row.append(" ")
		data.append(row)
			
	return data	