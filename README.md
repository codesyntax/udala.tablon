# udala.tablon

[![CI](https://github.com/codesyntax/udala.tablon/actions/workflows/main.yml/badge.svg)](https://github.com/codesyntax/udala.tablon/actions/workflows/main.yml)

**udala.tablon** provides an **Electronic Notice Board** (*Tablón de Anuncios Electrónico*) for Public Administration sites built on Plone 6.

It is designed to publish administrative announcements and their associated files in a legally verifiable way by integrating seamlessly with external accreditation and timestamping services (like Izenpe).

## Features

- **Custom Content Types:** Provides a strict, validated content hierarchy:
  - `Tablon`: The main container/board.
  - `DocumentoTablon`: The administrative announcement.
  - `AcreditedFile`: The uploaded binary files that require timestamping.
- **Legal Accreditation:** Automatically connects to external certificate authorities to timestamp published files, storing the resulting verifiable URLs natively on the Plone objects.
- **"Shared UID" Architecture:** Fully supports Plone App Multilingual (PAM). It intelligently decouples Plone's internal translated objects from the external timestamping service by mapping them to a single, language-agnostic "Shared UID". This guarantees that a document translated into Basque, Spanish, and English shares a single legal certificate URL.
- **Robust REST API:** Provides a powerful, fully dynamic JSON API (`/@tablon`) allowing third-party administrative backoffices to securely `POST`, `GET`, and `DELETE` multilingual announcements without needing to know Plone's internal folder structures.

## Documentation

Full documentation, including tutorials, how-to guides, concepts, and the complete REST API reference, is published online at:
**[https://codesyntax.github.io/udala.tablon/](https://codesyntax.github.io/udala.tablon/)**

## Installation

Install `udala.tablon` using your preferred Plone 6 package manager (e.g., `uv` or `pip` with `mxdev`):

Add it to your `requirements.txt` or `pyproject.toml`:
```text
udala.tablon
```

Then install the add-on in your Plone Control Panel.

## Configuration

After installation, navigate to the **Udala Tablon** section in your Plone Control Panel to configure:
1. The external accrediter endpoint URL (e.g., Izenpe).
2. The PKCS12 (`.p12`) certificate encoded in Base64 and its password.
3. An administrator email to receive alerts if the external timestamping service fails or times out.

## Contribute

- Issue Tracker: https://github.com/codesyntax/udala.tablon/issues
- Source Code: https://github.com/codesyntax/udala.tablon

## License

The project is licensed under the GPLv2.
