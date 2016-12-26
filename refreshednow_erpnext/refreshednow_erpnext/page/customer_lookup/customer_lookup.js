frappe.pages['customer-lookup'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Customer Lookup',
		single_column: true
	});

	//Append search textbox and button
	var content = null;
	content = page.wrapper.find(".page-content");
	console.log(content);
	var input_html= '<div class="input-group"> <input id="txt-lookup" type="text" class="form-control" placeholder="Search for caller number..."> <span class="input-group-btn"> <button id="btn-lookup" class="btn btn-secondary" type="button">Search!</button> </span> </div> <div class="clearfix"></div>'
	content.append(input_html);

	//Wireup events to search textbox and button
	var btn = content.find('#btn-lookup');
	var txt = content.find('#txt-lookup');
	btn.click(function() {
		frappe.call({
			method: "refreshednow_erpnext.ccc_api.get_caller_number",
			args: {
				caller_number: $(txt).val()
			},
			freeze: true,
			freeze_message: __("Looking up caller number..."),
			callback: function(r) {
				page.wrapper.find("#rn-ccc").remove();
				content.append(frappe.render_template("caller_information", {"caller_info": r.message}));

				lookup_call_lead(content);
				lookup_call_customer(content);
			}
		});
	});

	//Handle enter.
	$(document).keypress(function(e) {
		if (e.which == 13) {
			btn.click();			
		}
	});
}

function lookup_call_lead(content){
	var txt = content.find('#txt-lookup');
	var create_btn = content.find('#btn-create-lead');
	create_btn.click(function(r){
		frappe.call({
			method:"refreshednow_erpnext.ccc_api.create_lead",
			args:{
				caller_number: $(txt).val()
			},
			freeze: true,
			freeze_message: __("Looking up caller number..."),
			callback: function(r){
				console.log(r.message);
				var raw_url = window.location.origin;
				console.log(r.message);
				var str = "/desk#Form/Lead/"+r.message;
				var url = raw_url + str;
				window.location = url;
			}
		});

	});
}


function lookup_call_customer(content){
	var txt = content.find('#txt-lookup');
	var create_btn = content.find('#btn-create-customer');
	create_btn.click(function(r){
		frappe.prompt([
			{'fieldname': 'customer', 'fieldtype': 'Link', 'options':'Customer','label':'Customer'}
		],
		function(values){
			create_customer(values.customer, $(txt).val() )
		},
		'Select Customer',
		'Select'
		)
	});
}

function create_customer(customer_name, caller_number){
	frappe.call({
			method:"refreshednow_erpnext.ccc_api.create_contact",
			args:{
				caller_number: caller_number,
				customer_name: customer_name
			},
			callback: function(r){
				console.log(r.message);
				var raw_url = window.location.origin;
				var str = "/desk#Form/Contact/"+r.message;
				var url = raw_url + str;
				//var win = window.open(url);
				window.location = url;
			}
		});
}