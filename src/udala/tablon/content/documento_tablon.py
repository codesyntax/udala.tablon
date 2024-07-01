# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container

# from plone.namedfile import field as namedfile
from plone.supermodel import model
from udala.tablon import _

# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer


class IDocumentoTablon(model.Schema):
    """Marker interface and Dexterity Python Schema for DocumentoTablon"""

    origin = schema.TextLine(title=_("Origen del documento"))

    origin_department = schema.TextLine(
        title=_("Departamento origen del documento"), required=False
    )

    origin_details = schema.TextLine(
        title=_("Detalles del origen del documento"), required=False
    )

    publication_url = schema.TextLine(
        title=_("URL de publicacion del documento"), required=False
    )


@implementer(IDocumentoTablon)
class DocumentoTablon(Container):
    """Content-type class for IDocumentoTablon"""
