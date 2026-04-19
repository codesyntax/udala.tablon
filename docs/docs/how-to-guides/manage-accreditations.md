# Manage Accreditations

This guide explains how to configure and manage the external accreditation service for files uploaded to the Tablon.

The accreditation service guarantees that documents published on the board are timestamped and legally verifiable.

## Setting up the Connection

To connect to the accreditation service, you must have a valid PKCS12 certificate.

1.  Navigate to the Plone Control Panel -> **Udala Tablon**.
2.  Fill in the **Accrediter Endpoint URL** with the external service address.
3.  Convert your `.p12` or `.pfx` certificate to Base64 format:
    ```bash
    base64 -w 0 your_cert.p12 > cert_base64.txt
    ```
4.  Paste the contents of `cert_base64.txt` into the **PKCS12 File Content (Base64)** field.
5.  Enter the certificate password in the **PKCS12 File Password** field.
6.  Save the settings.

## Dealing with Accreditation Errors

If the service fails (due to network timeout or invalid credentials), the system will send an email to the configured `admin_email`. You should:

1. Check your email inbox for the exact error message.
2. Verify the endpoint URL is reachable from the server.
3. Ensure the certificate hasn't expired.

## Manual Accreditation Retries

If an automatic accreditation failed, you can manually trigger the process using the REST API endpoint:

```text
GET /@tablon/{document_shared_uid}/{file_shared_uid}/get_external_accreditation
```

This endpoint forces the system to try the accreditation again.
