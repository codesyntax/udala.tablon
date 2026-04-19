from plone import api
from plone.restapi.services import Service
from udala.tablon.annotations.document import delete_document
from udala.tablon.annotations.document import get_documents
from udala.tablon.annotations.file import delete_file
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


@implementer(IPublishTraverse)
class TablonDelete(Service):
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
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (doc id)")
        return self.params[0]

    def reply(self):
        if len(self.params) != 1:
            raise NotFound(self.context, "", self.request)

        doc_id = self._get_doc_id
        document = get_documents(doc_id)

        if document is None:
            raise NotFound(self.context, "", self.request)

        translations = document.get("translations", {})
        for uid in translations.values():
            if uid is not None:
                real_document = api.content.get(UID=uid)
                if real_document is not None:
                    api.content.delete(real_document)

        for file_id in document.get("files", []):
            delete_file(file_id)

        result = delete_document(doc_id)

        if result:
            return self.reply_no_content()

        raise NotFound(self.context, "", self.request)
