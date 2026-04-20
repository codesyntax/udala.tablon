# Phase 5: Test Suite Revival & Expansion - Detailed Implementation Plan

## 1. Goal
Repair the currently broken test suite (where `setUp` crashes due to `NoneType` errors from the old subscribers) and expand the coverage to explicitly verify the new dynamic, sequential, and monolingual-friendly Shared UID architecture introduced in Phases 1-4.

## 2. Fixing the Global `setUp()` Logic
Across `test_restapi.py`, `test_views.py`, and the utility tests, the `setUp()` method creates an `eu` Tablon, an `es` Tablon, links them, and then creates documents. 
*   **The Fix:** Once Phase 2 (Safe Subscribers) is implemented, the existing `setUp()` will naturally stop crashing because the `IObjectAddedEvent` will no longer blindly attempt to fetch a non-existent `"es"` translation.
*   **Refactoring Setup:** We will adjust the test setups to cleanly separate "Monolingual" setups (where PAM translations are not linked) from "Multilingual" setups (where documents are created in `eu`, then `es`, and then explicitly linked via `ITranslationManager`).

## 3. Rewriting Unit Tests for Storage (`test_document_annotation_utils.py` & `test_file_annotation_utils.py`)
As defined in Phase 1, the legacy storage tests must be completely rewritten to target the new dynamic dictionary structure.
*   **`test_register_single_language_document`**: Verify `register_documents(uid, "eu")` creates `{'translations': {'eu': uid}, 'files': []}`.
*   **`test_append_translation_to_existing_document`**: Verify passing a `shared_uid` updates the `translations` dict to hold multiple languages.
*   **`test_file_deduplication`**: Verify passing overlapping file arrays correctly uses `set()` to deduplicate the `files` array.
*   **`test_get_document_by_uid_and_lang_safe_handling`**: Verify `None` or missing language keys are handled gracefully without crashing.

## 4. Creating Integration Tests for Subscribers (`test_subscriber_register_*.py`)
These files are currently empty boilerplate. We will add full integration tests to verify the Zope events:
*   **`test_subscriber_on_add_monolingual`**: Create a document. Assert it gets a Shared UID in annotations under its own language.
*   **`test_subscriber_on_add_multilingual_translation`**: Create an EU document. Use PAM to translate it into ES. Assert the ES document correctly inherits the EU document's Shared UID instead of minting a new one.
*   **`test_subscriber_on_modify_translation_link`**: Create EU doc and ES doc independently (they get distinct Shared UIDs). Link them manually using `ITranslationManager`. Fire `IObjectModifiedEvent`. Assert their UIDs are merged into a single Shared UID in the annotations.

## 5. Updating REST API & View Tests (`test_restapi.py`, `test_views.py`)
*   **`test_restapi.py` adjustments:**
    *   Update `test_post_document_*` payloads to match the new dynamic serializer outputs (e.g., verifying that missing translations don't cause 500 errors and missing `origin_department_{lang}` keys are handled properly).
    *   **New Test: `test_get_document_monolingual`**: Create a document without translations. Fetch it via `@tablon/SHARED_UID`. Assert 200 OK and that it returns the base language's data without crashing.
    *   **New Test: `test_get_document_language_fallback`**: Fetch an EU document while simulating a request with `Accept-Language: fr`. Assert it safely falls back to the EU data instead of returning 404.
*   **`test_views.py` adjustments:**
    *   Verify `FileDownloadView` successfully traverses `/@tablon/doc_shared_uid/file_shared_uid` using the new `resolve_plone_uid` helper, returning the correct binary blob for the requested language.

## 6. Execution Order
Phase 5 will be executed incrementally alongside the other phases. 
1. Write the tests for Phase 1 alongside Phase 1 code.
2. Write the subscriber integration tests alongside Phase 2.
3. Fix the REST API and View tests alongside Phases 3 & 4. 
4. Run the full test suite (`make test`) and achieve 100% passing status.