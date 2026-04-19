"""Setup tests for this package."""

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that udala.tablon is properly installed."""

    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if udala.tablon is installed."""
        self.assertTrue(self.installer.is_product_installed("udala.tablon"))

    def test_browserlayer(self):
        """Test that IUdalaTablonLayer is registered."""
        from plone.browserlayer import utils
        from udala.tablon.interfaces import IUdalaTablonLayer

        self.assertIn(IUdalaTablonLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("udala.tablon")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if udala.tablon is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("udala.tablon"))

    def test_browserlayer_removed(self):
        """Test that IUdalaTablonLayer is removed."""
        from plone.browserlayer import utils
        from udala.tablon.interfaces import IUdalaTablonLayer

        self.assertNotIn(IUdalaTablonLayer, utils.registered_layers())
