# Phase 3: Traversal Routers (@tablon) - Detailed Implementation Plan

## 1. Goal
Make the `@tablon` endpoints (both REST API and Browser Views) completely language-agnostic so they do not depend on hardcoded "eu" or "es" keys, supporting both monolingual and fully dynamic multilingual setups natively.

## 2. Shared Safe-Resolution Helper (`src/udala/tablon/utils.py` or new helper location)

Instead of duplicating the language resolution logic in both routers, we'll create a helper method to safely resolve a `shared_uid` dictionary to a Plone object based on the current request context.

*   **Logic:** `resolve_plone_uid(annotation_dict, request)`
    1. Extract the `"translations"` dict from the annotation (this is the Phase 1 structure). If empty, return `None`.
    2. Identify the requested language. Use `request.get("LANGUAGE", api.portal.get_default_language())`. 
    3. Look up the Plone UID: `uid = translations.get(request_lang)`.
    4. If no exact match (e.g., viewing an untranslated item), fallback to the *first available* language in the dictionary to avoid returning a 404 unnecessarily: `uid = list(translations.values())[0] if translations else None`.
    5. Return the `uid`.

## 3. Changes to REST API Endpoint (`src/udala/tablon/restapi/tablon_service/get.py`)

*   **`TablonGet.reply()`**
    *   **Current State:** Extracts document via `document.get("eu")` unconditionally. Same for files via `file.get("eu")` falling back to `file.get("es")`.
    *   **New Logic:**
        1. Replace document lookup: `plone_doc_uid = resolve_plone_uid(document, self.request)`.
        2. Replace file lookup: `plone_file_uid = resolve_plone_uid(file, self.request)`.
        3. Eliminate all `if file_uid is None: file_uid = file.get("es")` boilerplate.
    *   **`TablonExpiredGet` Update:**
        *   Currently hardcodes `Language="eu"` in the catalog query.
        *   Change it to dynamically query the current language or remove the language constraint entirely depending on intended expired view behavior (often we only want to list the current language's expired items).

## 4. Changes to Browser View (`src/udala/tablon/views/file_download_view.py`)

*   **`FileDownloadView.__call__()`**
    *   **Current State:** Intercepts `/@tablon/doc_uid/file_uid` directly. Assumes `"eu"` and `"es"`.
    *   **New Logic:**
        1. Identical to the REST API refactoring: `plone_file_uid = resolve_plone_uid(file, self.request)`.
        2. Clean up the `NotFound` responses to be leaner.

## 5. Test Suite Strategy (`src/udala/tablon/tests/test_restapi.py`)

*   **Test Cases to Implement / Fix:**
    1.  **`test_tablon_router_monolingual`**
        *   Create document without PAM in "en" (or another non-standard language).
        *   Call `GET /@tablon/shared_uid`.
        *   Assert 200 OK and data is returned correctly.
    2.  **`test_tablon_router_fallback`**
        *   Create document in "eu".
        *   Simulate request with `LANGUAGE="fr"`.
        *   Assert the router successfully falls back to serving the "eu" JSON.
    3.  **`test_file_download_view_routing`**
        *   Assert the browser view correctly routes to the underlying binary blob using the language-agnostic logic.