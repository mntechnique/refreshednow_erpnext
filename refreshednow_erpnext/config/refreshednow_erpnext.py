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
					"name": "rn-weekly-resource",
					"label": "Weekly Availability of Resources",
					"description": _("Weekly Availability of Resources."),
				},
			]
		}
	]
