from BTrees.OOBTree import OOBTree
from datetime import datetime
from datetime import timezone
from plone import api
from zope.annotation.interfaces import IAnnotations

import uuid


ANNOTATION_KEY = "udala.tablon.archivo_tablon"


def register_file(uid: str, language: str, shared_uid: str | None = None) -> str:
    """register file in an annotation and produce a single identifier"""
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    generated_uuid = shared_uid
    if generated_uuid is None:
        generated_uuid = get_file_by_uid_and_lang(uid, language)

    if generated_uuid is None:
        generated_uuid = uuid.uuid4().hex
        while generated_uuid in annotations:
            generated_uuid = uuid.uuid4().hex

    data = annotations.get(
        generated_uuid,
        {
            "translations": {},
            "date": datetime.now(timezone.utc).isoformat(),
        },
    )

    data["translations"][language] = uid

    annotations[generated_uuid] = data
    annotated[ANNOTATION_KEY] = annotations

    return generated_uuid


def get_file(value):
    """given a registered UUID, return the related file or None if it does not exist"""

    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    return annotations.get(value, None)


def get_file_by_uid_and_lang(uid, language):
    if not uid:
        return None

    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())
    for k, v in annotations.items():
        translations = v.get("translations", {})
        if translations.get(language) == uid:
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
