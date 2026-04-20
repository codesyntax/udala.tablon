# Shared UID Architecture

The Electronic Notice Board relies on an architectural layer called the "Shared UID" system. This document explains the reasoning behind decoupling Plone's native UIDs from the external representation of documents and files.

## The Problem

In a multilingual Plone 6 setup, translating a content item via Plone App Multilingual (PAM) creates an entirely distinct object in the ZODB. 
If an announcement is published in both Basque (`eu`) and Spanish (`es`), Plone creates two objects, each with its own internal UID and physical URL (for example, `/eu/tablon/iragarkia` and `/es/tablon/anuncio`).

When submitting documents to an external timestamping or Accreditation service, the third-party service expects a *single* unique identifier and a *single* URL for "the document," regardless of which language a citizen is currently reading it in. Sending two separate UIDs would result in two distinct digital certificates for what is legally the same administrative act.

## The Solution

To solve this, `udala.tablon` implements a persistent mapping layer using Zope Annotations at the portal root.

When an API client publishes an announcement, the system dynamically generates a single UUID4 (the **Shared UID**). It then creates the Plone content object in the base language, registers it in the annotation dictionary, and sequentially creates any requested translations, mapping their respective Plone UIDs to the same Shared UID.

### The Storage Model

The mapping is stored efficiently in an `OOBTree` within `IAnnotations(portal)["udala.tablon.documento_tablon"]`.

```python
{
    "shared_uid_12345": {
        "translations": {
            "eu": "plone_uid_A",
            "es": "plone_uid_B",
            "en": "plone_uid_C"
        },
        "files": ["shared_file_uid_987", "shared_file_uid_654"],
        "date": "2024-03-01T12:00:00Z"
    }
}
```

### The Abstraction Layer

With this dictionary in place, the `@tablon` REST API and Browser Views can completely abstract away Plone's physical structure.

When a user visits `http://site.com/@tablon/shared_uid_12345`, the endpoint checks the `Accept-Language` header (or the current portal language), looks up the dictionary, and dynamically resolves to `plone_uid_A` or `plone_uid_B` behind the scenes.

## Why not use Plone App Multilingual's `TranslationGroup` UID?

PAM internally groups translations using a `TranslationGroup` UUID. While tempting to use, `udala.tablon` cannot rely on it because:

1. **Monolingual Support:** The package must function flawlessly on sites where Plone App Multilingual is completely uninstalled or disabled. In those scenarios, `TranslationGroup` UIDs do not exist.
2. **File Independence:** A single `DocumentoTablon` might contain a file that is language-neutral (applies to all languages) alongside a file that is language-specific (only for `eu`). Our custom mapping layer allows files to have their own Shared UIDs and distinct translation matrices independent of their parent document's PAM status.
