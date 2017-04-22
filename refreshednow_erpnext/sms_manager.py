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
    log_sms(sms_sender_name, mobile_no,message,response)
    return response.text

def fire_confirmation_sms(service):

    sms_message = "Thank you for contacting Refreshed Car Care. "
    sms_message += "We have taken your booking for a "
    sms_message += service.service_type
    sms_message += " on "
    sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(starts_on, "h:mm a").lower()
    #sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d 'at' H:mm a")
    #sms_message += frappe.utils.data.format_datetime(starts_on,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(starts_on, "ha").lower()

    status_msg = ""

    try:
        status_msg = send_sms(service.contact_phone, service.sms_message)
    except Exception as e:
        status_msg = "SMS was not sent to '{0}'. <hr> {1}".format(service.contact_phone, e)


def log_sms(sms_sender_name, mobile_no,message,response):
    note = frappe.new_doc("Note")
    note.title = "SMS Log (Confirmation) - "+ frappe.utils.nowdate() + frappe.utils.nowtime()
    note.public = 1
    note.content = "<ul><li>Sender name: '{0}'</li><li>Mobile Number:'{1}'</li><li>Message: '{2}'</li><li>Response: '{3}'</li></ul>".format(sms_sender_name, mobile_no,message,response) #"Sending message to {0} <hr> {1}".format(contact_phone or "Contact Phone", sms_message or "Message Content")
    note.save()
    frappe.db.commit()



def fire_reminder_sms(service):

    # get_msg(service, service_name)

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
            msg = get_msg(service, "tomorrow")

            note_content = ""
            try:
                send_sms(service.contact_phone, msg)
                note_content = "Sent message to {0} on {1} <hr> {2} <hr> {3}".format(service.customer or "'No Cust'", service.contact_phone or "'Phone No'",  msg or "'Message'", service.name or "'Service Name'")
                frappe.db.set_value("RN Scheduled Service", service.name, "sms_checkbox", 1)
                frappe.db.commit()
            except Exception as e:
                note_content = "Unable to send message to {0} on {1} <hr> {2} <hr> {3} <hr> {4}".format(service.customer or "'No Cust'", service.contact_phone or "'Phone No'",  msg or "'Message'", service.name or "'Service Name'", ex)


            note = frappe.new_doc("Note")
            note.title = "SMS Log (Reminder) - "+ frappe.utils.nowdate() + frappe.utils.nowtime()
            note.public = 1
            note.content = note_content
            note.save()

            frappe.db.commit()


def get_msg(service, on_day):
    sms_message = """We look forward to refreshing your car {on_day}, {on_time} using {service_type}.
     Thanks for using Refreshed Car Care.""".format(
        on_day=on_day,
        on_time=frappe.utils.data.format_datetime(service.starts_on,"EEEE MMM d") + " at " + frappe.utils.data.format_datetime(service.starts_on, "h:mm a").lower(),
        service_type=service.service_type
    )
    return sms_message
