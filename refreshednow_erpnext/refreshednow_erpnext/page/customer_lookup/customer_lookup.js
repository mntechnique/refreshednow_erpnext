frappe.pages['customer-lookup'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Customer Lookup',
		single_column: true
	});

	var content = null;
	/*content = page.wrapper.find(".panel");
	console.log(content.find("#"))*/

	content = page.wrapper.find(".page-content");
	console.log(content);
	var input_html= '<div class="input-group"> <input id="txt-lookup" type="text" class="form-control" placeholder="Search for caller number..."> <span class="input-group-btn"> <button id="btn-lookup" class="btn btn-secondary" type="button">Search!</button> </span> </div> <div class="clearfix"></div>'
	content.append(input_html);
	var btn = content.find('#btn-lookup');
	var txt = content.find('#txt-lookup');
/*	console.log(btn);*/
	btn.click(function() {
		frappe.call({
			method: "refreshednow_erpnext.api.get_caller_number",
			args: {
				caller_number: $(txt).val()
			},
			freeze: true,
			freeze_message: __("Retrieving Caller Details"),
			callback: function(r) {
				content.append(frappe.render_template("caller_information", {"caller_info": r.message}));

				lookup_call_lead(content);
				lookup_call_customer(content);
			}
		});
	});
}

function lookup_call_lead(content){
	var txt = content.find('#txt-lookup');
	var create_btn = content.find('#btn-create-lead');
	create_btn.click(function(r){
		frappe.call({
			method:"refreshednow_erpnext.api.create_lead",
			args:{
				caller_number: $(txt).val()
			},
			freeze: true,
			freeze_message: __("Retrieving Caller Details"),
			callback: function(r){
				console.log(r.message);
				var raw_url = window.location.origin;
				var str = "/desk#Form/Lead/"+r.message;
				var url = raw_url + str;
				var win = window.open(url,'_blank');
				win.focus();
			}
		});

	});
}


function lookup_call_customer(content){
	var txt = content.find('#txt-lookup');
	var create_btn = content.find('#btn-create-customer');
	create_btn.click(function(r){
		/*var d = new frappe.ui.Dialog({
		'fields': [
		{'fieldname': 'customer', 'fieldtype': 'Link', 'options':'Customer','label':'Customer'}
		],
		primary_action: function(){
		d.hide();
		show_alert(d.get_values());
		},
		'primary_label': "Select"
		});
		d.show();*/
		frappe.prompt([
			{'fieldname': 'customer', 'fieldtype': 'Link', 'options':'Customer','label':'Customer'}
		],
		function(values){
			/*console.log(values)*/
			create_customer(values.customer, $(txt).val() )
		},
		'Select Customer',
		'Select'
		)

	});
}



function create_customer(customer_name , caller_number){
	frappe.call({
			method:"refreshednow_erpnext.api.create_contact",
			args:{
				caller_number: caller_number,
				customer_name: customer_name
			},
			freeze: true,
			freeze_message: __("Retrieving Caller Details"),
			callback: function(r){
				console.log(r.message);
				var raw_url = window.location.origin;
				var str = "/desk#Form/Contact/"+r.message;
				var url = raw_url + str;
				var win = window.open(url,'_blank');
				win.focus();
			}
		});
}