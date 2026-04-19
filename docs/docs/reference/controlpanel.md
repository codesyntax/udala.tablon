# Registry Configuration Reference

The `udala.tablon` package creates a dedicated Plone Control Panel form to manage the external accreditation service.

## Configuration Registry Keys

All settings are stored in Plone's `plone.registry` under the prefix `udala.tablon.udala_tablon_control_panel.IUdalaTablonControlPanel`.

### `admin_email`
- **Type**: `schema.TextLine`
- **Description**: Administrator's email address. Used by the asynchronous task runners to send error notifications if the external accreditation service fails or times out.

### `domain`
- **Type**: `schema.TextLine`
- **Description**: The root URL of the Plone site. When running asynchronous processes (like celery/rabbitMQ tasks for accreditation), the system does not have access to the actual Request object. This setting provides the base URL needed to compute absolute URLs.

### `accrediterendpointurl`
- **Type**: `schema.TextLine`
- **Description**: The endpoint URL of the external accreditation/timestamping service (for example, Izenpe).

### `pkcs12_file_content_b64`
- **Type**: `schema.TextLine`
- **Description**: The PKCS12 (`.p12` / `.pfx`) certificate file encoded as a Base64 string. The system decodes this in-memory when authenticating with the external endpoint.

### `pkcs12_file_password`
- **Type**: `schema.Password`
- **Description**: The password required to unlock the provided PKCS12 certificate. It is masked in the Control Panel UI.
