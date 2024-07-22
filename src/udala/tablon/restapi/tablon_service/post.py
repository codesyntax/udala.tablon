# -*- coding: utf-8 -*-
import base64
from datetime import datetime

import pytz
from plone import api
from plone.app.dexterity.behaviors.metadata import IPublication
from plone.app.multilingual.interfaces import ITranslationManager
from plone.namedfile.file import NamedBlobFile
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from udala.tablon import _
from udala.tablon.config import TASK_DEFAULT_DELAY
from udala.tablon.file_utils import register_file
from udala.tablon.tasks import schedule_browser_view_with_traversal
from udala.tablon.utils import register_documents
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides

OK = 1
ACCEPTED_ORIGIN_VALUES = ["external", "internal"]


def _validate_not_empty(value):
    if value is not None:
        if value.strip():
            return OK

    return False


def _validate_record_number(value):
    if _validate_not_empty(value) is OK:
        return OK

    return translate(_("The field record_number is mandatory"), context=getRequest())


def _validate_date(value):
    if _validate_not_empty(value) is OK:
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            return OK
        except ValueError:
            return False

    return False


def _validate_date_start(value):
    if _validate_date(value) is OK:
        return OK
    return translate(
        _("The format of field date_start is not correct"),
        context=getRequest(),
    )


def _validate_date_end(value):
    if _validate_date(value) is OK:
        return OK

    return translate(
        _("The format of field date_end is not correct"), context=getRequest()
    )


def _validate_origin(value):
    if _validate_not_empty(value) is OK:
        if value in ACCEPTED_ORIGIN_VALUES:
            return OK

    return translate(_("The field origin is mandatory"), context=getRequest())


def _validate_origin_department_eu(value):
    if _validate_not_empty(value) is OK:
        return OK

    return translate(
        _("The field origin_department_eu is mandatory"), context=getRequest()
    )


def _validate_origin_department_es(value):
    if _validate_not_empty(value) is OK:
        return OK

    return translate(
        _("The field origin_department_es is mandatory"), context=getRequest()
    )


def _validate_origin_details_eu(value):
    if _validate_not_empty(value) is OK:
        return OK

    return translate(_("The field origin_details_eu mandatory"), context=getRequest())


def _validate_origin_details_es(value):
    if _validate_not_empty(value) is OK:
        return OK

    return translate(
        _("The field origin_details_es is mandatory"), context=getRequest()
    )


def _validate_description_eu(value):
    if _validate_not_empty(value) is OK:
        return OK

    return translate(_("The field description_eu is mandatory"), context=getRequest())


def _validate_description_es(value):
    if _validate_not_empty(value) is OK:
        return OK

    return translate(_("The field description_es is mandatory"), context=getRequest())


def _validate_url(value):
    if value and value.strip().startswith("http"):
        return OK

    if not value:
        return OK

    return False


def _validate_publication_url_eu(value):
    if _validate_url(value) is OK:
        return OK

    return translate(
        _("The format of the field publication_url_eu is not correct"),
        context=getRequest(),
    )


def _validate_publication_url_es(value):
    if _validate_url(value) is OK:
        return OK

    return translate(
        _("The format of the field publication_url_es is not correct"),
        context=getRequest(),
    )


def _validate_document(value):
    if value:
        for field, function in DOCUMENT_FIELD_VALIDATION.items():
            validation_result = function(value.get(field))
            if validation_result != OK:
                return validation_result

        return OK

    return translate(
        _("The value of a single document is not correct"),
        context=getRequest(),
    )


def _validate_documents(value):
    if value:
        if isinstance(value, list):
            for item in value:
                result = _validate_document(item)
                if result is not OK:
                    return result
    return True


def _validate_name_es(value):
    if _validate_not_empty(value):
        return OK

    return translate(
        _("The value of name_es in a single document is mandatory"),
        context=getRequest(),
    )


def _validate_name_eu(value):
    if _validate_not_empty(value):
        return OK

    return translate(
        _("The value of name_eu in a single document is mandatory"),
        context=getRequest(),
    )


def _validate_contents(value):
    if _validate_not_empty(value):
        return OK

    return translate(
        _("The value of contents in a single document is mandatory"),
        context=getRequest(),
    )


def _validate_filename(value):
    if _validate_not_empty(value):
        return OK

    return translate(
        _("The value of filename in a single document is mandatory"),
        context=getRequest(),
    )


def set_dates(content_item, effective, expiration):
    """set the effective and expiration date to a dexterity content item"""
    publication = IPublication(content_item)
    publication.effective = effective
    publication.expires = expiration


def get_accreditation(document_id, file_id):
    """
    Request the accreditation of the file
    using an async process
    """

    schedule_browser_view_with_traversal.schedule(
        delay=TASK_DEFAULT_DELAY,
        kwargs=dict(
            view_name="@tablon",
            context_path="/".join(api.portal.get().getPhysicalPath()),
            site_path="/".join(api.portal.get().getPhysicalPath()),
            username=api.user.get_current().getId(),
            params={},
            traversal=f"{document_id}/{file_id}/get_external_accreditation",
        ),
    )
    return 1


DOCUMENT_FIELD_VALIDATION = {
    "name_es": _validate_name_es,
    "name_eu": _validate_name_eu,
    "contents": _validate_contents,
    "filename": _validate_filename,
}

FIELD_VALIDATION = {
    "record_number": _validate_record_number,
    "date_start": _validate_date_start,
    "date_end": _validate_date_end,
    "origin": _validate_origin,
    "origin_department_eu": _validate_origin_department_eu,
    "origin_department_es": _validate_origin_department_es,
    "origin_details_eu": _validate_origin_details_eu,
    "origin_details_es": _validate_origin_details_es,
    "description_eu": _validate_description_eu,
    "description_es": _validate_description_es,
    "publication_url_eu": _validate_publication_url_eu,
    "publication_url_es": _validate_publication_url_es,
    "documents": _validate_documents,
}


class TablonPost(Service):
    def get_tablon(self, lang="eu"):
        portal = api.portal.get()
        brains = api.content.find(context=portal, Language="eu", portal_type="Tablon")
        for brain in brains:
            return brain.getObject()
        return None

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)

        # validate data
        for field, function in FIELD_VALIDATION.items():
            validation_result = function(data.get(field))
            if validation_result != OK:
                self.request.response.setStatus(400)
                return {
                    "error": {
                        "type": "Invalid data error",
                        "message": translate(
                            validation_result,
                            context=self.request,
                        ),
                    }
                }

        # We first get the strings coming from the REST API request
        date_start = data.get("date_start")
        date_end = data.get("date_end")

        # We get UTC time zones, so when creating python datetime objects
        # it is not enough to do it using `fromisoformat` because that would
        # create naive datetimes, so we first create these naive datetime
        # objects and then replace its timezone using UTC
        date_start = datetime.fromisoformat(date_start)
        date_end = datetime.fromisoformat(date_end)

        date_start = date_start.replace(tzinfo=pytz.timezone("UTC"))
        date_end = date_end.replace(tzinfo=pytz.timezone("UTC"))

        # Now that we have proper datetimes with timezones, we change its
        # timezone to be that from Madrid
        date_start = date_start.astimezone(pytz.timezone("Europe/Madrid"))
        date_end = date_end.astimezone(pytz.timezone("Europe/Madrid"))

        tablon_eu = self.get_tablon(lang="eu")
        if not tablon_eu:
            self.request.response.setStatus(500)
            return {
                "error": {
                    "type": "Internal Server Error",
                    "message": translate(
                        "There was an error connection to the board",
                        context=self.request,
                    ),
                }
            }

        documento_eu = api.content.create(
            container=tablon_eu,
            type="DocumentoTablon",
            title=data.get("record_number"),
            origin=data.get("origin"),
            origin_department=data.get("origin_department_eu"),
            origin_details=data.get("origin_details_eu"),
            publication_url=data.get("publication_url_eu"),
            description=data.get("description_eu"),
            # effective=date_start,
            # expires=date_end,
        )
        set_dates(documento_eu, date_start, date_end)

        api.content.transition(obj=documento_eu, transition="publish")

        ITranslationManager(documento_eu).add_translation("es")
        documento_es = ITranslationManager(documento_eu).get_translation("es")

        documento_es.title = data.get("record_number")
        documento_es.origin = data.get("origin")
        documento_es.origin_department = data.get("origin_department_es")
        documento_es.origin_details = data.get("origin_details_es")
        documento_es.publication_url = data.get("publication_url_es")
        documento_es.description = data.get("description_es")
        documento_es.effectiveDate = date_start
        documento_es.expirationDate = date_end
        # documento_es = documento_eu.addTranslation(
        #     language="es",
        #     title=data.get("record_number"),
        #     origin=data.get("origin"),
        #     origin_department=data.get("origin_department_es"),
        #     origin_details=data.get("origin_details_es"),
        #     publication_url=data.get("publication_url_es"),
        #     description=data.get("description_es"),
        #     effectiveDate=date_start,
        #     expirationDate=date_end,
        # )

        api.content.transition(obj=documento_es, transition="publish")

        eu_files = []
        es_files = []

        for file in data.get("documents", []):
            file_language = file.get("language")
            if file_language is None:
                # The file is bilingual

                # Create EU
                file_eu = api.content.create(
                    container=documento_eu,
                    type="AcreditedFile",
                    title=file.get("name_eu"),
                    # effective=date_start,
                    # expires=date_end,
                )
                file_eu.file = NamedBlobFile(
                    base64.urlsafe_b64decode(file.get("contents")),
                    filename=file.get("filename"),
                )

                set_dates(file_eu, date_start, date_end)

                # Translate into ES
                ITranslationManager(file_eu).add_translation("es")
                file_es = ITranslationManager(file_eu).get_translation("es")
                file_es.title = file.get("name_es")

                file_eu_id = register_file(file_eu.UID(), file_es.UID())
                eu_files.append(file_eu_id)
                es_files.append(file_eu_id)

            elif file_language in ["eu"]:
                # EU
                file_eu = api.content.create(
                    container=documento_eu,
                    type="AcreditedFile",
                    title=file.get("name_eu"),
                    # effective=date_start,
                    # expires=date_end,
                )
                set_dates(file_eu, date_start, date_end)

                file_eu.file = NamedBlobFile(
                    base64.urlsafe_b64decode(file.get("contents")),
                    filename=file.get("filename"),
                )

                file_eu_id = register_file(file_eu.UID(), None)
                eu_files.append(file_eu_id)

            elif file_language in ["es"]:
                # ES
                file_es = api.content.create(
                    container=documento_es,
                    type="AcreditedFile",
                    title=file.get("name_es"),
                    # effective=date_start,
                    # expires=date_end,
                )
                set_dates(file_es, date_start, date_end)

                file_es.file = NamedBlobFile(
                    base64.urlsafe_b64decode(file.get("contents")),
                    filename=file.get("filename"),
                )

                file_es_id = register_file(None, file_es.UID())
                es_files.append(file_es_id)

        document_id = register_documents(
            documento_eu.UID(), documento_es.UID(), eu_files, es_files
        )

        for file_id in set(eu_files + es_files):
            get_accreditation(document_id, file_id)

        portal_url = api.portal.get().absolute_url()
        document_uri = f"{portal_url}/@tablon/{document_id}"
        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", document_uri)

        return {
            "@id": document_uri,
            "uuid": document_id,
            "url_eu": documento_eu.absolute_url(),
            "url_es": documento_es.absolute_url(),
        }
