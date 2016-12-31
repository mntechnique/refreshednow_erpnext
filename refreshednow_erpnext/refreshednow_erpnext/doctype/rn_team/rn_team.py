# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RNTeam(Document):
	def validate(self):
		self.validate_teams()

	def validate_teams(self):
		member_emps = []

		for member in self.members:
			member_emps.append(member.member)

			containing_teams = frappe.get_all("RN Team Member", filters=[["member", "=", member.member],["parent", "!=", self.name]], fields=['parent'])
			if len(containing_teams) > 0:
				frappe.throw("Member {0} already exists in team {1}".format(member.member_name, containing_teams[0].parent))
		
		if len(member_emps) != len(set(member_emps)):
			frappe.throw("There are duplicate members in this team!")	 