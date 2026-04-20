# Phase 1: Dynamic Annotation API - Detailed Implementation Plan

## 1. Target Data Model (Strictly Enforced)

Because backward compatibility is not needed, all new and existing functions will strictly assume the new structure stored inside the `OOBTree` at `IAnnotations(portal)["udala.tablon.documento_tablon"]`.

**Document Model:**
```python
{
    "translations": {
        "eu": "plone_uid_1",
        "es": "plone_uid_2",
        "en": "plone_uid_3" 
    },
    "files": ["shared_file_uid_1", "shared_file_uid_2"],  # Single unified array
    "date": "2023-10-25T12:00:00Z"
}
```
*(The File model in `file_utils.py` uses the exact same `translations` dict, minus the `files` key).*

## 2. Changes to `src/udala/tablon/utils.py`

*   **`register_documents(uid: str, language: str, file_uids: list = None, shared_uid: str = None) -> str:`**
    *   **Goal:** Single-language, dynamic upsert.
    *   **Logic:**
        1. If `shared_uid` is provided, use it. Otherwise, look up an existing one using `get_document_by_uid_and_lang(uid, language)`.
        2. If neither exists, generate a new `shared_uid` (`uuid.uuid4().hex`).
        3. Fetch existing data for that `shared_uid` or initialize a new dict: `{'translations': {}, 'files': [], 'date': now()}`.
        4. Upsert the translation: `data["translations"][language] = uid`.
        5. Safely append files using set logic to avoid duplicates: `if file_uids: data["files"] = list(set(data["files"] + file_uids))`.
        6. Save back to the `OOBTree` and return the `shared_uid`.
    *   *Note:* All legacy parameters (`documento_eu`, `documento_es`, etc.) are removed.

*   **`get_document_by_uid_and_lang(uid, language)`**
    *   **Goal:** Fast and safe lookup mapping Plone to Shared UIDs.
    *   **Logic:** 
        1. Return `None` immediately if `uid` is falsy.
        2. Iterate over the annotations.
        3. Return the `shared_uid` if `uid == annotation_data.get("translations", {}).get(language)`.

*   **`get_documents(shared_uid)`**
    *   **Goal:** Fetch data safely.
    *   **Logic:** Simply return `annotations.get(shared_uid, None)`. No normalization needed since we dropped legacy support.

## 3. Changes to `src/udala/tablon/file_utils.py`

*   **`register_file(uid: str, language: str, shared_uid: str = None) -> str:`**
    *   **Goal:** Single-language file registration.
    *   **Logic:** Identical to `register_documents` (resolve ID, initialize `{translations: {}, date: now()}`, upsert `translations[language] = uid`, save, and return).

*   **`get_file_by_uid_and_lang(uid, language)`**
    *   **Goal:** Safe lookup matching the new structure.
    *   **Logic:** Identical to the document counterpart (ignore `None`, check `translations` dict).

## 4. Test Suite Strategy (`src/udala/tablon/tests/test_document_annotation_utils.py` & `test_file_annotation_utils.py`)

The current tests are tightly coupled to the old, simultaneous "eu/es" parameters. The test suite will be completely rewritten to cover the new single-step logic.

**Test Cases to Implement:**

1.  **`test_register_single_language_document`**
    *   Call `register_documents(uid="plone_1", language="eu")`.
    *   Assert a new UUID is generated.
    *   Assert the resulting structure is exactly `{'translations': {'eu': 'plone_1'}, 'files': [], 'date': ...}`.
2.  **`test_append_translation_to_existing_document`**
    *   Call `register_documents(uid="plone_1", language="eu")` (returns `shared_id`).
    *   Call `register_documents(uid="plone_2", language="es", shared_uid=shared_id)`.
    *   Assert the structure now holds both `{'eu': 'plone_1', 'es': 'plone_2'}` under `translations`.
3.  **`test_file_deduplication`**
    *   Call `register_documents` passing `file_uids=["file_1"]`.
    *   Call it again passing `file_uids=["file_1", "file_2"]`.
    *   Assert `data["files"]` is exactly `["file_1", "file_2"]` (no duplicates).
4.  **`test_get_document_by_uid_and_lang_safe_handling`**
    *   Assert passing `None` as the UID returns `None` immediately without crashing.
    *   Assert querying a valid UID but the wrong language (e.g., searching for "plone_1" in "es" instead of "eu") returns `None`.
    *   Assert valid queries return the correct Shared UUID.
5.  **`test_delete_document`**
    *   Verify the deletion function correctly wipes the key from the `OOBTree`.
6.  ***(Same 5 test cases duplicated in `test_file_annotation_utils.py` for `register_file`)*.**