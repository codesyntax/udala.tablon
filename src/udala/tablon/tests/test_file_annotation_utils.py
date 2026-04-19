from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from udala.tablon.file_utils import ANNOTATION_KEY
from udala.tablon.file_utils import delete_file
from udala.tablon.file_utils import get_file
from udala.tablon.file_utils import get_file_by_uid_and_lang
from udala.tablon.file_utils import register_file
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING
from zope.annotation.interfaces import IAnnotations

import unittest


class TestFileAnnotationUtils(unittest.TestCase):
    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        login(self.portal, SITE_OWNER_NAME)

        # Wipe annotations just in case
        annotated = IAnnotations(self.portal)
        if ANNOTATION_KEY in annotated:
            del annotated[ANNOTATION_KEY]

    def test_register_single_language_file(self):
        created_uuid = register_file(uid="file_plone_1", language="eu")

        annotated = IAnnotations(self.portal)
        annotations = annotated.get(ANNOTATION_KEY)

        self.assertIn(created_uuid, annotations)
        data = annotations[created_uuid]

        self.assertEqual(data["translations"]["eu"], "file_plone_1")
        self.assertTrue("date" in data)

    def test_append_translation_to_existing_file(self):
        shared_id = register_file(uid="file_plone_1", language="eu")
        register_file(uid="file_plone_2", language="es", shared_uid=shared_id)

        data = get_file(shared_id)

        self.assertEqual(data["translations"]["eu"], "file_plone_1")
        self.assertEqual(data["translations"]["es"], "file_plone_2")

    def test_get_file_by_uid_and_lang_safe_handling(self):
        # 1. Null handling
        self.assertIsNone(get_file_by_uid_and_lang(None, "eu"))

        # Setup data
        shared_id = register_file(uid="file_plone_1", language="eu")

        # 2. Valid UID, wrong language
        self.assertIsNone(get_file_by_uid_and_lang("file_plone_1", "es"))

        # 3. Valid UID, correct language
        self.assertEqual(get_file_by_uid_and_lang("file_plone_1", "eu"), shared_id)

    def test_delete_file(self):
        shared_id = register_file(uid="file_plone_1", language="eu")

        # Exists before deletion
        self.assertIsNotNone(get_file(shared_id))

        result_delete = delete_file(shared_id)
        self.assertTrue(result_delete)

        # Does not exist after
        self.assertIsNone(get_file(shared_id))

        # Double delete returns False
        self.assertFalse(delete_file(shared_id))
