from BTrees.OOBTree import OOBTree
from datetime import datetime, UTC
from plone import api
from Products.CMFPlone.utils import safe_text
from zope.annotation.interfaces import IAnnotations

import base64
import requests
import uuid


ANNOTATION_KEY = "udala.tablon.documento_tablon"


def register_documents(documento_eu, documento_es, files_eu, files_es):
    """register documents in an annotation and produce a single identifier"""
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    # Check whether this document is already added:
    generated_uuid = get_document_by_uid_and_lang(documento_eu, "eu")
    if generated_uuid is None:
        generated_uuid = uuid.uuid4().hex
        while generated_uuid in annotations:
            generated_uuid = uuid.uuid4().hex

    old_files_eu = annotations.get(generated_uuid, {}).get("files_eu", [])
    old_files_es = annotations.get(generated_uuid, {}).get("files_es", [])
    date = annotations.get(generated_uuid, {}).get(
        "date", datetime.now(UTC).isoformat()
    )

    annotations[generated_uuid] = {
        "eu": documento_eu,
        "es": documento_es,
        "files_eu": old_files_eu + files_eu,
        "files_es": old_files_es + files_es,
        "date": date,
    }

    annotated[ANNOTATION_KEY] = annotations

    return generated_uuid


def get_documents(value):
    """given a registered UUID, return the related documents or None if it does not exist"""

    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    return annotations.get(value, None)


def get_document_by_uid_and_lang(uid, language):
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())
    for k, v in annotations.items():
        if v.get(language, "") == uid:
            return k

    return None


def delete_document(value):
    """given a registered UUID, delete it from the annotation and return True
    if it was correctly deleted or False if not.
    """
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    if value in annotations:
        del annotations[value]
        annotated[ANNOTATION_KEY] = annotations
        return True

    return False


def get_file_contents(url):
    """download the url and return the contents in a base64 encoded string"""
    if url:
        try:
            data = requests.get(url, verify=False)
            if data.ok:
                return safe_text(base64.urlsafe_b64encode(data.content))
        except Exception as e:
            from logging import getLogger

            log = getLogger(__name__)
            log.info(e)
    return ""
