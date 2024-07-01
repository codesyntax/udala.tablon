# -*- coding: utf-8 -*-
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from udala.tablon.testing import UDALA_TABLON_FUNCTIONAL_TESTING
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING
from udala.tablon.utils import ANNOTATION_KEY
from udala.tablon.utils import delete_document
from udala.tablon.utils import get_document_by_uid_and_lang
from udala.tablon.utils import get_documents
from udala.tablon.utils import register_documents
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest


class TestAnnotationUtils(unittest.TestCase):

    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

        login(self.portal, SITE_OWNER_NAME)

        self.eu_tablon = createContentInContainer(
            self.portal.eu, "Tablon", title="Iragarki Ohola"
        )
        self.es_tablon = createContentInContainer(
            self.portal.es, "Tablon", title="Tablón de Anuncios"
        )
        ITranslationManager(self.eu_tablon).register_translation("es", self.es_tablon)

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

            ITranslationManager(mydoc_eu).register_translation("es", mydoc_es)
            ITranslationManager(file_eu).register_translation("es", file_es)

    def test_register_document_to_annotation(self):

        created_uuid = register_documents(
            self.eu_tablon.doc1.UID(),
            self.es_tablon.doc1.UID(),
            [self.eu_tablon.doc1.file_doc1.UID()],
            [self.es_tablon.doc1.file_doc1.UID()],
        )

        annotated = IAnnotations(self.portal)
        annotations = annotated.get(ANNOTATION_KEY)
        self.assertIn(created_uuid, annotations)

    def test_get_registered_document(self):

        created_uuid = register_documents(
            self.eu_tablon.doc1.UID(),
            self.es_tablon.doc1.UID(),
            [self.eu_tablon.doc1.file_doc1.UID()],
            [self.es_tablon.doc1.file_doc1.UID()],
        )

        documents = get_documents(created_uuid)

        self.assertTrue(isinstance(documents, dict))

        self.assertTrue(documents["eu"], self.eu_tablon.doc1.UID())
        self.assertTrue(documents["es"], self.es_tablon.doc1.UID())

        self.assertIn(self.eu_tablon.doc1.file_doc1.UID(), documents["files_eu"])
        self.assertIn(self.es_tablon.doc1.file_doc1.UID(), documents["files_es"])

    def test_get_document_by_uid_and_lang(self):
        created_uuid = register_documents(
            self.eu_tablon.doc1.UID(),
            self.es_tablon.doc1.UID(),
            [self.eu_tablon.doc1.file_doc1.UID()],
            [self.es_tablon.doc1.file_doc1.UID()],
        )

        eu_document = get_document_by_uid_and_lang(self.eu_tablon.doc1.UID(), "eu")
        self.assertEqual(eu_document, created_uuid)

        es_document = get_document_by_uid_and_lang(self.es_tablon.doc1.UID(), "es")
        self.assertEqual(es_document, created_uuid)
