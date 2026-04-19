from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from udala.tablon.annotations.document import get_document_by_uid_and_lang
from udala.tablon.annotations.document import get_documents
from udala.tablon.annotations.file import get_file
from udala.tablon.content.documento_tablon import IDocumentoTablon
from udala.tablon.interfaces import IUdalaTablonLayer
from udala.tablon.utils import get_file_contents
from udala.tablon.utils import is_pam_enabled
from zope.component import adapter
from zope.interface import implementer

import base64


@implementer(ISerializeToJson)
@adapter(IDocumentoTablon, IUdalaTablonLayer)
class DocumentoTablonSerializeToJson(SerializeToJson):
    def __call__(self, version=None, include_items=False):  # noqa: C901
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
                    file_translations = file_uid_data.get("translations", {})

                    if not file_translations:
                        continue

                    # Grab the base file for generic attributes (filename, contents)
                    base_lang = next(iter(file_translations))
                    base_file_uid = file_translations[base_lang]
                    base_file_obj = api.content.get(UID=base_file_uid)

                    if base_file_obj is not None:
                        file_data = {
                            "@id": f"{portal_url}/@tablon/{document_key}/{file_id}",
                            "uuid": file_id,
                            "titles": {},
                            "izenpe_urls": {},
                            "izenpe_contents": {},
                        }

                        if base_file_obj.file is not None:
                            file_data.update({
                                "filename": base_file_obj.file.filename,
                                "contents": base64.urlsafe_b64encode(
                                    base_file_obj.file.data
                                ).decode(),
                            })

                        for f_lang, f_uid in file_translations.items():
                            f_obj = api.content.get(UID=f_uid)
                            if f_obj:
                                file_data["titles"][f_lang] = f_obj.Title()
                                file_data["izenpe_urls"][f_lang] = f_obj.url
                                file_data["izenpe_contents"][f_lang] = (
                                    get_file_contents(f_obj.url)
                                )

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
            "translations": {},
            "documents": documents,
        }

        # Dynamically inject language-specific fields for all available translations
        for lang, translated_obj in translations.items():
            if translated_obj:
                result["translations"][lang] = {
                    "origin_department": translated_obj.origin_department,
                    "origin_details": translated_obj.origin_details,
                    "description": translated_obj.description,
                    "publication_url": translated_obj.publication_url,
                }

        return result
