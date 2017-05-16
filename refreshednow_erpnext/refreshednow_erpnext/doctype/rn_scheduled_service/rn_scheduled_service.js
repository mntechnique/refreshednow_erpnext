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

        // frm.add_custom_button(__("Add Contact with New Customer"), function() {
        //     new_contact_dialog(true)
        // }, __("Add Contact"));

        // frm.add_custom_button(__("Add Contact with existing Customer"), function() {
        //     new_contact_dialog(false)
        // }, __("Add Contact"));

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
        // cur_frm.set_query("customer", function() {
        //     return {
        //         "query": "refreshednow_erpnext.api.customer_query"
        //     };
        // });
       /* cur_frm.set_query("contact_person", function() {
            return {
                "query": "refreshednow_erpnext.api.contact_query",
            };
        });*/
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
                "query": "refreshednow_erpnext.api.get_address",
                "filters": {
                    "customer": frm.doc.customer,
                    "address_type": "Billing"
                }
            };
        });
        cur_frm.set_query("service_address", function() {
            return {
                "query": "refreshednow_erpnext.api.get_address",
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

        // console.log("Pre RS From", frm.doc.starts_on);
        // console.log("Pre RS To", frm.doc.ends_on);

        render_timeslot(frm);

        //frm.fields_dict.customer.new_doc = quick_entry_customer;
        frm.fields_dict.service_address.new_doc = quick_entry_service_address;
        frm.fields_dict.billing_address.new_doc = quick_entry_billing_address;
        frm.fields_dict.vehicle.new_doc = quick_entry_vehicle;
        frm.fields_dict.contact_person.new_doc = new_contact_dialog; //quick_entry_contact;
    },
    customer: function(frm) {
        if (frm.doc.customer) {
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
    },
    contact_person: function(frm) {
        clear_fields_on_contactperson_change();
    //  if(!frm.doc.contact_person) {
    //      cur_frm.set_value("customer", undefined);
    //  } else {
    //      frappe.db.get_value("Contact", frm.doc.contact_person, "customer", function(r){
    //          if (r) {
    //              cur_frm.set_value("customer", r.customer);
    //              cur_frm.refresh_fields();
    //          } else if (frm.doc.contact_person) { //Display error message only if a contact is selected.
    //              frappe.msgprint("No customer linked with this contact.");
    //          }
    //      });
    //      erpnext.utils.get_contact_details(frm);
    //  }
      /*  var customer = frappe.get_all("Dynamic Link",filters={"parent":frm.doc.contact_person},fields=["*"])
        frm.set_value("customer",customer[0].link_name)*/
      /*  if (frm.doc.contact_person) {
        frappe.call({
            method: "refreshednow_erpnext.api.set_customer",
            args: {
                "contact_person": frm.doc.contact_person,
            },
            callback: function(r) {
                if(r){
                    frm.set_value("customer",r.link_n);
                }
            }
        });
    }*/
        // cust = frappe.db.get_value("Dynamic Link", filters={"parent":frm.doc.contact_person}, fieldname="link_name",function(r){
        //     if(r){
        //         frm.set_value("customer",r.link_name);
        //         frm.set_df_property("customer", "read_only",1);
        //     }
        // });

        // frappe.db.get_value(
        //     "Contact",
        //     frm.doc.contact_person,
        //     "phone",
        //     function(r) {
        //         if (r) {
        //             frm.set_value("contact_phone", r.phone);
        //         }else {
        //         new_contact_dialog(frm);
        //         }
        //     }
        // );
        if(frm.doc.contact_person != ""){
            frappe.call({
                method: "refreshednow_erpnext.api.get_contact_info",
                args: {
                    contact_name: frm.doc.contact_person
                },
                callback: function(r) {
                    if (r || r.message) {
                        console.log("Setting values", r);
                        cur_frm.set_value("customer", r.message.customer);
                        cur_frm.set_value("rn_unsubscribe_sms", r.message.sms_check);
                        var phone = r.message.phone.replace(" ", "");
                        cur_frm.set_value("contact_phone", phone);
                        if (r.message.address) {
                            cur_frm.set_value("billing_address", r.message.address[0].parent);
                            cur_frm.set_value("service_address", r.message.address[0].parent);
                        }
                        cur_frm.set_value("vehicle_count", 1);
                    }
                }
            });
        }    
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
            args: {
                "team_name": frm.doc.team,
                "day_of_week": moment(cur_frm.doc.starts_on).format("dddd")
            },
            callback: function(r) {
                $(frm.fields_dict['team_details_html'].wrapper)
                 .html(frappe.render_template("team_details", {"team_name": frm.doc.team, "team_members": r.message}));
            }
        });
    }
}


// function  new_contact_dialog(frm) {
//     var dialog = new frappe.ui.Dialog({
//         title: __("Quick Customer Entry"),
//         fields: [
//             {fieldtype: "Link", fieldname: "customer", options: "Customer", label: __("Customer")},
//             {fieldtype: "Data", fieldname: "contact_person", label: __("Contact")},
//             {fieldtype: "Data", fieldname: "mobile_no", label: __("Mobile Number")},
//             {fieldtype: "Data", fieldname: "phone", label: __("Phone Number")}
//         ]
//     });

//     dialog.set_primary_action(__("Save"), function() {
//         var btn = this;
//         var values = dialog.get_values();
//         frappe.call({
//             doc: cur_frm.doc,
//             method: "refreshednow_erpnext.api.add_contact_to_customer",
//             args: {
//                 "values": values
//             },
//             callback: function(r) {
//                 dialog.clear(); dialog.hide();
//             }
//         })
//     });
// }

// function fetch_and_set_linked_fields(frm) {
//     frappe.db.get_value(
//         "Address",
//         { "customer":frm.doc.customer, "address_type":"Billing", "is_primary_address":true },
//         "name",
//         function(r) {
//             if (r) {
//                 console.log(r);
//                 frm.set_value("billing_address", r.name);
//             }
//         }
//     );
//     frappe.db.get_value(
//         "Address",
//         { "customer":frm.doc.customer, "address_type":"Service" },
//         "name",
//         function(r) {
//             if (r) {
//                 console.log(r);
//                 frm.set_value("service_address", r.name);
//             }
//         }
//     );
//     frappe.db.get_value(
//         "Contact",
//         { "customer":frm.doc.customer, "is_primary_contact": 1 },
//         "name",
//         function(r) {
//             if (r) {
//                 frm.set_value("contact_person", r.name);
//             }
//         }
//     );
// }

function render_timeslot(frm) {
    var starts_on = moment(frm.doc.starts_on).format("h:mm a");
    var ends_on = moment(frm.doc.ends_on).format("h:mm a");
    var timeslot = moment(frm.doc.starts_on).format("DD MMM Y") + ", " + starts_on + " - " + ends_on;

    var timeslot_html = '<div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Time Slot</label> </div> <div class="control-input-wrapper"> <div class="control-input-static"> <div class="link-field ui-front" style="position: relative;">' + timeslot + '</div> </div> </div> </div>';

    $(frm.fields_dict['timeslot_html'].wrapper)
                .html(timeslot_html);
}

// function quick_entry_customer() {
//     frappe._from_link = this;

//     mnt.quick_entry("Customer",
//     function(){},
//     {
//         "customer_name": this.$input.val(),
//         "customer_group": "All Customer Groups",
//         "customer_type": "Lead",
//         "territory": "All Territories"
//     });
// }

function quick_entry_service_address() {
    frappe._from_link = this;
    mnt.quick_entry("Address",
    function(){},
    {
        "address_title":  this.$input.val() || (cur_frm.doc.customer),
        "address_type": "Billing",
        "links": [{"link_doctype": "Customer", "link_name": cur_frm.doc.customer}]
    });
}

function quick_entry_billing_address() {
    frappe._from_link = this;

    mnt.quick_entry("Address",
    function(){},
    {
        "address_title": this.$input.val() || (cur_frm.doc.customer),
        "address_type": "Billing",
        "links": [{"link_doctype": "Customer", "link_name": cur_frm.doc.customer}]
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


function clear_fields_on_contactperson_change() {
    cur_frm.set_value("customer", "");
    cur_frm.set_value("bill_to", "");
    cur_frm.set_value("contact_phone", "");
    cur_frm.set_value("contact_email", "");
    cur_frm.set_value("service_address", "");
    cur_frm.set_value("billing_address", "");
    cur_frm.set_value("vehicle_count", "");
}

function new_contact_dialog() {
    var frm = cur_frm;

    var contact_person_value = frm.fields_dict["contact_person"].$input.val();

    var dialog = new frappe.ui.Dialog({
        title: __("New Contact"),
        fields: [
            {fieldtype: "Link", fieldname: "customer", label:__("Customer"), options: "Customer", reqd: 1},
            {fieldtype: "Data", fieldname: "contact_person", label: __("New Contact Name"), reqd: 1},
            {fieldtype: "Data", fieldname: "phone", label: __("Contact Number")}
        ]
    });

    if (isNaN(contact_person_value)) {
        dialog.set_value("contact_person", contact_person_value);
    } else {
        dialog.set_value("phone", contact_person_value);
    }

    dialog.get_field("customer").new_doc = function() { 
        frappe.msgprint("No need to click here. Just type in the name in the Customer field and the dialog will handle the rest.");
    };

    dialog.set_primary_action(__("Save"), function() {
        var btn = this;
        var values = dialog.get_values();
        frappe.call({
            doc: frm.doc,
            method: "add_contact_to_customer",
            args: {
                "values": values
            },
            callback: function(r) {
                cur_frm.set_value("contact_person", r.message);
                dialog.clear(); dialog.hide();
            }
        })
    });
    dialog.show();
}