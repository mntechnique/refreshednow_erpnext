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
			team.append("members", {"member":member.member})
		
		team.save()
		frappe.db.commit()


	def reload_members(self):
		#return "Members Loaded for {0}".format(self.team)
		return frappe.get_all("RN Team Member", filters={"parent":self.team}, fields=["*"])
