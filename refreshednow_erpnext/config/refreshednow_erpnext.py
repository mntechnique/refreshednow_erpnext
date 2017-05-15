from frappe import _

def get_data():
	return [
		{
			"label": _("Call Center"),
			"icon": "icon-star",
			"items": [
				{
					"type": "page",
					"name": "customer-lookup",
					"label": "Call Center Console",
					"description": _("Call center console."),
				},
			]
		},
		{
			"label": _("Teams"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "RN Team",
					"label": "Teams",
					"description": _("List of Teams."),
				},
				{
					"type": "doctype",
					"name": "RN Team Structure",
					"label": "Team Structure",
					"description": _(""),
				},
				{
					"type": "page",
					"name": "rn-team-tool",
					"label": "Team Allocation Tool",
					"description": _("Assign members to teams for each day of the week."),
				},	
			]
		},
		{
			"label": _("Scheduling"),
			"icon": "icon-star",
			"items": [
				{
					"type": "page",
					"name": "rn-team-scheduling",
					"label": "Service Scheduling Tool",
					"description": _("Schedule cleaning services based on available teams."),
				},
				{
					"type": "doctype",
					"name": "RN Scheduled Service",
					"label": "Scheduled Services List",
					"description": _("Flat list of scheduled services"),
				},
			]
		},
		{
			"label": _("Settings"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "RN Settings",
					"label": "RN Settings",
					"description": _("Tool for settings."),
				},
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"name": "Jobsheet",
					"label": "Jobsheet",
					"description": _("Jobsheet"),
					"route": "query-report/Jobsheet",
					"doctype": "DocType"
				},
			]
		}
	]
