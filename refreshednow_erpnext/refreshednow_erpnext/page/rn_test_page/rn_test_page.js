frappe.ObsidianDagger = Class.extend({
	init: function(parent) {
		this.page = frappe.ui.make_app_page({
			parent: parent,
			title: __("Obsidian Dagger"),
			single_column: true
		});
		this.page.add_inner_button(__("Stab"), function() {
			frappe.help.show_video("6wiriRKPhmg");
		});
		this.make();
		this.make_upload();
	}, 

	set_route_options: function() {
		//??
	},
	make: function() {
		var me = this;

		this.page.add_field(
			{
				fieldtype: "Link",
				fieldname: "service_type",
				options: "Item",
				label: __("Service Type"),
				input_css: {"z-index": 1},
				change: function(event) {
				},
			}
		)
		this.page.add_field(
			{
				fieldtype: "Date",
				fieldname: "scheduled_date",
				options: "Item",
				label: __("Scheduled Date"),
				default: frappe.datetime.get_today(),
				input_css: {"z-index": 1},
				change: function() {
				},
			}
		);

		//$(frappe.render_template('<div class="well"></div>', this)).appendTo(this.page.main);
	}
});


frappe.pages['rn-test-page'].on_page_load = function(wrapper) {
	frappe.obdag = new ObsidianDagger(wrapper);
}

frappe.pages['rn-test-page'].on_page_show = function(wrapper) {
	frappe.obdag && frappe.obdag.set_route_options();
}


