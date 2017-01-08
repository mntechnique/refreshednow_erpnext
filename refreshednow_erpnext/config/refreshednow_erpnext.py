from frappe import _

def get_data():
	return [
		{
			"label": _("Tools"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "RN Team",
					"label": "Teams",
					"description": _("List of Teams."),
				},
				{
					"type": "page",
					"name": "rn-team-scheduling",
					"label": "Team Scheduling",
					"description": _("Schedule cleaning services based on available teams."),
				},
				{
					"type": "page",
					"name": "customer-lookup",
					"label": "Call Center Console",
					"description": _("Call Center Console"),
				},
				{
					"type": "doctype",
					"name": "RN Scheduled Service",
					"label": "Scheduled Service",
					"description": _("Scheduled Service"),
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
					"label": "Team Tool",
					"description": _("Assign members to teams for each day of the week."),
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
		}
	]
