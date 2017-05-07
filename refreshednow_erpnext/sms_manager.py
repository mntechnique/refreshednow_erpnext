import frappe
from frappe import _
import json
import calendar
#from datetime import date, datetime, timedelta
from frappe.desk.reportview import get_match_cond
import json, pdfkit, os
from frappe.utils.pdf import get_pdf

import datetime
from dateutil import tz



@frappe.whitelist()
def send_sms(mobile_no, message):
    import requests

    sms_settings = frappe.get_doc("SMS Settings")

    querystring = {}

    for p in sms_settings.parameters:
        querystring.update({p.parameter:p.value})

    querystring.update({
        "sendername":sms_settings.sms_sender_name,
        sms_settings.receiver_parameter:mobile_no,
        sms_settings.message_parameter:message
    })

    #print sms_settings.sms_gateway_url, querystring
    # response = requests.request("GET", sms_settings.sms_gateway_url, params=querystring)
    response = frappe._dict({"text": "SMS Gateway Invoked"})

    log_sms(sms_sender_name, mobile_no,message,response)
    return response.text

def fire_confirmation_sms(service):
    sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms");
    print "sms", sms_block
    if not sms_block:
        get_msg(service, "confirmation_msg")
        #sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d 'at' H:mm a")
        #sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(starts_on, "ha").lower()
        status_msg = ""

        try:
            status_msg = send_sms(service.contact_phone, service.sms_message)
        except Exception as e:
            status_msg = "SMS was not sent to '{0}'. <hr> {1}".format(service.contact_phone, e)

def fire_cancellation_sms(service):
    sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms");
    print "sms", sms_block
    if not sms_block:
        get_msg(service, "cancellation_msg")
        #sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d 'at' H:mm a")
        #sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(starts_on, "ha").lower()
        status_msg = ""

        try:
            status_msg = send_sms(service.contact_phone, service.sms_message)
        except Exception as e:
            status_msg = "SMS was not sent to '{0}'. <hr> {1}".format(service.contact_phone, e)


def log_sms(sms_sender_name, mobile_no, message,response):
    for x in xrange(1,10):
        print "inside log_sms", sms_sender_name, mobile_no, message, response
        
    note = frappe.new_doc("Note")
    note.title = "SMS Log (Confirmation) - "+ frappe.utils.nowdate() + frappe.utils.nowtime()
    note.public = 1
    note.content = "<ul><li>Sender name: '{0}'</li><li>Mobile Number:'{1}'</li><li>Message: '{2}'</li><li>Response: '{3}'</li></ul>".format(sms_sender_name, mobile_no,message,response) #"Sending message to {0} <hr> {1}".format(contact_phone or "Contact Phone", sms_message or "Message Content")
    note.save()
    frappe.db.commit()



def fire_reminder_sms():

    # get_msg(service, service_name)
    # sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms")
    # print "sms", sms_block
    # if not sms_block:

    nowtime_utc = frappe.utils.datetime.datetime.utcnow()
    nowtime_utc = nowtime_utc.replace(tzinfo=tz.gettz("UTC"))
    nowtime_ak = nowtime_utc.astimezone(tz.gettz("Asia/Kolkata"))

    #Comparison times are adjusted for SF time.
    if nowtime_ak.hour in [20,21,22]:
        tomorrow = frappe.utils.data.add_to_date(frappe.utils.today(), days=1)
        services = frappe.db.sql("""SELECT * FROM `tabRN Scheduled Service`
                        WHERE date(starts_on) = '{starts_on_date}'
                        AND docstatus = 1
                        AND sms_checkbox != 1""".format(
                            starts_on_date=tomorrow
                        ), as_dict=1)
        get_msg(services, "reminder_msg")
        for service in services:
            sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms")
            if not sms_block:
                msg = get_msg(service, "tomorrow")
                send_sms(service.contact_phone, msg)
                frappe.db.set_value("RN Scheduled Service", service.name, "sms_checkbox", 1)
                frappe.db.commit()


def get_msg(service, msg_type):
    on_day= frappe.utils.data.date_diff(frappe.utils.data.format_datetime(service.starts_on,"EEEE MM dd"), datetime.date.today())

    if on_day == 1:
        day_string = "tomorrow"
    else:
        day_string = "today"

    reminder_msg = """We look forward to refreshing your car {on_day}, {on_time} using {service_type}.
     Thanks for using Refreshed Car Care.""".format(
        on_day= day_string,
        on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
        service_type=service.service_type
    )
    confirmation_msg = """Thank you for contacting Refreshed Car Care. We have taken your booking for a {service_type} on {on_time}.
    """.format(
         on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
        service_type=service.service_type
        )

    confirmation_msg = """Thank you for contacting Refreshed Car Care. We have taken your booking for a {service_type} on {on_time}.
    """.format(
         on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
        service_type=service.service_type
        )

    msg_dict = {"reminder_msg":reminder_msg,"confirmation_msg":confirmation_msg}
    return msg_dict[msg_type]


