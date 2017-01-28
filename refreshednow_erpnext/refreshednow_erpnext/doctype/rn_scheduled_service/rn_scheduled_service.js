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
		cur_frm.set_query("customer", function() {
			return {
				"query": "refreshednow_erpnext.api.customer_query"
			};
		});
		cur_frm.set_query("contact_person", function() {
			return {
				"filters": {
					"customer": cur_frm.doc.customer
				}
			};
		});
		cur_frm.set_query("team", function() {
			return {
				"filters": {
					"service_type": cur_frm.doc.service_type
				}
			};
		});
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
					"address_type": "Billing"
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

		frm.fields_dict.customer.new_doc = quick_entry_customer;
		frm.fields_dict.service_address.new_doc = quick_entry_service_address;
		frm.fields_dict.billing_address.new_doc = quick_entry_billing_address;
		frm.fields_dict.vehicle.new_doc = quick_entry_vehicle;
		frm.fields_dict.contact_person.new_doc = quick_entry_contact;
		
		if (!frm.doc.vehicle_count) { frm.set_value("vehicle_count", 1); }
	},
	customer: function(frm) {
		clear_fields_on_customer_change();
		if (frm.doc.customer) {
			fetch_and_set_linked_fields(frm);
			frm.set_value("bill_to", frm.doc.customer);
		} else {
			frm.doc.customer = undefined; //REQD
		}
	},
	vehicle: function(frm) {
		render_vehicles(frm);		
	},
	team: function(frm) {
		render_team_members(frm);
	},
	billing_address: function(frm) {
		erpnext.utils.get_address_display(frm, "billing_address", "billing_address_display");
	}, 
	service_address: function(frm) {
		erpnext.utils.get_address_display(frm, "service_address", "service_address_display");
	},
	billing_address_same_as_service: function(frm) {
		if (frm.doc.billing_address_same_as_service) frm.set_value("billing_address", "");
	}
	// contact_person: function(frm) {
	// 	if(!frm.doc.contact_person) {
	// 		cur_frm.set_value("customer", undefined);
	// 	} else {
	// 		frappe.db.get_value("Contact", frm.doc.contact_person, "customer", function(r){
	// 			if (r) {
	// 				cur_frm.set_value("customer", r.customer);
	// 				cur_frm.refresh_fields();
	// 			} else if (frm.doc.contact_person) { //Display error message only if a contact is selected.
	// 				frappe.msgprint("No customer linked with this contact.");
	// 			}
	// 		});
	// 		erpnext.utils.get_contact_details(frm);
	// 	}
	// }
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
			args: {
				"team_name": frm.doc.team, 
				"day_of_week": moment(cur_frm.doc.starts_on).format("dddd") 
			},
			callback: function(r) {
				//console.log(r);
				$(frm.fields_dict['team_details_html'].wrapper)
				 .html(frappe.render_template("team_details", {"team_name": frm.doc.team, "team_members": r.message}));	
			}
		});
	}
}

function fetch_and_set_linked_fields(frm) {
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
	frappe.db.get_value(
		"Address",
		{ "customer":frm.doc.customer, "address_type":"Service" }, 
		"name", 
		function(r) {
			if (r) {
				frm.set_value("service_address", r.name);	
			}
		}
	);
	frappe.db.get_value(
		"Contact",
		{ "customer":frm.doc.customer, "is_primary_contact": 1 }, 
		"name", 
		function(r) {
			if (r) {
				frm.set_value("contact_person", r.name);	
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

function quick_entry_customer() {
	frappe._from_link = this;

	mnt.quick_entry("Customer", 
	function(){}, 
	{ 
		"customer_name": this.$input.val(),
		"customer_group": "All Customer Groups",
		"customer_type": "Individual",
		"territory": "All Territories"
	});
}

function quick_entry_service_address() {
	frappe._from_link = this;
	mnt.quick_entry("Address", 
	function(){}, 
	{ 
		"address_title":  this.$input.val() || (cur_frm.doc.customer),
		"address_type": "Billing",
		"customer": cur_frm.doc.customer
	});
}

function quick_entry_billing_address() {
	frappe._from_link = this;

	mnt.quick_entry("Address", 
	function(){}, 
	{ 
		"address_title": this.$input.val() || (cur_frm.doc.customer),
		"address_type": "Billing",
		"customer": cur_frm.doc.customer
	});
}

function quick_entry_vehicle() {
	frappe._from_link = this;
	mnt.quick_entry("Vehicle", 
	function(){}, 
	{ 
		"make": this.$input.val().split(" ")[0],
		"model": this.$input.val().split(" ")[1],
		"rn_customer": cur_frm.doc.customer,
		"fuel_type": "Petrol",
		"uom": "Litre"
	});
}

function quick_entry_contact() {
	frappe._from_link = this;
	mnt.quick_entry("Contact", 
	function(){}, 
	{ 
		"first_name": this.$input.val().split(" ")[0],
		"last_name": this.$input.val().split(" ")[1] || "",
		"customer": cur_frm.doc.customer,
	});
}

function clear_fields_on_customer_change() {
	console.log("Clearing");
	cur_frm.set_value("contact_person", "");
	cur_frm.set_value("contact_display", "");
	cur_frm.set_value("bill_to", "");
	cur_frm.set_value("contact_phone", "");
	cur_frm.set_value("contact_email", "");
	cur_frm.set_value("service_address", "");
	cur_frm.set_value("billing_address", "");
}