# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "refreshednow_erpnext"
app_title = "RefreshedNow ERPNext"
app_publisher = "MN Technique"
app_description = "ERPNext Customization for Refreshed Car Care"
app_icon = "fa fa-car"
app_color = "#53baed"
app_email = "support@mntechnique.com"
app_license = "GPLv3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/css/refreshednow.min.css"
app_include_js = "/assets/js/refreshednow.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/refreshednow_erpnext/css/refreshednow_erpnext.css"
# web_include_js = "/assets/refreshednow_erpnext/js/refreshednow_erpnext.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "refreshednow_erpnext.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "refreshednow_erpnext.install.before_install"
# after_install = "refreshednow_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "refreshednow_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
    "Customer": {
        "onload": "refreshednow_erpnext.api.customer_vehicle_onload",
    },
    "Vehicle": {
    	"validate": "refreshednow_erpnext.api.vehicle_validate",
    },
    "Payment Entry": {
        "on_submit": "refreshednow_erpnext.api.pe_on_submit",
        "on_cancel": "refreshednow_erpnext.api.pe_on_cancel",
    },
    "Item": {
        "validate": "refreshednow_erpnext.api.item_validate"
    }
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"refreshednow_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"refreshednow_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"refreshednow_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"refreshednow_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"refreshednow_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "refreshednow_erpnext.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "refreshednow_erpnext.event.get_events"
# }

fixtures = [{"dt":"Custom Script", "filters": [["name", "in", ["Customer-Client"]]]},
	{"dt": "Custom Field", "filters": [["name", "in", [
		"Item-rn_sb_service_item_info",
		"Item-rn_start_time_hours",
		"Item-rn_start_time_minutes",
		"Item-cb_rn_sv_item",
		"Item-rn_end_time_hours",
		"Item-rn_end_time_minutes",
        "Customer-rn_customer_vehicles",
        "Customer-customer_vehicles_",
        "Vehicle-rn_customer",
        "Vehicle-rn_model_make",
        "Sales Invoice-rn_scheduled_service",
        "Item-rn_break_duration",
        "Item-rn_service_duration",
        "Item-rn_break_start_time_minutes",
        "Item-rn_break_start_time_hours",
        "Employee-rn_weekly_off",
        "Sales Invoice-rn_bill_to",
        "Sales Invoice-rn_service_time_slot"
	]]]},
	{"dt": "Property Setter", "filters": [["name", "in", [
		"Vehicle-model-in_list_view",
		"Vehicle-read_only_onload",
		"Vehicle-title_field",
		"Address-address_type-options",
		"Address-read_only_onload",
        "Contact-search_fields",
        "Contact-read_only_onload",
        "Sales Invoice-select_print_heading-default"
	]]]},
    {"dt": "Workflow", "filters": [["name", "in", [
        "RN Scheduled Service"
    ]]]},
    {"dt": "Workflow State", "filters": [["name", "in", [
        "To Schedule",
        "To Dispatch",
        "To Bill",
        "Completed",
        "Stopped"
    ]]]},
    {"dt": "Workflow Action", "filters": [["name", "in", [
        "Confirm",
        "Dispatch",
        "Bill",
        "Stop",
    ]]]}
]
