from Products.Five.browser import BrowserView


class AcreditedFileView(BrowserView):

    def __call__(self):

        blob = self.context.file

        self.request.RESPONSE.setHeader("Content-Type", blob.contentType)
        return blob.data
