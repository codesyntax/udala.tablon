# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from logging import getLogger
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_text
from udala.tablon import _
from udala.tablon.ws_utils import post_document_to_izenpe

import requests
import socket


def accreditation(object):
    """
    Helper method to get the accreditation for file
    with the given extension and url and expiration date
    """
    log = getLogger(__name__)
    date = object.expires.toZone("UTC").ISO8601()
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
            object.url(accredited_url)
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
    pkcs_12_file_contents_b64 = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.pkcs12_file_content_b64"
    )
    pkcs_12_file_pass = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.pkcs12_file_password"
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

        log = getLogger(__name__)
        log.info(data.status_code)
        log.info(data.text)
        return 0, None, ""

    except requests.exceptions.Timeout:
        log = getLogger(__name__)
        log.info("Timeout when accessing %s", endpointurl)
        return 0, None, ""


def get_publication_accreditation(object):
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
        from logging import getLogger

        log = getLogger(__name__)
        log.info(e)
        our_message = "Errorea ziurtagiria lortzean: "
        send_mail(our_message + message, object)
        return

    if result == 1:
        # putils.addPortalMessage(_("Accreditation correct"), type="info")
        our_message = "Ziurtagiri zuzena: "
        send_mail(our_message + message, object)

    else:
        # putils.addPortalMessage(
        #     _(
        #         "An error occurred getting the accreditation. Try again with"
        #         " the menu option: %(errorcode)s"
        #     )
        #     % {"errorcode": result},
        #     type="warning",
        # )
        our_message = "Errorea ziurtagiria lortzean: "
        send_mail(our_message + message, object)


def send_mail(message, object):
    email = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.admin_email"
    )
    mailhost = api.portal.get_tool("MailHost")
    portal = api.portal.get()
    messageText = "Izenperekin konexioaren emaitza: %s. Dokumentua:%s" % (
        message,
        object.absolute_url(),
    )
    mailhost.send(
        messageText,
        mto=email,
        mfrom=api.portal.get_registry_record("plone.email_from_address"),
        subject="Izenpe emaitza",
    )
