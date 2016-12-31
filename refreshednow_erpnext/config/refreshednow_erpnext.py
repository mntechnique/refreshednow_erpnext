from frappe import _

def get_data():
	return [
		{
			"label": _("Tools"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "RN Team Tool",
					"label": "Team Tool",
					"description": _("Tool for assigning members to teams."),
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
