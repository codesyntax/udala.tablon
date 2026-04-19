# REST API Endpoint Reference

The `udala.tablon` package extends Plone 6's core REST API with a dedicated router at the `/@tablon` path. This endpoint provides dynamic, language-agnostic access to the Electronic Notice Board, utilizing the Shared UID architecture.

## 1. Create Document (POST `/@tablon`)

Creates a new `DocumentoTablon` and its associated `AcreditedFile` children. It orchestrates automatic translation generation if Plone App Multilingual is installed.

### Request Body

The JSON payload uses a dynamic `translations` dictionary, allowing it to scale to any number of languages or monolingual setups without rigid `_eu`/`_es` suffixes.

```json
{
  "record_number": "2024/001",
  "date_start": "2024-03-01T00:00:00",
  "date_end": "2024-03-31T23:59:59",
  "origin": "external",
  "translations": {
    "eu": {
        "origin_department": "Kultura Saila",
        "origin_details": "Udaletxea",
        "description": "Kultur egitarauaren diru-laguntzak",
        "publication_url": "https://www.donostia.eus"
    },
    "es": {
        "origin_department": "Departamento de Cultura",
        "origin_details": "Ayuntamiento",
        "description": "Subvenciones para programas culturales",
        "publication_url": "https://www.donostia.eus/es"
    }
  },
  "documents": [
    {
      "language": null,
      "filename": "deialdia_convocatoria.pdf",
      "contents": "JVBERi0xLjMKJc...",
      "titles": {
          "eu": "Deialdia",
          "es": "Convocatoria"
      }
    }
  ]
}
```

### Responses
- `201 Created`: Contains the generated `Shared UUID` and the absolute physical URLs to the new Plone items. The returned keys (for example, `url_eu`, `url_es`, `url_en`) will dynamically match the language block provided in the payload's `translations` dictionary.
- `400 Bad Request`: Validation errors (for example, missing fields in a specific language block).
- `500 Internal Server Error`: No `Tablon` container found in the system.

## 2. Get Document (GET `/@tablon/{shared_uid}`)

Retrieves the serialized JSON of the document corresponding to the `shared_uid`.

### Headers
- `Accept-Language`: The API natively parses HTTP language headers (for example, `eu,en;q=0.9`) to filter the exact translation block needed. If no specific language is requested or found, it dynamically falls back to the portal's default language.

### Response
Returns the standard Plone REST API JSON serialization, with the added translatable fields dynamically injected based on the available translations in the Zope Annotation dictionary.

```json
{
    "@id": "http://localhost:8080/Plone/@tablon/b2c3d4e5f6g7h8i9j0k1",
    "uuid": "b2c3d4e5f6g7h8i9j0k1",
    "date_start": "2024-03-01T00:00:00Z",
    "date_end": "2024-03-31T23:59:59Z",
    "origin": "external",
    "translations": {
        "eu": {
            "origin_department": "Kultura Saila",
            "origin_details": "Udaletxea",
            "description": "Kultur egitarauaren diru-laguntzak",
            "publication_url": "https://www.donostia.eus"
        },
        "es": {
            "origin_department": "Departamento de Cultura",
            "origin_details": "Ayuntamiento",
            "description": "Subvenciones para programas culturales",
            "publication_url": "https://www.donostia.eus/es"
        }
    },
    "documents": [
        {
            "@id": "http://localhost:8080/Plone/@tablon/b2c3d4e5f6g7h8i9j0k1/a1b2c3d4e5",
            "uuid": "a1b2c3d4e5",
            "titles": {
                "eu": "Deialdia",
                "es": "Convocatoria"
            },
            "izenpe_urls": {
                "eu": "http://accreditation.service/cert",
                "es": "http://accreditation.service/cert"
            },
            "filename": "deialdia_convocatoria.pdf",
            "contents": "JVBERi..."
        }
    ]
}
```

## 3. Get Expired Documents (GET `/@tablon-expired`)

Retrieves a list of documents that have expired on a specific date.

### Query Parameters
- `date`: (Optional) An ISO-formatted date string (for example, `YYYY-MM-DD`). Defaults to the current date if omitted.

### Response
Returns an array of serialized `DocumentoTablon` JSON objects.

## 4. Get File (GET `/@tablon/{shared_uid}/{file_shared_uid}`)

Retrieves the serialized JSON of a specific file. Useful for verifying the `izenpe_url` (the external accreditation certificate URL).

## 5. Delete Document (DELETE `/@tablon/{shared_uid}`)

Deletes the document and all its associated files and translations from the Plone database. Also purges the Shared UID entry from the annotation storage mapping.

### Response
- `204 No Content`: Successful deletion.
- `404 Not Found`: The document or translation could not be located.

## 6. Trigger Manual Accreditation (GET `/@tablon/{shared_uid}/{file_shared_uid}/get_external_accreditation`)

An asynchronous trigger endpoint used to force a retry of the external accreditation connection for a specific file.

### Response
```json
{"status": "ok"}
```
