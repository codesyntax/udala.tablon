# Documentation Plan for `udala.tablon`

This document details the strategy for writing the official documentation of the `udala.tablon` package, which has been scaffolded using the Diátaxis framework via `cookieplone documentation_starter` inside the `docs/` directory.

## 1. Documentation Structure (Diátaxis)

The documentation is divided into four key quadrants:

### A. Tutorials (`docs/docs/tutorials/`)
- **`getting-started.md`**: A step-by-step tutorial for a developer to install `udala.tablon` in their local Plone 6 environment, start the instance, and manually configure the necessary Plone Control Panel settings for the accreditation service.

### B. How-To Guides (`docs/docs/how-to-guides/`)
- **`manage-accreditations.md`**: Guide for site administrators on how to handle certificates, external accreditation connections, and caching.
- **`publish-via-api.md`**: Practical guide for third-party client developers demonstrating how to post a new announcement using the REST API using various tools like `curl` or Python's `requests`.

### C. Concepts / Explanation (`docs/docs/concepts/`)
- **`shared-uid-architecture.md`**: An explanation of the custom Shared UID storage layer. It will explain why the package decouples Plone UIDs from external service URLs to handle monolingual and dynamic multilingual (Plone App Multilingual) environments synchronously.
- **`content-types.md`**: Explaining the strict hierarchy (`Tablon` -> `DocumentoTablon` -> `AcreditedFile`) and the `origin` restricted vocabulary.

### D. Reference (`docs/docs/reference/`)
- **`api.md`**: The comprehensive REST API endpoint specification. (See Section 2 below).
- **`controlpanel.md`**: Reference of all the registry settings available in the Tablon control panel.

---

## 2. REST API Documentation Details (`docs/docs/reference/api.md`)

The REST API reference will be the most critical part of the documentation. It must clearly define the generic multilingual JSON signatures introduced in recent refactorings.

### Endpoints to Document:

#### 1. `POST /@tablon`
*   **Description**: Creates a new `DocumentoTablon` alongside its `AcreditedFile` children and orchestrates automatic translation generation using Plone App Multilingual.
*   **Payload Signature**: Explain the new nested `translations` dictionary and the `titles` dictionary inside the `documents` array.
*   **Response**: Returns the created URLs for all languages and the `shared_uid` (`201 Created`).

#### 2. `GET /@tablon/{shared_uid}`
*   **Description**: Retrieves the document information.
*   **Headers**: Document the importance of the `Accept-Language` header to dynamically resolve the correct language representation without causing 404s.
*   **Response**: Shows the dynamically generated JSON containing the active language properties and the appended array of files.

#### 3. `GET /@tablon/{shared_uid}/{file_shared_uid}`
*   **Description**: Retrieves a specific file's serialized JSON payload.
*   **Headers**: Respects `Accept-Language` for dynamic fallback.

#### 4. `DELETE /@tablon/{shared_uid}`
*   **Description**: Deletes the document matching the `shared_uid` and all of its PAM translations, plus the corresponding files. Removes the entry from the Zope Annotation dictionary.

#### 5. `GET /@tablon/{shared_uid}/{file_shared_uid}/get_external_accreditation`
*   **Description**: Asynchronous trigger endpoint to request the external accreditation of the file.
*   **Response**: `{"status": "ok"}`

#### 6. `GET /@tablon-expired?date=YYYY-MM-DD`
*   **Description**: Retrieves a list of documents that have expired on the given date.
*   **Query Parameters**: `date` (ISO international format). If omitted, defaults to today.

---

## 3. Execution Plan

1.  **Write Content**: Fill out the `.md` files in the `docs/docs/` directories matching the structure above.
2.  **API Schema**: Provide robust JSON examples in `api.md` (using the newly normalized data from `example_data.py`).
3.  **Build & Test**: Run `make html` or `make livehtml` inside the `docs/` folder to compile the Sphinx documentation and verify the layout and syntax.
4.  **Linters**: Run `make vale` to ensure technical writing standards and spelling are correct.
5.  **Commit**: Push the documentation scaffold and the completed markdown files.