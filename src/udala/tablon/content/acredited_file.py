# -*- coding: utf-8 -*-
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from udala.tablon import _
from zope import schema
from zope.interface import alsoProvides, implementer


class IAcreditedFile(model.Schema):
    """Marker interface and Dexterity Python Schema for AcreditedFile"""

    file = NamedBlobFile(title="File", required=True)

    url = schema.TextLine(title=_("Accreditation URL"), required=False)


alsoProvides(IAcreditedFile["url"], ILanguageIndependentField)


@implementer(IAcreditedFile)
class AcreditedFile(Container):
    """Content-type class for IAcreditedFile"""
