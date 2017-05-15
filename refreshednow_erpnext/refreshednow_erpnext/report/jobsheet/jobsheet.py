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

	columns = [_("Type")] + [_("Time")] + [_("ID")] + \
	[_("Name")] + [_("Contact")] + [_("Address")] + \
	[_("Comments")] + [_("Car")] + [_("Cleaner Name")] + [_("Payment")]

	return columns

def get_service_data(filters):
	item_map = {}

	servicelist = frappe.db.sql("""SELECT service_type,starts_on,name,customer,contact,service_address_display,notes FROM `tabRN Scheduled Service`
				WHERE docstatus = 1""".format(
				), as_dict=1)

	print servicelist

	return servicelist	