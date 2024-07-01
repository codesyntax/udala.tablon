# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from udala.tablon import _

# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer


class IAcreditedFile(model.Schema):
    """Marker interface and Dexterity Python Schema for AcreditedFile"""

    file = NamedBlobFile(title="File", required=True)

    url = schema.TextLine(title=_("Accreditation URL"))


@implementer(IAcreditedFile)
class AcreditedFile(Container):
    """Content-type class for IAcreditedFile"""
