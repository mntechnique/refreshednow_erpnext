// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.query_reports["Jobsheet"] = {
	"filters": [
		{
			"fieldname":"service_type",
			"label": __("Service Type"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"starts_on",
			"label": __("Starts On"),
			"fieldtype": "Date",
			"default": moment(new Date()).add(1,'days').locale("en")
		}
	],
}
