// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt
frappe.ui.form.on('RN Team', {
	refresh: function(frm) {		
		frappe.call({
			method: "refreshednow_erpnext.api.get_settings",
			args: {
				fieldname: "rn_service_item_group"
			},
			callback: function(r) {
				if (!r.exc) {
					frm.set_query("service_type", function() {
						return {
							"filters": {
								"item_group": r.message,
							}
						};
					});
				} else {
					console.log(r.exc);
				}
			}
		});
		frm.set_query("supervisor", function() {
	        return {
	            "filters": {
	                "designation": "Supervisor"
	            }
	        };
	    });
	},
});

cur_frm.add_fetch("member", "employee_name", "member_name");
cur_frm.add_fetch("member", "designation", "designation");
cur_frm.add_fetch("structure", "service_type", "service_type");
cur_frm.add_fetch("supervisor", "employee_name", "supervisor_name");
