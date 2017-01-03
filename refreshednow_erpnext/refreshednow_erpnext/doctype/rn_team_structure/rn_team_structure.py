# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RNTeamStructure(Document):
	def validate(self):
		self.validate_designations_and_strength()

	def validate_designations_and_strength((self):
		designation_list = []
		for structure in self.team_structure:
			designation_list.append(structure.designation)
			if structure.strength <= 0:
				frappe.throw(_("Strength must be positive number"))

		if len(designation_list)!= len(set(designation_list)):
			frappe.throw(_("Same designation is entered more than once"))
