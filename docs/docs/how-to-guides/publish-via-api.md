# Publish Documents via API

This guide demonstrates how a third-party client can publish an announcement with associated files to the Tablon using the `udala.tablon` REST API.

## Scenario

You have an external application that generates public announcements and needs to publish them on your Plone 6 Electronic Notice Board in multiple languages (for example, Basque `eu` and Spanish `es`).

## 1. Preparing the Payload

The API accepts a dynamic JSON payload. You will need to encode any files in Base64 format.

Create a `payload.json` file:

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

## 2. Sending the Request

Use a tool like `curl` to post the payload to the `@tablon` endpoint. You must provide a valid authentication token (like a JWT or Basic Auth) with permissions to add content to the `Tablon` container.

```bash
curl -X POST "http://localhost:8080/Plone/@tablon" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <YOUR_TOKEN>" \
    -d @payload.json
```

## 3. Handling the Response

If successful, the API returns a `201 Created` status code and a JSON response containing the generated Shared UUID and the physical URLs of the created Plone items. The returned `url_{lang}` keys are dynamic and will precisely match the language codes provided in your payload's `translations` dictionary.

```json
{
    "@id": "http://localhost:8080/Plone/@tablon/b2c3d4e5f6g7h8i9j0k1",
    "uuid": "b2c3d4e5f6g7h8i9j0k1",
    "url_eu": "http://localhost:8080/Plone/tablon_id/documento_tablon",
    "url_es": "http://localhost:8080/Plone/es/tablon_id/documento_tablon"
}
```

You can now use `uuid` to fetch, update, or delete the document through the `@tablon` endpoint, completely independent of its physical URL or language.
