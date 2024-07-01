# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from udala.tablon.testing import UDALA_TABLON_FUNCTIONAL_TESTING
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING
from udala.tablon.utils import delete_document
from udala.tablon.utils import get_document_by_uid_and_lang
from udala.tablon.utils import get_documents
from udala.tablon.utils import register_documents
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError
from plone.app.multilingual.interfaces import ITranslationManager
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
            mydoc_es = createContentInContainer(
                self.es_tablon, "DocumentoTablon", title=doc
            )
            ITranslationManager(mydoc_eu).register_translation("es", mydoc_es)

    def test_empty_tablon(self):
        self.assertEqual(len(self.eu_tablon.values()), 0)
        self.assertEqual(len(self.es_tablon.values()), 0)
