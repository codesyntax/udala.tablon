from DateTime import DateTime
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from udala.tablon.annotations.document import get_documents
from udala.tablon.annotations.file import get_file
from udala.tablon.annotations.resolve import resolve_plone_uid
from udala.tablon.subscriber import get_publication_accreditation
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


@implementer(IPublishTraverse)
class TablonGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
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

    def reply(self):  # noqa: C901
        if len(self.params) == 1:
            doc_id = self._get_doc_id
            document = get_documents(doc_id)

            if document:
                plone_uid = resolve_plone_uid(document, self.request)
                if not plone_uid:
                    raise NotFound(self.context, "", self.request)

                plone_document = api.content.get(UID=plone_uid)
                if plone_document is not None:
                    adapter = getMultiAdapter(
                        (plone_document, self.request), ISerializeToJson
                    )
                    return adapter()

        elif len(self.params) == 2:
            doc_id = self._get_doc_id
            documents = get_documents(doc_id)

            file_id = self._get_file_id
            file = get_file(file_id)

            if documents and file:
                file_uid = resolve_plone_uid(file, self.request)

                if file_uid is None:
                    raise NotFound(self.context, "", self.request)

                file_object = api.content.get(UID=file_uid)
                if file_object is not None:
                    adapter = getMultiAdapter(
                        (file_object, self.request), ISerializeToJson
                    )

                    return adapter()

        elif len(self.params) == 3 and self.params[2] == "get_external_accreditation":
            file_id = self._get_file_id
            file = get_file(file_id)

            file_uid = resolve_plone_uid(file, self.request)

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
                get_publication_accreditation(file_object)

                return {"status": "ok"}

        raise NotFound(self.context, "", self.request)


class TablonExpiredGet(Service):
    def reply(self):

        date = self.request.get("date", None)
        date = DateTime() if date is None else DateTime(date, fmt="international")

        # Query "all" languages so we don't miss documents if the requested
        # language happens to lack a translation. The serializer automatically
        # embeds all available translations for a given Shared UID.
        brains = api.content.find(
            portal_type="DocumentoTablon",
            expires={
                "query": (date.earliestTime(), date.latestTime()),
                "range": "min:max",
            },
        )

        result = []
        seen_uids = set()

        from udala.tablon.annotations.document import get_document_by_uid_and_lang

        for brain in brains:
            obj = brain.getObject()

            # The serializer groups all translations under one Shared UID.
            # To avoid returning duplicate JSON objects when multiple translations
            # of the same document expire on the same day, we deduplicate by Shared UID.
            shared_uid = get_document_by_uid_and_lang(obj.UID(), obj.Language())
            if not shared_uid:
                continue

            if shared_uid in seen_uids:
                continue

            seen_uids.add(shared_uid)

            adapter = getMultiAdapter((obj, self.request), ISerializeToJson)

            item = adapter()
            result.append(item)

        return result
