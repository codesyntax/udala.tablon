# Phase 4: Bulletproof Serializers - Detailed Implementation Plan

## 1. Goal
Ensure the `@tablon` REST API serializers correctly output JSON representations of documents and files without crashing (`AttributeError`) when items are untranslated or deployed on monolingual sites. Stop hardcoding `eu`/`es` and use the dynamic structure introduced in Phase 1.

## 2. Changes to `DocumentoTablonSerializeToJson` (`src/udala/tablon/restapi/serializers.py`)

*   **Current State:** 
    It forces a translation lookup using a hardcoded `TRANSLATION_LANGUAGES = {"eu": "es", "es": "eu"}` dict. It then assumes `translated_context` is not `None` and injects `translated_context.origin_department`, crashing if untranslated. Finally, it uses the legacy `files_eu + files_es` array structure from annotations.

*   **New Logic:**
    1. Remove `TRANSLATION_LANGUAGES` entirely.
    2. Instead of finding a single "translated context", get *all* translations using PAM (if installed):
       ```python
       translations = {}
       if is_pam_enabled(self.context):
           manager = ITranslationManager(self.context)
           for lang, item in manager.get_translations().items():
               translations[lang] = item
       else:
           translations[self.context.Language()] = self.context
       ```
    3. Update the `document` lookup to use the Phase 1 structure:
       ```python
       files = document.get("files", [])
       ```
    4. When iterating over files, resolve their Shared UIDs using the `resolve_plone_uid(file_data, self.request)` helper built in Phase 3.
    5. Construct the JSON result dynamically based on the available translations:
       ```python
       result = {
           "@id": f"{portal_url}/@tablon/{document_key}",
           "uuid": document_key,
           "date_start": self.context.effective().toZone("UTC").ISO8601(),
           "date_end": self.context.expires().toZone("UTC").ISO8601(),
           "origin": self.context.origin,
           "documents": documents,
       }

       # Dynamically inject language-specific fields
       for lang, translated_obj in translations.items():
           result[f"origin_department_{lang}"] = translated_obj.origin_department
           result[f"origin_details_{lang}"] = translated_obj.origin_details
           result[f"description_{lang}"] = translated_obj.description
           result[f"publication_url_{lang}"] = translated_obj.publication_url
       ```
       *Note on API Contract:* If the frontend *strictly requires* keys like `origin_department_es` to be present even if null, the logic can be modified to pre-populate common languages (`eu`, `es`) with `None` and override them if the translation exists.

## 3. Test Suite Strategy (`src/udala/tablon/tests/test_restapi.py`)

The REST API test suite contains numerous tests (`test_post_document_...` etc.) that will need adjustment, particularly regarding the JSON payload structures and expected responses.

*   **Test Cases to Implement / Fix:**
    1.  **`test_serialize_monolingual_document`**
        *   Create an untranslated document.
        *   Call the serializer adapter directly or via a mock request.
        *   Assert the result contains `origin_department_{lang}` for the base language, and gracefully omits (or nulls) the missing languages without throwing an `AttributeError`.
    2.  **`test_serialize_multilingual_document`**
        *   Create a translated document (eu + es).
        *   Assert the resulting JSON contains populated `origin_department_eu` and `origin_department_es` correctly matching both objects.
    3.  **`test_serialize_document_with_files`**
        *   Create a document containing files.
        *   Assert `files` array is correctly serialized, including `izenpe_url` and base64 `contents` from the correct translated file blob.