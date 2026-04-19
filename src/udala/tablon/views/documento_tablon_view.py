# from udala.tablon import _
from plone import api
from Products.Five.browser import BrowserView
from udala.tablon.file_utils import get_file
from udala.tablon.utils import get_document_by_uid_and_lang
from udala.tablon.utils import get_documents
from zope.interface import implementer
from zope.interface import Interface


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IDocumentoTablonView(Interface):
    """Marker Interface for IDocumentoTablonView"""


@implementer(IDocumentoTablonView)
class DocumentoTablonView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('documento_tablon_view.pt')

    def files(self):
        portal = api.portal.get()
        portal_url = portal.absolute_url()
        language = self.context.Language()
        items = []

        document_key = get_document_by_uid_and_lang(self.context.UID(), language)
        document = get_documents(document_key)
        if document:
            shared_files = document.get("files", [])

            for shared_file_uid in shared_files:
                file_data = get_file(shared_file_uid)
                if file_data is not None:
                    # Using the translations dict structure safely
                    file_language_uid = file_data.get("translations", {}).get(language)
                    if file_language_uid:
                        file_object = api.content.get(UID=file_language_uid)
                        if file_object:
                            items.append({
                                "url": f"{portal_url}/@tablon/{document_key}/{shared_file_uid}",  # noqa: E501
                                "file_title": file_object.Title(),
                                "file_accreditation_url": file_object.url,
                            })
        return items
