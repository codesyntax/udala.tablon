from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from udala.tablon.content.acredited_file import IAcreditedFile
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING
from zope.component import createObject
from zope.component import queryUtility

import unittest


class AcreditedFileIntegrationTest(unittest.TestCase):
    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.parent = self.portal

    def test_ct_acredited_file_schema(self):
        fti = queryUtility(IDexterityFTI, name="AcreditedFile")
        schema = fti.lookupSchema()
        self.assertEqual(IAcreditedFile, schema)

    def test_ct_acredited_file_fti(self):
        fti = queryUtility(IDexterityFTI, name="AcreditedFile")
        self.assertTrue(fti)

    def test_ct_acredited_file_factory(self):
        fti = queryUtility(IDexterityFTI, name="AcreditedFile")
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IAcreditedFile.providedBy(obj),
            f"IAcreditedFile not provided by {obj}!",
        )

    def test_ct_acredited_file_adding(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        tablon = api.content.create(
            container=self.portal,
            type="Tablon",
            id="tablon_container",
        )
        doc = api.content.create(
            container=tablon,
            type="DocumentoTablon",
            id="documento_container",
        )

        obj = api.content.create(
            container=doc,
            type="AcreditedFile",
            id="acredited_file",
        )

        self.assertTrue(
            IAcreditedFile.providedBy(obj),
            f"IAcreditedFile not provided by {obj.id}!",
        )

        parent = obj.__parent__
        self.assertIn("acredited_file", parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn("acredited_file", parent.objectIds())

    def test_ct_acredited_file_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="AcreditedFile")
        self.assertFalse(fti.global_allow, f"{fti.id} should NOT be globally addable!")

    def test_ct_acredited_file_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="AcreditedFile")
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            "acredited_file_id",
            title="AcreditedFile container",
        )
        self.parent = self.portal[parent_id]

        from plone.api.exc import InvalidParameterError

        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type="Document",
                title="My Content",
            )
