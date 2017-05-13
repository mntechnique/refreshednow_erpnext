import frappe
from frappe import _
import json
import calendar
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

    response = requests.request("GET", sms_settings.sms_gateway_url, params=querystring)
    #response = frappe._dict({"text": "SMS Gateway Invoked"})

    log_sms(sms_settings.sms_sender_name, mobile_no,message,response)
    return response.text

def fire_confirmation_sms(service):
    sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms");
    
    if sms_block != 1:
        # message = get_msg(service, "confirmation")
        # status_msg = ""

        try:
            #status_msg = send_sms(service.contact_phone, message)
            status_msg = send_service_sms(service, "confirmation")
        except Exception as e:
            status_msg = "SMS was not sent to '{0}'. <hr> {1}".format(service.contact_phone, e)
            frappe.msgprint(status_msg)

def fire_cancellation_sms(service):
    sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms");

    if sms_block != 1:
        # message = get_msg(service, "cancellation")
        # status_msg = ""

        try:
            #status_msg = send_sms(service.contact_phone, message)
            status_msg = send_service_sms(service, "cancellation")
        except Exception as e:
            status_msg = "SMS was not sent to '{0}'. <hr> {1}".format(service.contact_phone, e)
            frappe.msgprint(status_msg)    

def log_sms(sms_sender_name, mobile_no, message, response, purpose):
    note = frappe.new_doc("Note")
    note.title = "SMS Log ({0}) - {1} {2}".format(purpose.title(), frappe.utils.nowdate(), frappe.utils.nowtime())
    note.public = 1
    note.content = "<ul><li>Sender name: '{0}'</li><li>Mobile Number:'{1}'</li><li>Message: '{2}'</li><li>Response: '{3}'</li></ul>".format(sms_sender_name, mobile_no,message,response) #"Sending message to {0} <hr> {1}".format(contact_phone or "Contact Phone", sms_message or "Message Content")
    note.save()
    frappe.db.commit()

def fire_reminder_sms():
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
        
        for service in services:
            sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms")
            if sms_block != 1:
                #msg = get_msg(service, "reminder")
                #send_sms(service.contact_phone, msg)
                send_service_sms(service, "reminder")
                frappe.db.set_value("RN Scheduled Service", service.name, "sms_checkbox", 1)
                frappe.db.commit()


def get_msg(service, msg_type):
    on_day = frappe.utils.data.date_diff(frappe.utils.data.format_datetime(service.starts_on,"EEEE MM dd"), datetime.date.today())

    if on_day == 0:
        day_string = "today"
    elif on_day == 1:
        day_string = "tomorrow"
    else:
        day_string = ""

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

    cancellation_msg = """According to your request, service for {service_type} on {on_time} has been cancelled. Thank you for contacting Refreshed Car Care.
    """.format(
        on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
        service_type=service.service_type
        )

    msg_dict = {"reminder":reminder_msg,"confirmation":confirmation_msg,"cancellation":cancellation_msg}
    return msg_dict[msg_type]


def send_service_sms(service, purpose):
    import requests
    
    for x in xrange(1,10):
        print ("service:", service, "purpose:", purpose)

    message = get_msg(service, purpose)

    sms_settings = frappe.get_doc("SMS Settings")
    querystring = {}

    for p in sms_settings.parameters:
        querystring.update({p.parameter:p.value})

    querystring.update({
        "sendername":sms_settings.sms_sender_name,
        sms_settings.receiver_parameter:service.contact_phone,
        sms_settings.message_parameter:message
    })

    # response = requests.request("GET", sms_settings.sms_gateway_url, params=querystring)
    response = frappe._dict({"text": "SMS Gateway Invoked"})

    for x in xrange(1,10):
        print ("sender:", sms_settings.sms_sender_name, ", mobile:", service.contact_phone, ", message", message, ", response:", response, ", purpose:", purpose)

    log_sms(sms_settings.sms_sender_name, service.contact_phone, message, response, purpose)

    return response.text
