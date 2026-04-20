from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from udala.tablon.accreditation import get_publication_accreditation
from udala.tablon.annotations.document import get_documents
from udala.tablon.annotations.file import get_file
from udala.tablon.annotations.resolve import resolve_plone_uid
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


@implementer(IPublishTraverse)
class FileDownloadView(BrowserView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        self.query = self.request.form.copy()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    @property
    def _get_doc_id(self):
        if len(self.params) not in [2, 3]:
            raise Exception("Must supply exactly two parameters (doc id, file_id)")
        return self.params[0]

    @property
    def _get_file_id(self):
        if len(self.params) not in [2, 3]:
            raise Exception("Must supply exactly two parameters (doc id, file_id)")
        return self.params[1]

    def __call__(self):
        if len(self.params) in [2, 3]:
            doc_id = self._get_doc_id
            documents = get_documents(doc_id)

            file_id = self._get_file_id
            file = get_file(file_id)
            if documents and file:
                file_uid = resolve_plone_uid(file, self.request)

                if file_uid is None:
                    self.request.response.setStatus(404)
                    return {
                        "error": {
                            "type": "Not found",
                            "message": translate(
                                "The requested file does not exist",
                                context=self.request,
                            ),
                        }
                    }

                file_object = api.content.get(UID=file_uid)
                if file_object is not None:
                    if (
                        len(self.params) == 3
                        and self.params[2] == "get_external_accreditation"
                    ):
                        alsoProvides(self.request, IDisableCSRFProtection)
                        get_publication_accreditation(file_object)

                        return 1

                    else:
                        if file_object.file is not None:
                            blob = file_object.file

                            self.request.RESPONSE.setHeader(
                                "Content-Type", blob.contentType
                            )
                            return blob.data

                        return ""

        raise NotFound(self.context, "", self.request)
