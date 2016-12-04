import frappe
from frappe import _

@frappe.whitelist()
def get_available_cleaners():
	return "Hanumant Shinde"

@frappe.whitelist()
def get_daily_allocation():
	return "Yeshwant 'Nana' Shinde"