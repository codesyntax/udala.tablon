from .utils import is_pam_enabled
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
        register_documents(eu_object.UID(), es_object.UID(), [], [])
    else:
        register_documents(obj.UID(), None, [], [])
