from .utils import is_pam_enabled
from Acquisition import aq_parent
from udala.tablon.annotations.document import get_document_by_uid_and_lang
from udala.tablon.annotations.document import register_documents
from udala.tablon.annotations.file import get_file_by_uid_and_lang
from udala.tablon.annotations.file import register_file


try:
    from plone.app.multilingual import api as pamapi
except ImportError:
    pamapi = None


def handler(obj, event):
    """Event handler"""
    language = obj.Language()
    if not language:
        return

    shared_file_uid = None

    if is_pam_enabled(obj):
        manager = pamapi.get_translation_manager(obj)
        translations = manager.get_translations()

        # Check if this file is a translation of a file that already exists
        for lang, translated_obj in translations.items():
            if lang != language and translated_obj is not None:
                other_uid = translated_obj.UID()
                existing_shared_uid = get_file_by_uid_and_lang(other_uid, lang)
                if existing_shared_uid:
                    shared_file_uid = existing_shared_uid
                    break

    # Register the file sequentially
    file_uid = register_file(
        uid=obj.UID(), language=language, shared_uid=shared_file_uid
    )

    # Bubble up to the parent DocumentoTablon
    parent = aq_parent(obj)
    if parent is not None:
        parent_lang = parent.Language()
        parent_uid = parent.UID()

        # Check if parent is registered already
        parent_shared_uid = get_document_by_uid_and_lang(parent_uid, parent_lang)

        if parent_shared_uid is not None:
            # Append the file ID to the existing document annotation
            register_documents(
                uid=parent_uid,
                language=parent_lang,
                file_uids=[file_uid],
                shared_uid=parent_shared_uid,
            )
        else:
            # Fallback if document wasn't registered for some reason
            register_documents(
                uid=parent_uid,
                language=parent_lang,
                file_uids=[file_uid],
            )
