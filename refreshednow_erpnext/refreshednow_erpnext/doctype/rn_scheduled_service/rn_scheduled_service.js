// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('RN Scheduled Service', {
	refresh: function(frm) {

		if (frm.doc.workflow_state == "Completed") {
			frm.set_df_property("remarks", "read_only", 1);
		}

		frm.add_custom_button(__("Go to Team Scheduling"), function() {
			frappe.set_route("rn-team-scheduling");
		});

		
		// //Set sales order if exists.
		// frappe.db.get_value("Sales Order", {"rn_scheduled_service": cur_frm.doc.name}, "name", function(r) {
		//     if (r) {
		//         cur_frm.set_value("sales_order", r.name);
		//     } else {
		//     	add_make_so_button(cur_frm);
		//     }
		// });

		//Set sales order if exists.
		// frappe.db.get_value("Sales Invoice", {"rn_scheduled_service": cur_frm.doc.name}, "name", function(r) {
		//     if (r) {
		//         cur_frm.set_value("sales_invoice", r.name);
		//     }
		// });

		//Show service items only.
		frappe.db.get_value("RN Settings", "RN Settings", "rn_service_item_group", function(r) {
			cur_frm.set_query("service_type", function() {
				return {
					"filters": {
						"item_group": r.rn_service_item_group,
					}
				};
			});	
		})
		//Filter dropdowns by Customer and pertinent criteria.
		cur_frm.set_query("billing_address", function() {
			return {
				"filters": {
					"customer": frm.doc.customer,
					"address_type": "Billing"
				}
			};
		});
		cur_frm.set_query("service_address", function() {
			return {
				"filters": {
					"customer": frm.doc.customer,
					"address_type": "Service"
				}
			};
		});
		cur_frm.set_query("vehicle", function() {
			return {
				"filters": {
					"rn_customer": frm.doc.customer
				}
			};
		});

		render_vehicles(frm);
		render_team_members(frm);
		render_timeslot(frm);
	},
	customer: function(frm) {
		fetch_and_set_addresses(frm);		
	},
	vehicle: function(frm) {
		render_vehicles(frm);		
	},
	team: function(frm) {
		render_team_members(frm);
	}
});

function render_vehicles(frm) {
	$(frm.fields_dict['vehicle_details_html'].wrapper)
				.html("<div class='text-muted text-center' style='padding-top:5%;'>Please select a vehicle.</div>");

	if (frm.doc.vehicle) {
		frappe.model.with_doc("Vehicle", frm.doc.vehicle, function(vehicle_name) {
			var vehicle = frappe.model.get_doc("Vehicle", vehicle_name);
			$(frm.fields_dict['vehicle_details_html'].wrapper)
				.html(frappe.render_template("customer_vehicle", {"customer_vehicle": [vehicle]})).find(".btn-vehicle").addClass("hide");
		});
	}
}

function render_team_members(frm) {
	$(frm.fields_dict['team_details_html'].wrapper)
				.html("<div class='text-muted text-center' style='padding-top:5%;'>Please select a team</div>");

	if (frm.doc.team) {
		frappe.call({
			method: "refreshednow_erpnext.api.get_team_members",
			args: {"team_name": frm.doc.team },
			callback: function(r) {
				console.log(r);
				$(frm.fields_dict['team_details_html'].wrapper)
				 .html(frappe.render_template("team_details", {"team_name": frm.doc.team, "team_members": r.message}));	
			}
		});
	}
}

function fetch_and_set_addresses(frm) {
	frappe.db.get_value(
		"Address",
		{ "customer":frm.doc.customer, "address_type":"Billing", "is_primary_address":true }, 
		"name", 
		function(r) {
			if (r) {
				//console.log(r);
				frm.set_value("billing_address", r.name);	
			}
		}
	);
}

function render_timeslot(frm) {
	var starts_on = moment(frm.doc.starts_on).format("h:mm a");
	var ends_on = moment(frm.doc.ends_on).format("h:mm a");
	var timeslot = moment(frm.doc.starts_on).format("DD MMM Y") + ", " + starts_on + " - " + ends_on;

	var timeslot_html = '<div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Time Slot</label> </div> <div class="control-input-wrapper"> <div class="control-input-static"> <div class="link-field ui-front" style="position: relative;">' + timeslot + '</div> </div> </div> </div>';

	$(frm.fields_dict['timeslot_html'].wrapper)
				.html(timeslot_html);
}

// function add_make_so_button(frm) {
// 	if ((!frm.doc.sales_order) && (frm.doc.docstatus == 1)) {
// 		frm.add_custom_button(__("Sales Order"), function() {
// 			frappe.call({
// 				method: "create_so",
// 				doc: cur_frm.doc,
// 				callback: function(r){
// 					if (r) {
// 						cur_frm.set_value("sales_order", r.message);
// 						frappe.show_alert("Sales Order " + r.message + " created successfully.", 5);
// 						cur_frm.refresh();
// 					}
// 				}
// 			})
// 		},__("Make"));
// 	}
// }