from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
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

import base64


TRANSLATION_LANGUAGES = {"eu": "es", "es": "eu"}


@implementer(ISerializeToJson)
@adapter(IDocumentoTablon, Interface)
class DocumentoTablonSerializeToJson(SerializeToJson):
    def __call__(self, version=None, include_items=False):
        portal_url = api.portal.get().absolute_url()
        document_key = get_document_by_uid_and_lang(
            self.context.UID(), self.context.Language()
        )

        translated_context = ITranslationManager(self.context).get_translation(
            TRANSLATION_LANGUAGES.get(self.context.Language())
        )

        document = get_documents(document_key)
        documents = []

        files_eu = document.get("files_eu")
        files_es = document.get("files_es")

        for file_id in set(files_eu + files_es):
            file_uid_data = get_file(file_id)
            if file_uid_data is not None:
                file_uid = file_uid_data.get("eu", None)
                if file_uid is None:
                    file_uid = file_uid_data.get("es", None)

                if file_uid is not None:
                    file_object = api.content.get(UID=file_uid)
                    if file_object is not None:
                        file_data = {
                            "@id": f"{portal_url}/@tablon/{document_key}/{file_id}",
                            "uuid": file_id,
                            "title": file_object.Title(),
                            "izenpe_url": file_object.url,
                            "izenpe_content": get_file_contents(file_object.url),
                        }
                        if file_object.file is not None:
                            file_data.update(
                                {
                                    "filename": file_object.file.filename,
                                    "contents": base64.urlsafe_b64encode(
                                        file_object.file.data
                                    ).decode(),
                                }
                            )
                        documents.append(file_data)

        language = self.context.Language()
        translated_language = translated_context.Language()

        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            "@id": f"{portal_url}/@tablon/{document_key}",
            "uuid": document_key,
            # "date_start": DateTime(self.context.EffectiveDate()).ISO8601(),
            # "date_end": DateTime(self.context.ExpirationDate()).ISO8601(),
            "date_start": self.context.effective().toZone("UTC").ISO8601(),
            "date_end": self.context.expires().toZone("UTC").ISO8601(),
            "origin": self.context.origin,
            f"origin_department_{language}": self.context.origin_department,
            f"origin_department_{translated_language}": translated_context.origin_department,
            f"origin_details_{language}": self.context.origin_details,
            f"origin_details_{translated_language}": translated_context.origin_details,
            f"description_{language}": self.context.description,
            f"description_{translated_language}": translated_context.description,
            f"publication_url_{language}": self.context.publication_url,
            f"publication_url_{translated_language}": translated_context.publication_url,
            "documents": documents,
        }

        return result
