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
    myfield_name = schema.TextLine(
        title=_(
            "This is an example field for this control panel",
        ),
        description=_(
            "",
        ),
        default="",
        required=False,
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
