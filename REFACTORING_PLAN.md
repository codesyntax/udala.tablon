# Refactoring Plan: Udala Tablon Shared UIDs

## Objective
Make the Shared UID architecture (used to decouple physical Plone URLs/languages from external accreditation services via the `@tablon` endpoints) robust, crash-free, and fully compatible with both monolingual and multilingual (PAM) environments.

## Current Flaws Addressed
1. **Event Crashes (`IObjectAddedEvent`):** Subscribers currently crash trying to fetch non-existent translations at the exact millisecond of object creation.
2. **Hardcoded Languages:** The annotation storage (`files_eu`, `es_uid`) and `@tablon` traversal routers hardcode `"eu"` and `"es"`, causing failures on monolingual sites or sites using other languages.
3. **Missing Translation Merges:** When an item is translated *after* creation, there is no logic to merge the distinct Shared UIDs, breaking the single-URL requirement.
4. **Serializer Exceptions:** The REST API serializers crash (`AttributeError`) if they attempt to serialize an untranslated document.

---

## Execution Phases

### Phase 1: Dynamic Annotation API
**Files:** `src/udala/tablon/utils.py`, `src/udala/tablon/file_utils.py`
- Modify `register_documents()` and `register_file()` to accept a single object (`uid`, `language`) instead of hardcoded pairs.
- Store translations in a dynamic dictionary within the annotation: `{'translations': {'eu': 'uid1', 'en': 'uid2'}, 'files': ['shared_file_uid_1', ...]}`.
- Refactor lookup functions (`get_document_by_uid_and_lang`) to iterate through the dynamic `translations` map safely.

### Phase 2: Safe & Sequential Subscribers
**Files:** `src/udala/tablon/subscribers/register_document.py`, `src/udala/tablon/subscribers/register_file.py`, `src/udala/tablon/subscribers/configure.zcml`
- **Creation Hook:** Change `IObjectAddedEvent` to only register the newly created object in its own language. If PAM is enabled and the object is already a translation of an existing item, inherit the existing Shared UID. Otherwise, generate a new one.
- **Translation Hook:** Add an `IObjectModifiedEvent` or PAM-specific translation hook to merge Shared UIDs when two documents are linked as translations post-creation.

### Phase 3: Fix Traversal Routers (@tablon)
**Files:** `src/udala/tablon/restapi/tablon_service/get.py`, `src/udala/tablon/views/file_download_view.py`
- Remove hardcoded `get("eu")` fallbacks.
- When resolving a Shared UID to a Plone object, attempt to match the current request language. If that fails, safely fallback to the first available language in the Shared UID's `translations` dict to serve the JSON/File.

### Phase 4: Bulletproof Serializers
**Files:** `src/udala/tablon/restapi/serializers.py`
- Update `DocumentoTablonSerializeToJson` to handle `translated_context = None` gracefully.
- Do not crash when generating `origin_department_{translated_language}`; handle missing translations by omitting or nulling the fields safely.

### Phase 5: Test Suite Revival & Expansion
**Files:** `src/udala/tablon/tests/*`
- Fix the test `setUp()` which currently triggers the `NoneType` crash.
- **Monolingual Tests:** Create items without PAM, assert Shared UIDs are minted and `@tablon` endpoints resolve them.
- **Multilingual Tests:** Create an EU item, translate to ES, assert the ES item inherits the Shared UID. Assert `@tablon` returns merged JSON correctly.
