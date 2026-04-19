from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from udala.tablon.testing import UDALA_TABLON_INTEGRATION_TESTING
from udala.tablon.utils import ANNOTATION_KEY
from udala.tablon.utils import delete_document
from udala.tablon.utils import get_document_by_uid_and_lang
from udala.tablon.utils import get_documents
from udala.tablon.utils import register_documents
from zope.annotation.interfaces import IAnnotations

import unittest


class TestAnnotationUtils(unittest.TestCase):
    layer = UDALA_TABLON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        login(self.portal, SITE_OWNER_NAME)

        # We don't need actual content objects to test the dict manipulation layer.
        # We can just use dummy UIDs, as utils.py just works with strings and annotations.
        # Wipe annotations just in case
        annotated = IAnnotations(self.portal)
        if ANNOTATION_KEY in annotated:
            del annotated[ANNOTATION_KEY]

    def test_register_single_language_document(self):
        created_uuid = register_documents(uid="plone_1", language="eu")

        annotated = IAnnotations(self.portal)
        annotations = annotated.get(ANNOTATION_KEY)

        self.assertIn(created_uuid, annotations)
        data = annotations[created_uuid]

        self.assertEqual(data["translations"]["eu"], "plone_1")
        self.assertEqual(data["files"], [])
        self.assertTrue("date" in data)

    def test_append_translation_to_existing_document(self):
        shared_id = register_documents(uid="plone_1", language="eu")
        register_documents(uid="plone_2", language="es", shared_uid=shared_id)

        data = get_documents(shared_id)

        self.assertEqual(data["translations"]["eu"], "plone_1")
        self.assertEqual(data["translations"]["es"], "plone_2")
        self.assertEqual(data["files"], [])

    def test_file_deduplication(self):
        shared_id = register_documents(
            uid="plone_1", language="eu", file_uids=["file_1"]
        )

        data = get_documents(shared_id)
        self.assertEqual(data["files"], ["file_1"])

        # Append an overlapping file list
        register_documents(
            uid="plone_2",
            language="es",
            file_uids=["file_1", "file_2"],
            shared_uid=shared_id,
        )

        data2 = get_documents(shared_id)
        self.assertCountEqual(data2["files"], ["file_1", "file_2"])

    def test_get_document_by_uid_and_lang_safe_handling(self):
        # 1. Null handling
        self.assertIsNone(get_document_by_uid_and_lang(None, "eu"))

        # Setup data
        shared_id = register_documents(uid="plone_1", language="eu")

        # 2. Valid UID, wrong language
        self.assertIsNone(get_document_by_uid_and_lang("plone_1", "es"))

        # 3. Valid UID, correct language
        self.assertEqual(get_document_by_uid_and_lang("plone_1", "eu"), shared_id)

    def test_delete_document(self):
        shared_id = register_documents(uid="plone_1", language="eu")

        # Exists before deletion
        self.assertIsNotNone(get_documents(shared_id))

        result_delete = delete_document(shared_id)
        self.assertTrue(result_delete)

        # Does not exist after
        self.assertIsNone(get_documents(shared_id))

        # Double delete returns False
        self.assertFalse(delete_document(shared_id))
