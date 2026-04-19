from udala.tablon.annotations.document import get_document_by_uid_and_lang
from udala.tablon.annotations.document import register_documents
from udala.tablon.utils import is_pam_enabled


try:
    from plone.app.multilingual import api as pamapi
except ImportError:
    pamapi = None


def handler(obj, event):
    """Event handler"""
    language = obj.Language()
    if not language:
        # Failsafe if object hasn't been assigned a language yet
        return

    shared_uid = None

    if is_pam_enabled(obj):
        manager = pamapi.get_translation_manager(obj)
        translations = manager.get_translations()

        # Check if this object is a translation of something that already exists
        for lang, translated_obj in translations.items():
            if lang != language and translated_obj is not None:
                # We found another translation. Let's see if it has a shared UID.
                other_uid = translated_obj.UID()
                existing_shared_uid = get_document_by_uid_and_lang(other_uid, lang)
                if existing_shared_uid:
                    shared_uid = existing_shared_uid
                    break

    # Register sequentially (it will mint a new shared_uid if None is passed)
    register_documents(uid=obj.UID(), language=language, shared_uid=shared_uid)
