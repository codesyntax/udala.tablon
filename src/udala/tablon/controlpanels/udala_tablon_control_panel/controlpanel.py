# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from udala.tablon import _
from udala.tablon.interfaces import IUdalaTablonLayer
from zope import schema
from zope.component import adapter
from zope.interface import Interface


class IUdalaTablonControlPanel(Interface):
    accrediterendpointurl = schema.TextLine(
        title=_(
            "Accrediter endpoint URL",
        ),
        description=_(
            "",
        ),
        default="https://epublicacion.izenpe.com:8445/constancia_publicacion/services/IzenpeConstanciaPubDes?wsdl",
        required=True,
        readonly=False,
    )
    pkcs12_file_content_b64 = schema.Text(
        title=_(
            "base64 encoded pkcs12 file",
        ),
        description=_(
            "",
        ),
        default="",
        required=True,
        readonly=False,
    )
    pkcs12_file_password = schema.TextLine(
        title=_(
            "Password of the pkcs12 file",
        ),
        description=_(
            "",
        ),
        default="",
        required=True,
        readonly=False,
    )
    domain = schema.TextLine(
        title=_(
            "Enter the full domain (with https) of the site. ",
        ),
        description=_(
            "We need to pass this as a configuration item because when running async processes we do not have access to the real URL of the object",
        ),
        default="",
        required=True,
        readonly=False,
    )
    admin_email = schema.TextLine(
        title=_(
            "Email address where accreditation notifications will be sent",
        ),
        description=_(
            "",
        ),
        default="",
        required=True,
        readonly=False,
    )


class UdalaTablonControlPanel(RegistryEditForm):
    schema = IUdalaTablonControlPanel
    schema_prefix = "udala.tablon.udala_tablon_control_panel"
    label = _("Udala Tablon Control Panel")


UdalaTablonControlPanelView = layout.wrap_form(
    UdalaTablonControlPanel, ControlPanelFormWrapper
)


@adapter(Interface, IUdalaTablonLayer)
class UdalaTablonControlPanelConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IUdalaTablonControlPanel
    configlet_id = "udala_tablon_control_panel-controlpanel"
    configlet_category_id = "Products"
    title = _("Udala Tablon Control Panel")
    group = ""
    schema_prefix = "udala.tablon.udala_tablon_control_panel"
