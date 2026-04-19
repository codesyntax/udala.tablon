from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from udala.tablon.content.documento_tablon import IDocumentoTablon
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING
from zope.component import createObject
from zope.component import queryUtility

import unittest


class DocumentoTablonIntegrationTest(unittest.TestCase):
    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.parent = self.portal

    def test_ct_documento_tablon_schema(self):
        fti = queryUtility(IDexterityFTI, name="DocumentoTablon")
        schema = fti.lookupSchema()
        self.assertEqual(IDocumentoTablon, schema)

    def test_ct_documento_tablon_fti(self):
        fti = queryUtility(IDexterityFTI, name="DocumentoTablon")
        self.assertTrue(fti)

    def test_ct_documento_tablon_factory(self):
        fti = queryUtility(IDexterityFTI, name="DocumentoTablon")
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IDocumentoTablon.providedBy(obj),
            f"IDocumentoTablon not provided by {obj}!",
        )

    def test_ct_documento_tablon_adding(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        obj = api.content.create(
            container=self.portal,
            type="DocumentoTablon",
            id="documento_tablon",
        )

        self.assertTrue(
            IDocumentoTablon.providedBy(obj),
            f"IDocumentoTablon not provided by {obj.id}!",
        )

        parent = obj.__parent__
        self.assertIn("documento_tablon", parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn("documento_tablon", parent.objectIds())

    def test_ct_documento_tablon_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="DocumentoTablon")
        self.assertTrue(fti.global_allow, f"{fti.id} is not globally addable!")

    def test_ct_documento_tablon_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="DocumentoTablon")
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            "documento_tablon_id",
            title="DocumentoTablon container",
        )
        self.parent = self.portal[parent_id]
        
        obj = api.content.create(
            container=self.parent,
            type="AcreditedFile",
            title="My Acredited File",
        )
        self.assertTrue(obj, f"Cannot add {obj.id} to {fti.id} container!")
        
        from plone.api.exc import InvalidParameterError
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type="Document",
                title="My Content",
            )
