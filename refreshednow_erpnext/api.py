import frappe
from frappe import _

@frappe.whitelist()
def get_available_cleaners():
	return "Hanumant Shinde"

@frappe.whitelist()
def get_daily_allocation():
	return "Yeshwant 'Nana' Shinde"

@frappe.whitelist()
def get_caller_number(caller_number):

	cname = frappe.db.get_value("Contact",{"mobile_no":caller_number},"customer")
	if cname:
		#Create stub lead if lead is not found.
		c = frappe.get_doc("Customer",cname)
		out = frappe._dict({"name":c.customer_name,
								"mobile_number":caller_number,
								"phone":frappe.db.get_value("Contact",{"mobile_no":caller_number},"phone"),
								"caller_type":"Customer",
								"email_id":frappe.db.get_value("Contact",{"mobile_no":caller_number},"email_id")})
		return out
	lname = frappe.db.get_value("Lead",{"mobile_no":caller_number},"name")
	if lname:
		l = frappe.get_doc("Lead",lname)
		out = frappe._dict({"name":l.lead_name,
							"mobile_number":caller_number,
							"phone":l.phone,
							"email_id":l.email_id,
							"caller_type":"Lead"
			})
		return out
	return frappe._dict({"name":"New Lead","caller_type":"New Lead"})


# @frappe.whitelist()
# def get_email_list():
# 	import email
# 	email_queue_list = frappe.get_list("Email Queue", fields=["name", "recipient", "modified", "message", "acumen_email_subject"], filters={"status":"Sent"})

# 	rmsg = []

# 	for email_queue in email_queue_list:
# 		b = email.message_from_string(email_queue.message)

# 		if b['Subject'].startswith("Weekly status"):
# 			rmsg.append(
# 				frappe._dict({
# 					"name": email_queue.name,
# 					"recipient":email_queue.recipient,
# 					"content":render_html_email_msg(email_queue.name),
# 					"modified": frappe.utils.data.getdate(email_queue.modified)
# 				}),
# 			)

# 	return rmsg

