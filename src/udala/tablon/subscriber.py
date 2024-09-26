# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from logging import getLogger
from plone import api
from Products.CMFPlone.utils import safe_text
from udala.tablon.ws_utils import post_document_to_izenpe

import requests


def accreditation(object):
    """
    Helper method to get the accreditation for file
    with the given extension and url and expiration date
    """
    log = getLogger(__name__)
    date = object.expires().toZone("UTC").ISO8601()
    # field = object.getField("file")
    # extension = field.getFilename(object).rsplit(".")[-1]
    field = object.file
    extension = field.filename.rsplit(".")[-1]
    url = object.absolute_url()

    if not url.startswith("http"):
        # We need to manipulate the URL because when calling from an
        # async process we are not getting the correct URL
        domain = api.portal.get_registry_record(
            "udala.tablon.udala_tablon_control_panel.domain"
        )
        portal_path = "/".join(api.portal.get().getPhysicalPath())[1:]
        url = url.replace(portal_path, domain)

    result, accredited_url, message = get_accreditation_for_url(
        url, object.Title(), extension, date, object.Language()
    )

    if result and accredited_url:
        if result == 1:
            object.url = accredited_url
            log.info("OK Izenpe: url: %s message: %s", url, message)
            return 1, message
        else:
            log.info("Error Izenpe: url: %s message: %s", url, message)
            return 0, message

    log.info("Error Izenpe: url: %s message: %s", url, message)
    return 0, message


def get_accreditation_for_url(url, title, f_extension, f_revision, language):
    """
    Send the document to the accreditation service and return the status,
    the url of the accreditation file
    and any other message that the service returns
    """
    log = getLogger(__name__)

    endpointurl = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.accrediterendpointurl"
    )

    try:

        data = post_document_to_izenpe(
            url=url,
            title=safe_text(title),
            revision_date=f_revision,
            extension=f_extension,
            language=language,
        )

        if data:
            return data.get("status"), data.get("url"), data.get("message")

        return 0, None, ""

    except requests.exceptions.Timeout:
        log.info("Timeout when accessing %s", endpointurl)
        return 0, None, ""


def get_publication_accreditation(object):
    """given a Plone object, get the accreditation for it"""
    log = getLogger(__name__)
    message = ""
    if object.expires is None:
        # No expiration date, try finding it in parent
        parent = aq_parent(object)
        if parent.expires is not None:
            object.expires = parent.expires
        else:
            return
    try:
        result, message = accreditation(object)
    except Exception as e:
        log.info(e)
        our_message = "Errorea ziurtagiria lortzean: "
        send_mail(our_message + message, object)
        return

    if result == 1:
        our_message = "Ziurtagiri zuzena: "
        send_mail(our_message + message, object)

    else:
        log.info(result)
        our_message = "Errorea ziurtagiria lortzean: "
        send_mail(our_message + message, object)


def send_mail(message, object):
    """send the given message by email to the admin"""
    email = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.admin_email"
    )
    mailhost = api.portal.get_tool("MailHost")

    message_text = "Izenperekin konexioaren emaitza: %s. Dokumentua:%s" % (
        message,
        object.absolute_url(),
    )
    mailhost.send(
        message_text,
        mto=email,
        mfrom=api.portal.get_registry_record("plone.email_from_address"),
        subject="Izenpe emaitza",
    )
