# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.dexterity.utils import createContentInContainer
from udala.tablon.file_utils import register_file
from udala.tablon.testing import UDALA_TABLON_FUNCTIONAL_TESTING
from udala.tablon.utils import register_documents
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

import transaction
import unittest


class TestViews(unittest.TestCase):
    layer = UDALA_TABLON_FUNCTIONAL_TESTING

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

            file_key = register_file(file_eu.UID(), file_es.UID())

            register_documents(
                mydoc_eu.UID(),
                mydoc_es.UID(),
                [file_key],
                [file_key],
            )

            ITranslationManager(mydoc_eu).register_translation("es", mydoc_es)
            ITranslationManager(file_eu).register_translation("es", file_es)

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
