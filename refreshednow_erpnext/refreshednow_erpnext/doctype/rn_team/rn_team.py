# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class RNTeam(Document):
	def autoname(self):
		service_type = "TEAM"
		if "go" in self.service_type.lower():
			service_type += "-GO"	
		elif "pro" in self.service_type.lower():
			service_type += "-PRO"

		self.name = make_autoname(service_type + "-.##")

	def validate(self):
		self.validate_teams()
		self.validate_team_structure()

	def validate_teams(self):
		member_emps = []

		for member in self.members:
			member_emps.append(member.member)

			containing_teams = frappe.get_all("RN Team Member", filters=[["member", "=", member.member],["parent", "!=", self.name]], fields=['parent'])
			if len(containing_teams) > 0:
				frappe.throw("Member {0} already exists in team {1}".format(member.member_name, containing_teams[0].parent))
		
		if len(member_emps) != len(set(member_emps)):
			frappe.throw("There are duplicate members in this team!")

	def validate_team_structure(self):
		ts = frappe.get_doc("RN Team Structure", self.structure)

		designations_in_structure = [tsi.designation for tsi in ts.team_structure]
		# designations_in_team = [member.designation for member in self.members]
		for member in self.members:
			member_designation = frappe.db.get_value("Employee", member.member, "designation")

			if member_designation not in designations_in_structure:
				frappe.throw("This team cannot have members with designation {0}.".format(member_designation))

		for item in ts.team_structure:
			#Designation must exist in structure.
			member_count_by_designation = len([x for x in self.members if frappe.db.get_value("Employee", x.member, "designation") == item.designation])

			if member_count_by_designation > item.strength:
				frappe.throw("Can have a maximum of {0} members with designation {1}.".format(item.strength, item.designation))
