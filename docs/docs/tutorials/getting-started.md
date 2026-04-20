# Getting Started

This tutorial will guide you through setting up and running `udala.tablon` in a local Plone 6 environment.

## 1. Installation

First, install the package in your Plone environment. If you're using `uv` and `mxdev`, add the package to your requirements.

```bash
uv pip install udala.tablon
```

## 2. Start the Instance

Start the Zope instance:

```bash
make start
```

## 3. Install the Add-on in Plone

1. Navigate to the Plone Control Panel (usually `http://localhost:8080/Plone/@@overview-controlpanel`).
2. Go to **Add-ons**.
3. Find **Udala Tablon** and click **Install**.

## 4. Configure Accreditation Service

To make the accreditation system work, you need to configure it in the registry:

1. Go to the **Udala Tablon** control panel.
2. Enter the URL of the external accreditation endpoint.
3. Provide the `pkcs12` certificate encoded in Base64 and its password.
4. Set the `admin_email` where error notifications will be sent if the accreditation fails.

You are now ready to publish documents!
