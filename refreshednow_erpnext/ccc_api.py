#Call Centre Console API
import frappe
from frappe import _
import json
from datetime import datetime, timedelta


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

@frappe.whitelist()
def create_contact(customer_name, caller_number):
	cd = frappe.new_doc("Contact")
	cd.mobile_no = caller_number
	cd.first_name = "{m}".format(c=customer_name, m=caller_number)
	cd.customer = customer_name
	cd.insert(ignore_permissions=True)
	frappe.db.commit()
	return cd.name