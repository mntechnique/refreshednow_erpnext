// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('RN Scheduled Service', {
	refresh: function(frm) {
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
					"address_type": "Shipping"
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
	},
	customer: function(frm) {
		fetch_and_set_addresses(frm);		
	},
	vehicle: function(frm) {
		render_vehicles(frm);		
	}
});

function render_vehicles(frm) {
	$(frm.fields_dict['vehicle_details_html'].wrapper)
				.html("<div class='text-muted text-center' style='padding-top:5%;'>Please select a vehicle.</div>");

	if (frm.doc.vehicle) {
		frappe.model.with_doc("Vehicle", frm.doc.vehicle, function(vehicle_name) {
			var vehicle = frappe.model.get_doc("Vehicle", vehicle_name);
			$(frm.fields_dict['vehicle_details_html'].wrapper)
				.html(frappe.render_template("customer_vehicle", {"customer_vehicle": [vehicle]}));
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