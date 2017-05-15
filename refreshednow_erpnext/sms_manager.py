import frappe
from frappe import _
import json
import calendar
from frappe.desk.reportview import get_match_cond
import json, pdfkit, os
from frappe.utils.pdf import get_pdf

import datetime
from dateutil import tz


def fire_confirmation_sms(service):
    sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms");
    
    if sms_block != 1:
        response, sms_msg = send_service_sms(service, "confirmation")
        log_service_sms("confirmation", service, sms_msg, response)

def fire_cancellation_sms(service):
    sms_block = frappe.db.get_value("Customer",filters={"name":service.customer},fieldname="rn_unsubscribe_sms");

    if sms_block != 1:
        response, sms_msg = send_service_sms(service, "cancellation")
        log_service_sms("cancellation", service, sms_msg, response)

# def log_sms(sms_sender_name, mobile_no, message, response, purpose):
#     note = frappe.new_doc("Note")
#     note.title = "SMS Log ({0}) - {1} {2}".format(purpose.title(), frappe.utils.nowdate(), frappe.utils.nowtime())
#     note.public = 1
#     note.content = "<ul><li>Sender name: '{0}'</li><li>Mobile Number:'{1}'</li><li>Message: '{2}'</li><li>Response: '{3}'</li></ul>".format(sms_sender_name, mobile_no,message,response) #"Sending message to {0} <hr> {1}".format(contact_phone or "Contact Phone", sms_message or "Message Content")
#     note.save()
#     frappe.db.commit()

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
                response, sms_msg = send_service_sms(service, "reminder")
                log_service_sms("reminder", service, sms_msg, response)

                if not "Error" in response:
                    frappe.db.set_value("RN Scheduled Service", service.name, "sms_checkbox", 1)
                    frappe.db.commit()


def get_msg(service, msg_type):
    on_day = frappe.utils.data.date_diff(frappe.utils.data.format_datetime(service.starts_on,"EEEE MM dd"), datetime.date.today())

    confirmation_msg = """Your {service_type} is confirmed for {on_time} ({service_no}). To cancel or reschedule, please call us at least 2 hour prior. Thanks, Refreshed Car Care.""".format(service_type=service.service_type,
                on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
                service_no=service.name)


    reminder_msg = """Reminder: Your {service_type} ({service_no}) is scheduled tomorrow at {on_time}. To cancel or reschedule, please call us at least 2 hour prior. Thanks, Refreshed Car Care.""".format(
        service_type=service.service_type,
        service_no=service.name,
        on_time=frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower()
    )
    
    cancellation_msg = """We have cancelled your {service_type} for {on_time} ({service_no}). To reschedule, please call us. Thanks, Refreshed Car Care.""".format(
        service_type=service.service_type,
        on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
        service_no=service.name
        )


    # reminder_msg = """We look forward to refreshing your car {on_day}, {on_time} using {service_type}.
    #  Thanks for using Refreshed Car Care.""".format(
    #     on_day= day_string,
    #     on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
    #     service_type=service.service_type
    # )
    # confirmation_msg = """Thank you for contacting Refreshed Car Care. We have taken your booking for a {service_type} on {on_time}.
    # """.format(
    #     on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
    #     service_type=service.service_type
    #     )

    # cancellation_msg = """According to your request, service for {service_type} on {on_time} has been cancelled. Thank you for contacting Refreshed Car Care.
    # """.format(
    #     on_time=frappe.utils.data.format_datetime(service.reporting_time,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.reporting_time, "h:mm a").lower(),
    #     service_type=service.service_type
    #     )

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

    #response = frappe._dict({"text": "SMS Gateway Invoked"})
    try:
        response = requests.request("GET", sms_settings.sms_gateway_url, params=querystring)
    except Exception as e:
        response = {"text": "Error: SMS was not sent to {0} <br> Reason: {1}".format(service.contact_phone, e.message)}

  #  log_sms(sms_settings.sms_sender_name, service.contact_phone, message, response, purpose)

    return response.get("text"), message

def log_service_sms(purpose, service, message, response):
    note = frappe.new_doc("Note")
    note.title = "SMS Log ({purpose}{error}) - {nowdate} {nowtime}".format(purpose=purpose.title(), 
            nowdate=frappe.utils.nowdate(), 
            nowtime=frappe.utils.nowtime(),
            error= ", Error" if "Error" in response else "")
    note.public = 1
    note.content = "<ul><li>Mobile Number:'{0}'</li><li>Message: '{1}'</li><li>Response: '{2}'</li></ul>".format(service.contact_phone, message, response)
    note.save()
    frappe.db.commit()