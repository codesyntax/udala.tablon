# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.dexterity.utils import createContentInContainer
from udala.tablon.file_utils import ANNOTATION_KEY
from udala.tablon.file_utils import delete_file
from udala.tablon.file_utils import get_file
from udala.tablon.file_utils import get_file_by_uid_and_lang
from udala.tablon.file_utils import register_file
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING
from zope.annotation.interfaces import IAnnotations

import unittest
import uuid


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

        created_uuid = register_file(
            self.eu_tablon.doc1.file_doc1.UID(),
            self.es_tablon.doc1.file_doc1.UID(),
        )

        annotated = IAnnotations(self.portal)
        annotations = annotated.get(ANNOTATION_KEY)
        self.assertIn(created_uuid, annotations)

    def test_get_registered_document(self):

        created_uuid = register_file(
            self.eu_tablon.doc1.file_doc1.UID(),
            self.es_tablon.doc1.file_doc1.UID(),
        )

        documents = get_file(created_uuid)

        self.assertTrue(isinstance(documents, dict))

        self.assertTrue(documents["eu"], self.eu_tablon.doc1.file_doc1.UID())
        self.assertTrue(documents["es"], self.es_tablon.doc1.file_doc1.UID())

    def test_get_inexistent_file(self):
        document1 = get_file_by_uid_and_lang(uuid.uuid4().hex, "eu")
        self.assertEqual(document1, None)

        document2 = get_file_by_uid_and_lang(uuid.uuid4().hex, "es")
        self.assertEqual(document2, None)

    def test_get_inexistent_language(self):
        document1 = get_file_by_uid_and_lang(uuid.uuid4().hex, "fr")
        self.assertEqual(document1, None)

        document2 = get_file_by_uid_and_lang(uuid.uuid4().hex, "en")
        self.assertEqual(document2, None)

    def test_get_existing_file_in_inexisting_language(self):
        register_file(
            self.eu_tablon.doc1.file_doc1.UID(),
            self.es_tablon.doc1.file_doc1.UID(),
        )

        eu_document = get_file_by_uid_and_lang(
            self.eu_tablon.doc1.file_doc1.UID(), "fr"
        )
        self.assertEqual(eu_document, None)

    def test_get_file_by_uid_and_lang(self):
        created_uuid = register_file(
            self.eu_tablon.doc1.file_doc1.UID(),
            self.es_tablon.doc1.file_doc1.UID(),
        )

        eu_document = get_file_by_uid_and_lang(
            self.eu_tablon.doc1.file_doc1.UID(), "eu"
        )
        self.assertEqual(eu_document, created_uuid)

        es_document = get_file_by_uid_and_lang(
            self.es_tablon.doc1.file_doc1.UID(), "es"
        )
        self.assertEqual(es_document, created_uuid)

    def test_delete_unexisting_file(self):
        generated_uuid = uuid.uuid4().hex

        result_delete = delete_file(generated_uuid)
        self.assertFalse(result_delete)

    def test_delete_file(self):
        created_uuid = register_file(
            self.eu_tablon.doc1.file_doc1.UID(),
            self.es_tablon.doc1.file_doc1.UID(),
        )

        result_delete = delete_file(created_uuid)
        self.assertTrue(result_delete)

        annotated = IAnnotations(self.portal)
        annotations = annotated.get(ANNOTATION_KEY, [])
        self.assertNotIn(created_uuid, annotations)
        self.assertEqual(len(annotations), 0)
