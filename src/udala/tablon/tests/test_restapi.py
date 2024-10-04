from .example_data import correct_document_different_documents_per_language
from .example_data import correct_document_files_and_urls
from .example_data import correct_document_no_files
from .example_data import correct_document_no_urls
from .example_data import document_error_in_forms_empty_record_number
from .example_data import document_error_in_forms_invalid_end_date
from .example_data import document_error_in_forms_invalid_start_date
from .example_data import document_error_in_forms_no_description_es
from .example_data import document_error_in_forms_no_description_eu
from .example_data import document_error_in_forms_no_origin
from .example_data import document_error_in_forms_no_origin_department_es
from .example_data import document_error_in_forms_no_origin_department_eu
from .example_data import document_error_in_forms_no_origin_details_es
from .example_data import document_error_in_forms_no_origin_details_eu
from .example_data import document_error_in_forms_no_record_number
from .example_data import document_to_publish_at_midnight
from .example_data import invalid_url
from .example_data import wrong_origin
from DateTime import DateTime
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import RelativeSession
from udala.tablon.file_utils import register_file
from udala.tablon.testing import UDALA_TABLON_FUNCTIONAL_TESTING
from udala.tablon.utils import register_documents

import transaction
import unittest
import uuid


EFFECTIVE_DATE = DateTime("1995-07-31T13:45:00")
EXPIRATION_DATE = DateTime("1995-10-31T13:45:00")


class TestRESTAPIEndpoints(unittest.TestCase):
    layer = UDALA_TABLON_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        login(self.portal, SITE_OWNER_NAME)

        self.eu_tablon = createContentInContainer(
            self.portal.eu, "Tablon", title="Iragarki Ohola"
        )
        self.es_tablon = createContentInContainer(
            self.portal.es,
            "Tablon",
            title="Tablón de Anuncios",
        )
        ITranslationManager(self.eu_tablon).register_translation("es", self.es_tablon)

        self.file_data = {}
        self.document_data = []
        self.file_annotation_ids = []

        for doc in ["doc1", "doc2"]:
            mydoc_eu = createContentInContainer(
                self.eu_tablon,
                "DocumentoTablon",
                title=doc,
                effective=EFFECTIVE_DATE,
                expires=EXPIRATION_DATE,
            )

            file_eu = createContentInContainer(
                mydoc_eu,
                "AcreditedFile",
                title=f"file_{doc}",
            )
            mydoc_es = createContentInContainer(
                self.es_tablon,
                "DocumentoTablon",
                title=doc,
                effective=EFFECTIVE_DATE,
                expires=EXPIRATION_DATE,
            )
            file_es = createContentInContainer(
                mydoc_es,
                "AcreditedFile",
                title=f"file_{doc}",
            )

            ITranslationManager(mydoc_eu).register_translation("es", mydoc_es)
            ITranslationManager(file_eu).register_translation("es", file_es)

            file_key = register_file(file_eu.UID(), file_es.UID())

            key = register_documents(
                mydoc_eu.UID(),
                mydoc_es.UID(),
                [file_key],
                [file_key],
            )
            self.document_data.append(key)
            self.file_annotation_ids.append(file_key)
            self.file_data[key] = [file_key]

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.anonymous_api_session = RelativeSession(self.portal_url, test=self)
        self.anonymous_api_session.headers.update({"Accept": "application/json"})

        transaction.commit()

    def test_get_anonymous_unauthorized(self):
        response = self.anonymous_api_session.get("/@tablon")
        self.assertEqual(response.status_code, 404)

    def test_get_empty_id(self):
        response = self.api_session.get("/@tablon")
        self.assertEqual(response.status_code, 404)

    def test_get_inexisting_document(self):
        generated_uuid = uuid.uuid4().hex
        response = self.api_session.get(f"/@tablon/{generated_uuid}")
        self.assertEqual(response.status_code, 404)

    def test_get_inexisting_file_in_inexisting_doc(self):
        generated_uuid_1 = uuid.uuid4().hex
        generated_uuid_2 = uuid.uuid4().hex
        response = self.api_session.get(
            f"/@tablon/{generated_uuid_1}/{generated_uuid_2}"
        )
        self.assertEqual(response.status_code, 404)

    def test_get_inexisting_file_in_existing_doc(self):
        generated_uuid_1 = uuid.uuid4().hex
        response = self.api_session.get(
            f"/@tablon/{self.document_data[0]}/{generated_uuid_1}"
        )
        self.assertEqual(response.status_code, 404)

    def test_get_document(self):
        response = self.api_session.get(f"/@tablon/{self.document_data[0]}")
        self.assertEqual(response.status_code, 200)

    def test_get_file_in_document(self):
        response = self.api_session.get(
            f"/@tablon/{self.document_data[0]}/{self.file_annotation_ids[0]}"
        )

        self.assertEqual(response.status_code, 200)

    def test_post_document_invalid_urls(self):
        response = self.api_session.post("/@tablon", json=invalid_url)
        self.assertEqual(response.status_code, 400)

    def test_post_document_error_no_origin(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_origin
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_error_no_description_es(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_description_es
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_error_no_description_eu(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_description_eu
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_with_files_and_urls(self):

        response = self.api_session.post(
            "/@tablon", json=correct_document_files_and_urls
        )

        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        generated_uuid = response_json.get("uuid")

        response = self.api_session.get(f"/@tablon/{generated_uuid}")
        self.assertEqual(response.status_code, 200)

    def test_post_document_without_files(self):
        response = self.api_session.post("/@tablon", json=correct_document_no_files)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        generated_uuid = response_json.get("uuid")

        response = self.api_session.get(f"/@tablon/{generated_uuid}")
        self.assertEqual(response.status_code, 200)

    def test_post_document_without_urls(self):
        response = self.api_session.post("/@tablon", json=correct_document_no_urls)

        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        generated_uuid = response_json.get("uuid")

        response = self.api_session.get(f"/@tablon/{generated_uuid}")
        self.assertEqual(response.status_code, 200)

    def test_post_document_publish_at_midnight(self):
        response = self.api_session.post(
            "/@tablon", json=document_to_publish_at_midnight
        )
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        generated_uuid = response_json.get("uuid")

        response = self.api_session.get(f"/@tablon/{generated_uuid}")
        self.assertEqual(response.status_code, 200)

    def test_post_document_invalid_start_date(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_invalid_start_date
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_invalid_end_date(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_invalid_end_date
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_no_record_number(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_record_number
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_emtpy_record_number(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_empty_record_number
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_different_languages_files(self):

        response = self.api_session.post(
            "/@tablon", json=correct_document_different_documents_per_language
        )
        self.assertEqual(response.status_code, 201)

    def test_post_document_no_origin_department_es(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_origin_department_es
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_no_origin_department_eu(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_origin_department_eu
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_no_origin_details_eu(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_origin_details_eu
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_no_origin_details_es(self):
        response = self.api_session.post(
            "/@tablon", json=document_error_in_forms_no_origin_details_es
        )
        self.assertEqual(response.status_code, 400)

    def test_post_document_wrong_origin(self):
        response = self.api_session.post("/@tablon", json=wrong_origin)
        self.assertEqual(response.status_code, 400)

    def test_get_with_3_params(self):
        generated_uuid_1 = uuid.uuid4().hex
        generated_uuid_2 = uuid.uuid4().hex
        generated_uuid_3 = uuid.uuid4().hex
        response = self.api_session.get(
            f"/@tablon/{generated_uuid_1}/{generated_uuid_2}/{generated_uuid_3}"
        )

        self.assertEqual(response.status_code, 404)

    def test_get_with_4_params(self):
        generated_uuid_1 = uuid.uuid4().hex
        generated_uuid_2 = uuid.uuid4().hex
        generated_uuid_3 = uuid.uuid4().hex
        generated_uuid_4 = uuid.uuid4().hex
        response = self.api_session.get(
            f"/@tablon/{generated_uuid_1}/{generated_uuid_2}/{generated_uuid_3}/{generated_uuid_4}"
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_existing_document(self):
        response = self.api_session.delete(
            f"/@tablon/{self.document_data[0]}",
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_unexisting_document(self):
        generated_uuid_1 = uuid.uuid4().hex

        response = self.api_session.delete(
            f"/@tablon/{generated_uuid_1}",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_error_request(self):
        response = self.api_session.delete(
            "/@tablon",
        )
        self.assertEqual(response.status_code, 404)

    def test_get_expired_today(self):
        response = self.api_session.get("/@tablon-expired")
        self.assertEqual(response.status_code, 200)

    def test_get_expired_in_a_given_day(self):
        response = self.api_session.get("/@tablon-expired?date=1995-10-31")

        self.assertEqual(response.status_code, 200)
        response_json = response.json()

        self.assertEqual(len(response_json), 2)
