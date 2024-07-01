# -*- coding: utf-8 -*-
import base64
import uuid
from datetime import datetime

import requests
from BTrees.OOBTree import OOBTree
from plone import api
from zope.annotation.interfaces import IAnnotations

ANNOTATION_KEY = "eibarkoudala.tablon.documento_tablon"


def register_documents(documento_eu, documento_es, files_eu, files_es):
    """register documents in an annotation and produce a single identifier"""
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    generated_uuid = uuid.uuid4().hex
    while generated_uuid in annotations:
        generated_uuid = uuid.uuid4().hex

    annotations[generated_uuid] = {
        "eu": documento_eu,
        "es": documento_es,
        "files_eu": files_eu,
        "files_es": files_es,
        "date": datetime.now().isoformat(),
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
                return base64.urlsafe_b64encode(data.content)
        except Exception as e:
            pass
    return ""
