# Phase 6: Generic API Signature for `@tablon` POST - Implementation Plan

## 1. Goal
Refactor the `/plone/@tablon` POST endpoint (`src/udala/tablon/restapi/tablon_service/post.py`) to support true dynamic multilingualism. Replace the rigid, hardcoded `_eu` and `_es` fields with a generic nested `translations` dictionary that seamlessly scales to any number of languages or monolingual setups.

## 2. API Signature Contract Change

**Old (Flat) Signature:**
```json
{
  "record_number": "1234",
  "date_start": "2023-10-25T10:00:00",
  "date_end": "2023-11-25T10:00:00",
  "origin": "external",
  "origin_department_eu": "Udaltzaingoa",
  "origin_department_es": "Policía",
  "description_eu": "Iragarkia",
  "description_es": "Anuncio",
  "origin_details_eu": "Details EU",
  "origin_details_es": "Details ES",
  "publication_url_eu": "http://eu",
  "publication_url_es": "http://es",
  "documents": [
    {
      "language": null, 
      "name_eu": "Fitxategia.pdf",
      "name_es": "Archivo.pdf",
      "filename": "file.pdf",
      "contents": "base64..."
    }
  ]
}
```

**New (Nested/Generic) Signature:**
```json
{
  "record_number": "1234",
  "date_start": "2023-10-25T10:00:00",
  "date_end": "2023-11-25T10:00:00",
  "origin": "external",
  "translations": {
    "eu": {
      "origin_department": "Udaltzaingoa",
      "description": "Iragarkia",
      "origin_details": "Details EU",
      "publication_url": "http://eu"
    },
    "es": {
      "origin_department": "Policía",
      "description": "Anuncio",
      "origin_details": "Details ES",
      "publication_url": "http://es"
    }
  },
  "documents": [
    {
      "language": null,
      "filename": "file.pdf",
      "contents": "base64...",
      "titles": {
        "eu": "Fitxategia.pdf",
        "es": "Archivo.pdf"
      }
    }
  ]
}
```

## 3. Refactoring `post.py` Validation Logic
1.  **Remove Hardcoded Validators:** Delete `_validate_origin_department_eu`, `_validate_origin_department_es`, `_validate_description_eu`, `_validate_name_eu`, etc.
2.  **Add `_validate_translations`:**
    *   Ensure the `translations` key exists and is a dictionary.
    *   Iterate through `translations.items()`. For each language block, ensure `origin_department`, `description`, `origin_details`, and (optionally valid) `publication_url` are present. Return specific errors like `"The field origin_department is mandatory for language 'eu'."`.
3.  **Update `_validate_documents`:**
    *   Ensure `titles` is a dictionary.
    *   Iterate through `titles.items()` ensuring a non-empty string title is provided for each language specified.

## 4. Refactoring `post.py` Creation Logic
1.  **Dynamic Base Selection:**
    *   Instead of `tablon_eu = self.get_tablon(lang="eu")`, query for the `Tablon` object using the site's default language, or simply find *any* `Tablon` object if the site is monolingual.
    *   Determine the "base" language from the payload. If the site's default language is in `payload['translations']`, use it as the base. Otherwise, use the first language key available.
2.  **Iterative Document Creation:**
    *   Pop the base language data from `translations`.
    *   Create `DocumentoTablon` in the `Tablon` container, applying the base data. Transition to "publish".
    *   For the remaining languages in `translations`, use `ITranslationManager.add_translation(lang)`. Get the translated object, apply the language-specific data, and transition to "publish".
    *   Store the created documents in a tracking dictionary: `created_docs = {'eu': doc_eu, 'es': doc_es}`.
    *   Call `register_documents(uid, lang, ...)` using the Phase 1/2 Shared UID architecture for each created document.
3.  **Iterative File Creation:**
    *   For each document in `payload['documents']`:
        *   If `file["language"]` is `None` (Bilingual/Multilingual):
            *   Create the base `AcreditedFile` inside the base `DocumentoTablon`. Set its `file` blob and `title` from `titles[base_lang]`.
            *   Iterate through the remaining `created_docs` languages. Use `ITranslationManager.add_translation(lang)`, set the blob, and set `title` from `titles[lang]`.
            *   Call `register_file(uid, lang, ...)` for each translation, sharing the UID.
        *   If `file["language"]` is specific (e.g., `"eu"`):
            *   Create the file *only* inside `created_docs["eu"]`. Set title from `titles["eu"]`. Register it.
4.  **Dynamic Response:**
    *   Return a dictionary of the generated URLs based purely on what was created in `created_docs` (e.g., `"url_eu": "...", "url_es": "..."`).

## 5. Test Suite Adaptation (`test_restapi.py`)
*   Rewrite all mock payloads (`correct_document_different_documents_per_language`, `correct_document_no_files`, etc.) to match the new nested JSON structure.
*   The tests will implicitly verify the new dynamic validator and creation loops.
