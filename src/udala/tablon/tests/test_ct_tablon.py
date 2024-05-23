# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from udala.tablon.content.tablon import ITablon  # NOQA E501
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING  # noqa
from zope.component import createObject
from zope.component import queryUtility

import unittest


class TablonIntegrationTest(unittest.TestCase):

    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_tablon_schema(self):
        fti = queryUtility(IDexterityFTI, name='Tablon')
        schema = fti.lookupSchema()
        self.assertEqual(ITablon, schema)

    def test_ct_tablon_fti(self):
        fti = queryUtility(IDexterityFTI, name='Tablon')
        self.assertTrue(fti)

    def test_ct_tablon_factory(self):
        fti = queryUtility(IDexterityFTI, name='Tablon')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ITablon.providedBy(obj),
            u'ITablon not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_tablon_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Tablon',
            id='tablon',
        )

        self.assertTrue(
            ITablon.providedBy(obj),
            u'ITablon not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('tablon', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('tablon', parent.objectIds())

    def test_ct_tablon_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Tablon')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_tablon_filter_content_type_false(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Tablon')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'tablon_id',
            title='Tablon container',
        )
        self.parent = self.portal[parent_id]
        obj = api.content.create(
            container=self.parent,
            type='Document',
            title='My Content',
        )
        self.assertTrue(
            obj,
            u'Cannot add {0} to {1} container!'.format(obj.id, fti.id)
        )
