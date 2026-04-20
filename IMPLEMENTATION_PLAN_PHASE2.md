# Phase 2: Safe & Sequential Subscribers - Detailed Implementation Plan

## 1. Goal
To fix the fundamental crash happening at object creation (`AttributeError: 'NoneType' object has no attribute 'UID'`) and accurately support objects being translated incrementally over time (as happens in reality).

## 2. Changes to Subscribers (`src/udala/tablon/subscribers/register_document.py` & `register_file.py`)

*   **`register_document.handler(obj, event)`**
    *   **Current State:** It checks if PAM is installed, unconditionally fetches both "eu" and "es" translations, and tries to register them both. It crashes because the second translation doesn't exist yet.
    *   **New Logic (Creation):**
        1. Fetch the language of the newly created object: `language = obj.Language()`.
        2. If PAM is installed, check if this new object is *already* a translation of another object (this happens when creating a translation via PAM).
           * *Logic:* `manager = pamapi.get_translation_manager(obj)`
           * Get the translations dict: `translations = manager.get_translations()`
           * Remove the current language to find others: `other_langs = [l for l in translations if l != language]`
           * If `other_langs` exists, take the first one, fetch its Plone UID, and query the annotation storage for its `shared_uid` using `get_document_by_uid_and_lang(other_uid, other_lang)`.
        3. Call `register_documents(uid=obj.UID(), language=language, shared_uid=found_shared_uid_or_none)`.
        4. This completely avoids fetching a non-existent translation and neatly appends the new translation to the existing Shared UID if one exists.

*   **`register_file.handler(obj, event)`**
    *   **Current State:** Same issue as document, plus it attempts to register the parent documents unconditionally.
    *   **New Logic (Creation):**
        1. Apply the exact same safe PAM resolution logic as `register_document.py` to get the file's language and any existing `shared_file_uid`.
        2. Call `register_file(uid=obj.UID(), language=language, shared_uid=found_shared_file_uid_or_none)`.
        3. Get the parent document: `parent = aq_parent(obj)`.
        4. Call `register_documents(uid=parent.UID(), language=parent.Language(), file_uids=[file_shared_uid])`. The underlying logic from Phase 1 will safely deduplicate this file ID.

## 3. Handling Post-Creation Translations (`src/udala/tablon/subscribers/configure.zcml`)

When a user creates an English document, translates it to Spanish, they are linked *after* creation. PAM fires an `IObjectModifiedEvent` or an `IObjectTranslatedEvent`.

*   **Logic to Implement:** 
    *   In `configure.zcml`, we must also bind the handlers to `IObjectModifiedEvent`.
    *   Since our Phase 1 `register_documents` logic uses `set()` for files and safe `upserts` for translations, running the subscriber multiple times (on added and on modified) is 100% idempotent and safe. By simply registering the subscriber for `zope.lifecycleevent.interfaces.IObjectModifiedEvent` as well, it will automatically heal and merge translations when PAM links them.

## 4. Test Suite Strategy (`src/udala/tablon/tests/test_subscriber_register_document.py` & `test_subscriber_register_file.py`)

The current tests are empty boilerplate. We will add meaningful integration tests.

**Test Cases to Implement:**
1.  **`test_monolingual_creation`:**
    *   Create `DocumentoTablon` in a single language.
    *   Assert `get_document_by_uid_and_lang` returns a valid Shared UID.
2.  **`test_multilingual_sequential_creation`:**
    *   Create an EU `DocumentoTablon`. Capture its `shared_uid`.
    *   Create an ES `DocumentoTablon` and link it via `ITranslationManager.register_translation`.
    *   Trigger an `IObjectModifiedEvent` on both.
    *   Assert the ES document's Plone UID resolves to the *exact same* `shared_uid` as the EU document.
3.  **`test_file_registration_bubbles_to_document`:**
    *   Create a document. Create an `AcreditedFile` inside it.
    *   Assert the file gets a Shared UID.
    *   Assert the document's annotation array `data["files"]` contains the file's Shared UID.