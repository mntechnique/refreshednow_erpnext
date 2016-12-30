// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('RN Team Tool', {
	refresh: function(frm) {
		frm.disable_save();
		frm.page.hide_menu();
		frm.page.hide_icon_group();
		frm.page.wrapper.find(".timeline").hide();

		reload_members(frm)
		frm.add_custom_button(__("Update Members"), function() {
			if (cur_frm.doc.members.length == 0) {
				frappe.msgprint("There are no members to update.")
			} else {
				frappe.call({
					method: "update_members",
					doc: cur_frm.doc,
					callback: function(r) {
						if (!r.exc) { frappe.show_alert(r.message); }
					}
				});
			}
		});
	},
	team: function(frm) {
		reload_members(frm);		
	}
});

function reload_members(frm) {
	frm.set_value("members", []);
	frappe.call({
		method: "reload_members",
		doc: frm.doc,
		callback: function(r) {
			$.each(r.message, function(idx, val) {
				var row = frappe.model.add_child(frm.doc, "RN Team Member", "members");
				row.member = val.member;
				refresh_field("members");
			});
		}
	});
}
