# -*- coding: utf-8 -*-
from udala.tablon.subscriber import getPublicationAccreditation
from DateTime import DateTime
from udala.tablon.file_utils import get_file
from udala.tablon.utils import (
    get_document_by_uid_and_lang,
    get_documents,
)
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zope.i18n import translate
from zope.interface import alsoProvides, implementer
from zope.publisher.interfaces import IPublishTraverse, NotFound
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter


@implementer(IPublishTraverse)
class TablonGet(Service):
    def __init__(self, context, request):
        super(TablonGet, self).__init__(context, request)
        self.params = []
        self.query = self.request.form.copy()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    @property
    def _get_doc_id(self):
        if len(self.params) not in [1, 2, 3]:
            raise Exception("Must supply exactly one parameter (doc id)")
        return self.params[0]

    @property
    def _get_file_id(self):
        if len(self.params) not in [1, 2, 3]:
            raise Exception("Must supply exactly one parameter (doc id)")
        return self.params[1]

    def reply(self):
        if len(self.params) == 1:

            doc_id = self._get_doc_id
            document = get_documents(doc_id)

            if document:
                eu_uid = document.get("eu")
                eu_document = api.content.get(UID=eu_uid)

                adapter = getMultiAdapter(
                    (eu_document, self.request), ISerializeToJson
                )

                return adapter()

        elif len(self.params) == 2:
            doc_id = self._get_doc_id
            documents = get_documents(doc_id)

            file_id = self._get_file_id
            file = get_file(file_id)

            if documents and file:
                file_uid = file.get("eu")
                if file_uid is None:
                    file_uid = file.get("es")

                if file_uid is None:
                    adapter = getMultiAdapter(
                        (eu_document, self.request), ISerializeToJson
                    )

                return adapter()

        elif (
            len(self.params) == 3
            and self.params[2] == "get_external_accreditation"
        ):
            file_id = self._get_file_id
            file = get_file(file_id)
            file_uid = file.get("eu")
            if file_uid is None:
                file_uid = file.get("es")

            if file_uid is None:
                self.request.response.setStatus(404)
                return {
                    "error": {
                        "type": "Not found",
                        "message": translate(
                            "The requested file does not exist",
                            context=self.request,
                        ),
                    }
                }

            file_object = api.content.get(UID=file_uid)
            if file_object is not None:
                alsoProvides(self.request, IDisableCSRFProtection)
                getPublicationAccreditation(file_object)

                return {"status": "ok"}

        raise NotFound(self.context, "", self.request)


class TablonExpiredGet(Service):
    def reply(self):
        date = self.request.get("date", None)
        if date is None:
            date = DateTime()
        else:
            date = DateTime(date, fmt="international")

        brains = api.content.find(
            Language="eu",
            portal_type="DocumentoTablon",
            expires={
                "query": (date.earliestTime(), date.latestTime()),
                "range": "min:max",
            },
        )

        result = []
        for brain in brains:
            adapter = getMultiAdapter(
                (brain.getObject(), self.request), ISerializeToJson
            )

            item = adapter()
            result.append(item)

        return result
