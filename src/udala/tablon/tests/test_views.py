from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.testing.z2 import Browser
from udala.tablon.file_utils import register_file
from udala.tablon.testing import UDALA_TABLON_FUNCTIONAL_TESTING
from udala.tablon.utils import register_documents
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

import transaction
import unittest
import uuid


class TestViews(unittest.TestCase):
    layer = UDALA_TABLON_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        login(self.portal, SITE_OWNER_NAME)

        self.eu_tablon = createContentInContainer(
            self.portal.eu, "Tablon", title="Iragarki Ohola"
        )
        self.es_tablon = createContentInContainer(
            self.portal.es, "Tablon", title="Tablón de Anuncios"
        )
        ITranslationManager(self.eu_tablon).register_translation("es", self.es_tablon)

        self.file_keys = []
        self.document_keys = []

        for doc in ["doc1", "doc2"]:
            mydoc_eu = createContentInContainer(
                self.eu_tablon, "DocumentoTablon", title=doc
            )

            file_eu = createContentInContainer(
                mydoc_eu,
                "AcreditedFile",
                title=f"file_{doc}",
            )
            mydoc_es = createContentInContainer(
                self.es_tablon, "DocumentoTablon", title=doc
            )
            file_es = createContentInContainer(
                mydoc_es,
                "AcreditedFile",
                title=f"file_{doc}",
            )

            self.file_keys.append(register_file(file_eu.UID(), "eu"))

            self.document_keys.append(
                register_documents(
                    uid=mydoc_eu.UID(), language="eu", file_uids=[self.file_keys[-1]]
                )
            )

            ITranslationManager(mydoc_eu).register_translation("es", mydoc_es)
            ITranslationManager(file_eu).register_translation("es", file_es)

        # Set up browser
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )

        transaction.commit()

    def test_tablon_view(self):
        view = getMultiAdapter((self.eu_tablon, getRequest()), name="view")

        try:
            view()
        except Exception as e:
            e  # make pylint happy
            self.fail(
                f"View for content-type {self.eu_tablon.portal_type} raised an exception"
            )

    def test_doc_view(self):
        view = getMultiAdapter((self.eu_tablon.doc1, getRequest()), name="view")

        try:
            view()
        except Exception as e:
            e  # make pylint happy
            self.fail(
                f"View for content-type {self.eu_tablon.doc1.portal_type} raised an exception"
            )

        list_of_files = view.files()

        self.assertEqual(len(list_of_files), 1)

    def test_file_download_view_inexisting_file(self):
        generated_uuid1 = uuid.uuid4().hex
        generated_uuid2 = uuid.uuid4().hex
        with self.assertRaises(NotFound):
            self.portal.restrictedTraverse(
                f"@tablon/{generated_uuid1}/{generated_uuid2}"
            )

    def test_file_download_view_inexisting_file_of_existing_document(self):
        generated_uuid2 = uuid.uuid4().hex
        with self.assertRaises(NotFound):
            self.portal.restrictedTraverse(
                f"@tablon/{self.document_keys[0]}/{generated_uuid2}"
            )

    def test_file_download_view(self):
        self.browser.open(
            f"{self.portal_url}/@tablon/{self.document_keys[-1]}/{self.file_keys[-1]}"
        )
        self.assertTrue(self.browser.headers.get("Status").startswith("20"))
