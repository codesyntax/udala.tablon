from .utils import is_pam_enabled
from Acquisition import aq_parent
from udala.tablon.file_utils import register_file
from udala.tablon.utils import register_documents


try:
    from plone.app.multilingual import api as pamapi
except ImportError:
    pamapi = None


def handler(obj, event):
    """Event handler"""
    print(f"{event.__class__} on object {obj.absolute_url()}")
    if is_pam_enabled(obj):
        manager = pamapi.get_translation_manager(obj)
        eu_object = manager.get_translation("eu")
        es_object = manager.get_translation("es")
        file_uid = register_file(eu_object.UID(), es_object.UID())
        eu_parent = aq_parent(eu_object)
        es_parent = aq_parent(es_object)
        register_documents(eu_parent.UID(), es_parent.UID(), [file_uid], [file_uid])

    else:
        file_uid = register_file(obj.UID(), None)
        parent = aq_parent(obj)
        register_documents(parent.UID(), None, [file_uid], [])
