# from udala.tablon import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ITablonView(Interface):
    """Marker Interface for ITablonView"""


@implementer(ITablonView)
class TablonView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('tablon_view.pt')

    pass
