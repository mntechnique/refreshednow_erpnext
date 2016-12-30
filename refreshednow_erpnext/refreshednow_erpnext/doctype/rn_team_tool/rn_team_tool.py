# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RNTeamTool(Document):
	def update_members(self):
		team = frappe.get_doc("RN Team", self.team)

		for member in self.members:
			if member.member not in [m.member for m in team.members]:
				team.append("members", {"member":member.member})

		for team_member in team.members:
			if team_member.member not in [m.member for m in self.members]:
				frappe.delete_doc("RN Team Member", filter={"parent": self.team, "member":member})

		team.save()
		frappe.db.commit() 

		return "Members updated for {0}".format(self.team)


	def reload_members(self):
		#return "Members Loaded for {0}".format(self.team)
		return frappe.get_all("RN Team Member", filters={"parent":self.team}, fields=["*"])
