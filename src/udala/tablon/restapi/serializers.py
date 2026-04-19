from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from udala.tablon.annotations.document import get_document_by_uid_and_lang
from udala.tablon.annotations.document import get_documents
from udala.tablon.annotations.file import get_file
from udala.tablon.annotations.resolve import resolve_plone_uid
from udala.tablon.content.documento_tablon import IDocumentoTablon
from udala.tablon.interfaces import IUdalaTablonLayer
from udala.tablon.subscribers.utils import is_pam_enabled
from udala.tablon.utils import get_file_contents
from zope.component import adapter
from zope.interface import implementer

import base64


@implementer(ISerializeToJson)
@adapter(IDocumentoTablon, IUdalaTablonLayer)
class DocumentoTablonSerializeToJson(SerializeToJson):
    def __call__(self, version=None, include_items=False):
        portal_url = api.portal.get().absolute_url()
        document_key = get_document_by_uid_and_lang(
            self.context.UID(), self.context.Language()
        )

        translations = {}
        if is_pam_enabled(self.context):
            manager = ITranslationManager(self.context)
            translations = manager.get_translations()
        else:
            translations[self.context.Language()] = self.context

        document = get_documents(document_key)
        documents = []

        if document:
            files = document.get("files", [])

            for file_id in set(files):
                file_uid_data = get_file(file_id)
                if file_uid_data is not None:
                    file_uid = resolve_plone_uid(file_uid_data, self.request)

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
                                file_data.update({
                                    "filename": file_object.file.filename,
                                    "contents": base64.urlsafe_b64encode(
                                        file_object.file.data
                                    ).decode(),
                                })
                            documents.append(file_data)

        result = {
            "@id": f"{portal_url}/@tablon/{document_key}",
            "uuid": document_key,
            "date_start": self.context.effective.toZone("UTC").ISO8601()
            if hasattr(self.context.effective, "toZone")
            else self.context.effective().toZone("UTC").ISO8601(),
            "date_end": self.context.expires.toZone("UTC").ISO8601()
            if hasattr(self.context.expires, "toZone")
            else self.context.expires().toZone("UTC").ISO8601(),
            "origin": self.context.origin,
            "documents": documents,
        }

        # Dynamically inject language-specific fields for all available translations
        for lang, translated_obj in translations.items():
            if translated_obj:
                result[f"origin_department_{lang}"] = translated_obj.origin_department
                result[f"origin_details_{lang}"] = translated_obj.origin_details
                result[f"description_{lang}"] = translated_obj.description
                result[f"publication_url_{lang}"] = translated_obj.publication_url

        return result
