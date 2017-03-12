frappe.listview_settings['RN Scheduled Service'] = {
	onload: function(listview) {
		listview.page.add_menu_item(__("Print Job Sheet"), function() {
			names=[];
			$.each(listview.get_checked_items(), function(key, value){
				names.push(value._name);
			});
			var w = window.open("/api/method/refreshednow_erpnext.api.print_job_sheet?"
							+"names="+encodeURIComponent(names)+"&lang=ENG");
	
			if(!w) {
				frappe.msgprint(__("Please enable pop-ups")); return;
			}
		});
	}
};