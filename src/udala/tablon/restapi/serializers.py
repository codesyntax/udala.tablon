# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from udala.tablon.content.documento_tablon import IDocumentoTablon
from udala.tablon.file_utils import get_file
from udala.tablon.utils import get_document_by_uid_and_lang
from udala.tablon.utils import get_documents
from udala.tablon.utils import get_file_contents
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


TRANSLATION_LANGUAGES = {"eu": "es", "es": "eu"}


@implementer(ISerializeToJson)
@adapter(IDocumentoTablon, Interface)
class DocumentoTablonSerializeToJson(SerializeToJson):
    def __call__(self, version=None, include_items=False):
        portal_url = api.portal.get().absolute_url()
        document_key = get_document_by_uid_and_lang(
            self.context.UID(), self.context.Language()
        )

        translated_context = self.context.getTranslation(
            TRANSLATION_LANGUAGES.get(self.context.Language())
        )

        document = get_documents(document_key)
        documents = []

        files_eu = document.get("files_eu")
        files_es = document.get("files_es")

        for file_id in set(files_eu + files_es):
            file_uid_data = get_file(file_id)
            file_uid = file_uid_data.get("eu", None)
            if file_uid is None:
                file_uid = file_uid_data.get("es", None)

            if file_uid is not None:
                file_object = api.content.get(UID=file_uid)
                if file_object is not None:
                    documents.append(
                        {
                            "@id": "{}/@tablon/{}/{}".format(
                                portal_url, document_key, file_id
                            ),
                            "uuid": file_id,
                            "title": file_object.Title(),
                            "filename": file_object.getField("file")
                            .get(file_object)
                            .filename,
                            "contents": file_object.getField("file")
                            .get(file_object)
                            .data.encode("base64"),
                            "izenpe_url": file_object.getUrl(),
                            "izenpe_content": get_file_contents(file_object.getUrl()),
                        }
                    )

        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            "@id": "{}/@tablon/{}".format(portal_url, document_key),
            "uuid": document_key,
            # "date_start": DateTime(self.context.EffectiveDate()).ISO8601(),
            # "date_end": DateTime(self.context.ExpirationDate()).ISO8601(),
            "date_start": self.context.effective().toZone("UTC").ISO8601(),
            "date_end": self.context.expires().toZone("UTC").ISO8601(),
            "origin": self.context.origin,
            "origin_department_{}".format(
                self.context.Language()
            ): self.context.origin_department,
            "origin_department_{}".format(
                translated_context.Language()
            ): translated_context.origin_department,
            "origin_details_{}".format(
                self.context.Language()
            ): self.context.origin_details,
            "origin_details_{}".format(
                translated_context.Language()
            ): translated_context.origin_details,
            "description_{}".format(self.context.Language()): self.context.description,
            "description_{}".format(
                translated_context.Language()
            ): translated_context.description,
            "publication_url_{}".format(
                translated_context.Language()
            ): self.context.publication_url,
            "publication_url_{}".format(
                self.context.Language()
            ): translated_context.publication_url,
            "documents": documents,
        }

        return result
