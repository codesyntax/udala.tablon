from BTrees.OOBTree import OOBTree
from datetime import datetime, UTC
from plone import api
from zope.annotation.interfaces import IAnnotations

import uuid


ANNOTATION_KEY = "udala.tablon.archivo_tablon"


def register_file(file_eu, file_es):
    """register file in an annotation and produce a single identifier"""
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    # Check whether this file is already added.
    generated_uuid = get_file_by_uid_and_lang(file_eu, "eu")
    if generated_uuid is None:
        generated_uuid = uuid.uuid4().hex
        while generated_uuid in annotations:
            generated_uuid = uuid.uuid4().hex

    old_file_eu = annotations.get(generated_uuid, {}).get("eu")
    old_file_es = annotations.get(generated_uuid, {}).get("es")
    date = annotations.get(generated_uuid, {}).get(
        "date", datetime.now(UTC).isoformat()
    )

    annotations[generated_uuid] = {
        "eu": old_file_eu or file_eu,
        "es": old_file_es or file_es,
        "date": date,
    }

    annotated[ANNOTATION_KEY] = annotations

    return generated_uuid


def get_file(value):
    """given a registered UUID, return the related file or None if it does not exist"""

    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    return annotations.get(value, None)


def get_file_by_uid_and_lang(uid, language):
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())
    for k, v in annotations.items():
        if v.get(language, "") == uid:
            return k

    return None


def delete_file(value):
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
