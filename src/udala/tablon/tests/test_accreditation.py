from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from udala.tablon.accreditation import accreditation
from udala.tablon.testing import UDALA_TABLON_FUNCTIONAL_TESTING
from unittest.mock import patch

import unittest


class TestAccreditation(unittest.TestCase):
    layer = UDALA_TABLON_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        login(self.portal, SITE_OWNER_NAME)
        self.tablon = api.content.create(self.portal, "Tablon", title="Tablon")
        self.doc = api.content.create(self.tablon, "DocumentoTablon", title="doc1")
        self.file = api.content.create(self.doc, "AcreditedFile", title="file1")
        from plone.namedfile.file import NamedBlobFile

        self.file.file = NamedBlobFile(b"test", filename="test.pdf")
        self.doc.expires = "2025-12-31"

    @patch("udala.tablon.accreditation.get_accreditation_for_url")
    def test_accreditation_multilingual(self, mock_get_accreditation):
        mock_get_accreditation.return_value = (1, "http://accreditation.service", "OK")

        # Test with PAM enabled
        with patch("udala.tablon.accreditation.is_pam_enabled", return_value=True):
            result, message = accreditation(self.file)

        self.assertEqual(result, 1)
        self.assertEqual(message, "OK")
        self.assertEqual(self.file.url, "http://accreditation.service")

    @patch("udala.tablon.accreditation.get_accreditation_for_url")
    def test_accreditation_monolingual(self, mock_get_accreditation):
        mock_get_accreditation.return_value = (1, "http://accreditation.service", "OK")

        # Test without PAM enabled
        with patch("udala.tablon.accreditation.is_pam_enabled", return_value=False):
            result, message = accreditation(self.file)

        self.assertEqual(result, 1)
        self.assertEqual(message, "OK")
        self.assertEqual(self.file.url, "http://accreditation.service")
