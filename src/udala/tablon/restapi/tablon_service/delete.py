# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from udala.tablon.utils import delete_document
from udala.tablon.utils import get_documents
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


@implementer(IPublishTraverse)
class TablonDelete(Service):
    def __init__(self, context, request):
        super(TablonDelete, self).__init__(context, request)
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

        eu_uid = document.get("eu", None)
        es_uid = document.get("es", None)
        for uid in [eu_uid, es_uid]:
            if uid is not None:
                real_document = api.content.get(UID=uid)
                if real_document is not None:
                    api.content.delete(real_document)

        result = delete_document(doc_id)

        if result:
            return self.reply_no_content()

        raise NotFound(self.context, "", self.request)
