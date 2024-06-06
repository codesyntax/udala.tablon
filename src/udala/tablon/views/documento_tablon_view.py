# -*- coding: utf-8 -*-

# from udala.tablon import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IDocumentoTablonView(Interface):
    """ Marker Interface for IDocumentoTablonView"""


@implementer(IDocumentoTablonView)
class DocumentoTablonView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('documento_tablon_view.pt')

    def __call__(self):
        # Implement your own actions:
        return self.index()
