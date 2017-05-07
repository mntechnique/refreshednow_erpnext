# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate
#from frappe.utils.datetime import datetime
from frappe import _
#from refreshednow_erpnext.api import send_sms
from refreshednow_erpnext.sms_manager import fire_confirmation_sms
from refreshednow_erpnext.sms_manager import fire_cancellation_sms

class RNScheduledService(Document):
    def validate(self):
        self.validate_address()
        self.validate_reporting_time()
        self.check_overlap()
        # self.validate_schedule_days(allow_scheduling_after_days=0)
        self.check_no_of_vehicles()
        self.validate_team_availability()
        self.save_service_summary()

    def before_submit(self):
        if not self.sales_order:
            self.sales_order = self.create_sales_order()

    def on_submit(self):
        for x in xrange(1,10):
            print "Workflow State", self.workflow_state

        if self.workflow_state == "Stopped":
            fire_cancellation_sms()
            #pass
        elif self.workflow_state == "To Dispatch":
            fire_confirmation_sms(self)
            #pass
        else:
            pass

    def on_cancel(self):
        linked_so = frappe.db.get_value("Sales Order", filters={"rn_scheduled_service": self.name}, fieldname="name")

        if linked_so:
            oso = frappe.get_doc("Sales Order", linked_so)
            oso.cancel()
            frappe.db.commit()

    # def create_sales_invoice(self):
    #   defaults_temp = frappe.defaults.get_defaults()

    #   #Create a sales order if customer is selected.
    #   si = frappe.new_doc("Sales Order")
    #   si.transaction_date = self.starts_on

    #   if self.bill_to:
    #       si.rn_bill_to = self.bill_to

    #   si.company = defaults_temp.get("company")
    #   si.customer = self.customer


    #   #si.rn_service_time_slot = self.starts_on + ", " + self.starts_on + " - " + self.ends_on
    #   starts_on = frappe.utils.get_datetime(self.starts_on)
    #   ends_on = frappe.utils.get_datetime(self.ends_on)

    #   si.rn_service_time_slot = frappe.utils.datetime.datetime.strftime(starts_on, "%d-%m-%Y") + '<br>' + frappe.utils.datetime.datetime.strftime(starts_on, "%H:%M %p") + ' - ' + frappe.utils.datetime.datetime.strftime(ends_on, "%H:%M %p")

    #   if self.billing_address:
    #       si.customer_address = self.billing_address
    #   else:
    #       si.customer_address = self.service_address

    #   si.delivery_date = add_days(si.transaction_date, 10)
    #   si.currency = defaults_temp.get("currency")
    #   si.selling_price_list = defaults_temp.get("selling_price_list")
    #   si.rn_scheduled_service = self.name

    #   si.append("items", {
    #       "item_code": self.service_type,
    #       "qty": float(self.vehicle_count),
    #       "rate": frappe.db.get_value("Item Price", filters={"price_list":si.selling_price_list}, fieldname="price_list_rate"),
    #       "conversion_factor": 1.0
    #   })

    #   try:
    #       si.save()
    #       si.submit()
    #   except Exception, e:
    #       frappe.throw(_("Sales Invoice was not saved. <br/> %s" % (e)))
    #   else:
    #       return si.name

    def create_sales_order(self):
        defaults_temp = frappe.defaults.get_defaults()

        #Create a sales order if customer is selected.
        so = frappe.new_doc("Sales Order")
        so.transaction_date = self.starts_on

        so.company = defaults_temp.get("company")
        so.customer = self.customer
        so.delivery_date = add_days(so.transaction_date, 10)
        so.currency = defaults_temp.get("currency")
        so.selling_price_list = defaults_temp.get("selling_price_list")
        so.rn_scheduled_service = self.name
        starts_on = frappe.utils.get_datetime(self.starts_on)
        ends_on = frappe.utils.get_datetime(self.ends_on)
        so.rn_service_time_slot = frappe.utils.datetime.datetime.strftime(starts_on, "%d-%m-%Y") + '<br>' + frappe.utils.datetime.datetime.strftime(starts_on, "%H:%M %p") + ' - ' + frappe.utils.datetime.datetime.strftime(ends_on, "%H:%M %p")

        so.append("items", {
            "item_code": self.service_type,
            "qty": 1.0,
            "rate": frappe.db.get_value("Item Price", filters={"price_list":so.selling_price_list, "item_code": self.service_type}, fieldname="price_list_rate"),
            "conversion_factor": 1.0
        })

        try:
            so.save()
            so.submit()
            frappe.db.commit()
        except Exception, e:
            print "Exception", e
            frappe.throw(_("Sales Order was not saved. <br/> %s" % (e)))
        else:
            return so.name

    def check_overlap(self):
        existing_services = frappe.get_all("RN Scheduled Service", filters={"team": self.team, "docstatus" : 1}, fields=["name", "starts_on", "ends_on", "team"])
        for ss in existing_services:
            starts_on = frappe.utils.data.get_datetime(self.starts_on)
            ends_on = frappe.utils.data.get_datetime(self.ends_on)

            # if ss.team == self.team:
            #   frappe.throw("Team {0} is already scheduled for <a href='/desk#Form/{1}/{2}'>{2}</a>. Please select another team.".format(self.team, self.doctype, ss.name))

            if (starts_on > ss.starts_on and starts_on < ss.ends_on) or \
                (ends_on > ss.starts_on and ends_on < ss.ends_on) or \
                (starts_on <= ss.starts_on and ends_on >= ss.ends_on):
                frappe.throw("This service overlaps with {0}".format(ss.name))

    # def validate_schedule_days(self, allow_scheduling_after_days=1, allow_scheduling_after_hours=14):
    #     #days=1 ---> disallow scheduling of a service before tomorrow.
    #     allow_scheduling_after_date = frappe.utils.datetime.datetime.today() + frappe.utils.datetime.timedelta(days=allow_scheduling_after_days)

    #     if frappe.utils.getdate(self.starts_on) < allow_scheduling_after_date.date():
    #         frappe.throw("Services can be scheduled after {0}".format(frappe.utils.datetime.datetime.strftime(frappe.utils.data.getdate(allow_scheduling_after_date), "%d %b %Y")))

    def check_no_of_vehicles(self):
        if self.vehicle_count <= 0:
            frappe.throw("Must have at least one vehicle for a service.")

    def validate_team_availability(self):
        allocations = frappe.get_all("RN Team Day Employee", filters={"team": self.team, "day_of_week": frappe.utils.get_datetime(self.starts_on).strftime("%A")})
        if len(allocations) == 0:
            frappe.throw("No allocations for this team. <br> Please allocate members to this team using Team Allocation Tool.")

    def validate_address(self):
        if not self.billing_address_same_as_service and not self.billing_address:
            frappe.throw("Please set the billing address.")


    def validate_reporting_time(self):
        if self.reporting_time < self.starts_on or self.reporting_time>self.ends_on:
            frappe.throw("Reporting time must be within the selected service slot.")

    def save_service_summary(self):
        whatsapp_msg = """<div>
                            <div class="row">
                                <div class="col-sm-12">Booking Number:  {0}</div>
                                <div class="col-sm-12">Name:  {1}</div>
                                <div class="col-sm-12">Type:  {2}</div>
                                <div class="col-sm-12">Date:   {3}</div>
                                <div class="col-sm-12">Time:  {4}</div>
                                <div class="col-sm-12">Address:  {5}</div>
                                <div class="col-sm-12">Contact Number:  {6}</div>
                                <div class="col-sm-12">Comments:  {8}</div>
                                <div class="col-sm-12">Car:  {9}
                                <a href="https://api.whatsapp.com/send?phone={6}">Send Message</a></div>

                            </div>
                        </div>
                        """.format(self.name, self.customer, self.service_type, frappe.utils.data.format_datetime(self.reporting_time,"EEEE MMM d"), frappe.utils.data.format_datetime(self.reporting_time, "h:mm a").lower(),
                            self.service_address_display, self.contact_phone, "none", self.remarks, self.vehicle)

        self.service_details_summary = whatsapp_msg

