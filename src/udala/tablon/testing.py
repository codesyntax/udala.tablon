# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import udala.tablon


class UdalaTablonLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=udala.tablon)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "udala.tablon:default")


UDALA_TABLON_FIXTURE = UdalaTablonLayer()


UDALA_TABLON_INTEGRATION_TESTING = IntegrationTesting(
    bases=(UDALA_TABLON_FIXTURE,),
    name="UdalaTablonLayer:IntegrationTesting",
)


UDALA_TABLON_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(UDALA_TABLON_FIXTURE,),
    name="UdalaTablonLayer:FunctionalTesting",
)


UDALA_TABLON_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        UDALA_TABLON_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="UdalaTablonLayer:AcceptanceTesting",
)
