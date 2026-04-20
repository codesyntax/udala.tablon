from BTrees.OOBTree import OOBTree
from datetime import datetime
from datetime import timezone
from plone import api
from zope.annotation.interfaces import IAnnotations

import uuid


ANNOTATION_KEY = "udala.tablon.documento_tablon"


def register_documents(
    uid: str,
    language: str,
    file_uids: list | None = None,
    shared_uid: str | None = None,
) -> str:
    """register documents in an annotation and produce a single identifier"""
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    if file_uids is None:
        file_uids = []

    generated_uuid = shared_uid
    if generated_uuid is None:
        generated_uuid = get_document_by_uid_and_lang(uid, language)

    if generated_uuid is None:
        generated_uuid = uuid.uuid4().hex
        while generated_uuid in annotations:
            generated_uuid = uuid.uuid4().hex

    data = annotations.get(
        generated_uuid,
        {
            "translations": {},
            "files": [],
            "date": datetime.now(timezone.utc).isoformat(),
        },
    )

    data["translations"][language] = uid
    if file_uids:
        # Avoid duplicate files while preserving order (optional) or just use set
        data["files"] = list(set(data.get("files", []) + file_uids))

    annotations[generated_uuid] = data
    annotated[ANNOTATION_KEY] = annotations

    return generated_uuid


def get_documents(value):
    """given a registered UUID, return the related documents or None if it does not exist"""  # noqa: E501
    portal = api.portal.get()
    annotated = IAnnotations(portal)
    annotations = annotated.get(ANNOTATION_KEY, OOBTree())

    return annotations.get(value, None)


def get_document_by_uid_and_lang(uid, language):
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
