# -*- coding: utf-8 -*-
from udala.tablon.utils import register_documents
from .utils import is_pam_enabled

try:
    from plone.app.multilingual import api as pamapi
except ImportError:
    pamapi = None


def handler(obj, event):
    """Event handler"""
    print("{0} on object {1}".format(event.__class__, obj.absolute_url()))
    if is_pam_enabled(obj):
        manager = pamapi.get_translation_manager(obj)
        eu_object = manager.get_translation("eu")
        es_object = manager.get_translation("es")
        register_documents(eu_object.UID(), es_object.UID(), [], [])
    else:
        register_documents(obj.UID(), None, [], [])
