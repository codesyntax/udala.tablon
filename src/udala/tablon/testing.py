# -*- coding: utf-8 -*-
from plone.app.i18n.locales.interfaces import IContentLanguages
from plone.app.i18n.locales.interfaces import IMetadataLanguages
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing import zope
from Products.CMFPlone.utils import getToolByName
from zope.component import getUtility

import udala.tablon


ENABLED_LANGUAGES = ["eu", "es"]


def set_supported_languages(portal):
    """Set supported languages to the same predictable set for all test layers."""
    language_tool = getToolByName(portal, "portal_languages")
    for lang in ENABLED_LANGUAGES:
        language_tool.addSupportedLanguage(lang)


def set_available_languages():
    """Limit available languages to a small set.

    We're doing this to avoid excessive language lists in dumped responses
    for docs. Depends on our own ModifiableLanguages components
    (see plone.restapi:testing profile).
    """
    getUtility(IContentLanguages).setAvailableLanguages(ENABLED_LANGUAGES)
    getUtility(IMetadataLanguages).setAvailableLanguages(ENABLED_LANGUAGES)


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
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])

        applyProfile(portal, "udala.tablon:default")
        set_supported_languages(portal)
        if portal.portal_setup.profileExists("plone.app.multilingual:default"):
            applyProfile(portal, "plone.app.multilingual:default")
        set_available_languages()
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")


UDALA_TABLON_FIXTURE = UdalaTablonLayer()


UDALA_TABLON_INTEGRATION_TESTING = IntegrationTesting(
    bases=(UDALA_TABLON_FIXTURE,),
    name="UdalaTablonLayer:IntegrationTesting",
)


UDALA_TABLON_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(UDALA_TABLON_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="UdalaTablonLayer:FunctionalTesting",
)
