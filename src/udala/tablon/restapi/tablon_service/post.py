from datetime import datetime
from plone import api
from plone.app.dexterity.behaviors.metadata import IPublication
from plone.app.multilingual.interfaces import ITranslationManager
from plone.namedfile.file import NamedBlobFile
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from udala.tablon import _
from udala.tablon.cache import purge_urls
from udala.tablon.config import TASK_DEFAULT_DELAY
from udala.tablon.file_utils import get_file
from udala.tablon.file_utils import register_file
from udala.tablon.subscriber import get_publication_accreditation
from udala.tablon.utils import register_documents
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides

import base64
import pytz


try:
    from udala.tablon.tasks import schedule_browser_view_with_traversal

    TASK_QUEUE = True
except ImportError:
    TASK_QUEUE = False


OK = 1
ACCEPTED_ORIGIN_VALUES = ["external", "internal"]


def _validate_not_empty(value):
    if value is not None and value.strip():
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
    if _validate_not_empty(value) is OK and value in ACCEPTED_ORIGIN_VALUES:
        return OK

    return translate(_("The field origin is mandatory"), context=getRequest())


def _validate_url(value):
    if value and value.strip().startswith("http"):
        return OK

    if not value:
        return OK

    return False


def _validate_translations(value):
    if not value or not isinstance(value, dict):
        return translate(
            _("The field translations is mandatory and must be an object"),
            context=getRequest(),
        )

    for lang, data in value.items():
        if not isinstance(data, dict):
            return translate(
                _("The translation data for language must be an object"),
                context=getRequest(),
            )

        if _validate_not_empty(data.get("origin_department")) is not OK:
            return translate(
                _(f"The field origin_department is mandatory for language {lang}"),
                context=getRequest(),
            )

        if _validate_not_empty(data.get("origin_details")) is not OK:
            return translate(
                _(f"The field origin_details is mandatory for language {lang}"),
                context=getRequest(),
            )

        if _validate_not_empty(data.get("description")) is not OK:
            return translate(
                _(f"The field description is mandatory for language {lang}"),
                context=getRequest(),
            )

        pub_url = data.get("publication_url")
        if pub_url and _validate_url(pub_url) is not OK:
            return translate(
                _(
                    f"The format of the field publication_url is not correct for language {lang}"  # noqa: E501
                ),
                context=getRequest(),
            )

    return OK


def _validate_documents_payload(value):
    if value and isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                return translate(
                    _("The value of a single document is not correct"),
                    context=getRequest(),
                )

            if _validate_not_empty(item.get("contents")) is not OK:
                return translate(
                    _("The value of contents in a single document is mandatory"),
                    context=getRequest(),
                )

            if _validate_not_empty(item.get("filename")) is not OK:
                return translate(
                    _("The value of filename in a single document is mandatory"),
                    context=getRequest(),
                )

            titles = item.get("titles")
            if not titles or not isinstance(titles, dict):
                return translate(
                    _("The field titles in a single document is mandatory"),
                    context=getRequest(),
                )

            for lang, title in titles.items():
                if _validate_not_empty(title) is not OK:
                    return translate(
                        _(
                            f"The title in a single document is mandatory for language {lang}"  # noqa: E501
                        ),
                        context=getRequest(),
                    )
    return OK


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

    if TASK_QUEUE:
        schedule_browser_view_with_traversal.schedule(
            delay=TASK_DEFAULT_DELAY,
            kwargs={
                "view_name": "@tablon",
                "context_path": "/".join(api.portal.get().getPhysicalPath()),
                "site_path": "/".join(api.portal.get().getPhysicalPath()),
                "username": api.user.get_current().getId(),
                "params": {},
                "traversal": f"{document_id}/{file_id}/get_external_accreditation",
            },
        )
    else:
        alsoProvides(getRequest(), IDisableCSRFProtection)
        file_data = get_file(file_id)
        if file_data:
            from udala.tablon.utils import resolve_plone_uid

            file_uid = resolve_plone_uid(file_data, getRequest())
            if file_uid:
                file_object = api.content.get(UID=file_uid)
                if file_object is not None:
                    get_publication_accreditation(file_object)
    return 1


FIELD_VALIDATION = {
    "record_number": _validate_record_number,
    "date_start": _validate_date_start,
    "date_end": _validate_date_end,
    "origin": _validate_origin,
    "translations": _validate_translations,
    "documents": _validate_documents_payload,
}


class TablonPost(Service):
    def get_tablon(self, lang=None):
        portal = api.portal.get()
        query = {"portal_type": "Tablon"}
        if lang:
            query["Language"] = lang
        brains = api.content.find(context=portal, **query)
        for brain in brains:
            return brain.getObject()

        brains = api.content.find(context=portal, portal_type="Tablon")
        for brain in brains:
            return brain.getObject()

        return None

    def reply(self):  # noqa: C901
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

        date_start = datetime.fromisoformat(date_start)
        date_end = datetime.fromisoformat(date_end)

        date_start = date_start.replace(tzinfo=pytz.timezone("UTC"))
        date_end = date_end.replace(tzinfo=pytz.timezone("UTC"))

        date_start = date_start.astimezone(pytz.timezone("Europe/Madrid"))
        date_end = date_end.astimezone(pytz.timezone("Europe/Madrid"))

        translations_data = data.get("translations", {})
        languages = list(translations_data.keys())

        base_lang = api.portal.get_default_language()
        if base_lang not in languages and languages:
            base_lang = languages[0]

        tablon_base = self.get_tablon(lang=base_lang)
        if not tablon_base:
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

        created_docs = {}

        # Create base document
        base_trans_data = translations_data[base_lang]
        documento_base = api.content.create(
            container=tablon_base,
            type="DocumentoTablon",
            title=data.get("record_number"),
            origin=data.get("origin"),
            origin_department=base_trans_data.get("origin_department"),
            origin_details=base_trans_data.get("origin_details"),
            publication_url=base_trans_data.get("publication_url"),
            description=base_trans_data.get("description"),
        )
        set_dates(documento_base, date_start, date_end)
        documento_base.reindexObject()
        api.content.transition(obj=documento_base, transition="publish")
        created_docs[base_lang] = documento_base

        from udala.tablon.subscribers.utils import is_pam_enabled

        if is_pam_enabled(documento_base):
            for lang in languages:
                if lang == base_lang:
                    continue

                trans_data = translations_data[lang]
                ITranslationManager(documento_base).add_translation(lang)
                documento_trans = ITranslationManager(documento_base).get_translation(
                    lang
                )

                documento_trans.title = data.get("record_number")
                documento_trans.origin = data.get("origin")
                documento_trans.origin_department = trans_data.get("origin_department")
                documento_trans.origin_details = trans_data.get("origin_details")
                documento_trans.publication_url = trans_data.get("publication_url")
                documento_trans.description = trans_data.get("description")

                set_dates(documento_trans, date_start, date_end)
                documento_trans.reindexObject()
                api.content.transition(obj=documento_trans, transition="publish")

                created_docs[lang] = documento_trans

        file_shared_uids = []

        for file_data in data.get("documents", []):
            file_lang = file_data.get("language")
            titles = file_data.get("titles", {})

            file_shared_uid = None

            if file_lang is None:
                # Bilingual / Multilingual file
                base_file_created = False
                base_file_obj = None
                for lang, doc in created_docs.items():
                    title = titles.get(lang, file_data.get("filename"))

                    if not base_file_created:
                        file_obj = api.content.create(
                            container=doc,
                            type="AcreditedFile",
                            title=title,
                        )
                        file_obj.file = NamedBlobFile(
                            base64.urlsafe_b64decode(file_data.get("contents")),
                            filename=file_data.get("filename"),
                        )
                        set_dates(file_obj, date_start, date_end)
                        file_obj.reindexObject()
                        base_file_obj = file_obj
                        base_file_created = True
                    else:
                        if is_pam_enabled(base_file_obj):
                            ITranslationManager(base_file_obj).add_translation(lang)
                            file_obj = ITranslationManager(
                                base_file_obj
                            ).get_translation(lang)
                            file_obj.title = title
                            set_dates(file_obj, date_start, date_end)
                            file_obj.reindexObject()

                    file_shared_uid = register_file(
                        uid=file_obj.UID(), language=lang, shared_uid=file_shared_uid
                    )

                file_shared_uids.append(file_shared_uid)

            else:
                # Single language file
                doc = created_docs.get(file_lang)
                if doc:
                    title = titles.get(file_lang, file_data.get("filename"))
                    file_obj = api.content.create(
                        container=doc,
                        type="AcreditedFile",
                        title=title,
                    )
                    file_obj.file = NamedBlobFile(
                        base64.urlsafe_b64decode(file_data.get("contents")),
                        filename=file_data.get("filename"),
                    )
                    set_dates(file_obj, date_start, date_end)
                    file_obj.reindexObject()

                    f_uid = register_file(uid=file_obj.UID(), language=file_lang)
                    file_shared_uids.append(f_uid)

        document_shared_uid = None
        response_urls = {}
        tablons_to_purge = set()

        for lang, doc in created_docs.items():
            response_urls[f"url_{lang}"] = doc.absolute_url()
            document_shared_uid = register_documents(
                uid=doc.UID(),
                language=lang,
                file_uids=file_shared_uids,
                shared_uid=document_shared_uid,
            )
            tablons_to_purge.add(doc.__parent__.absolute_url())

        for file_id in set(file_shared_uids):
            get_accreditation(document_shared_uid, file_id)

        portal_url = api.portal.get().absolute_url()
        document_uri = f"{portal_url}/@tablon/{document_shared_uid}"
        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", document_uri)

        purge_urls(list(tablons_to_purge))

        result = {
            "@id": document_uri,
            "uuid": document_shared_uid,
        }
        result.update(response_urls)
        return result
