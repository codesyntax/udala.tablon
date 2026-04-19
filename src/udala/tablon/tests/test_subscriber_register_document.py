from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from udala.tablon.testing import UDALA_TABLON_FUNCTIONAL_TESTING
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING

import unittest


class SubscriberIntegrationTest(unittest.TestCase):
    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])


class SubscriberFunctionalTest(unittest.TestCase):
    layer = UDALA_TABLON_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
