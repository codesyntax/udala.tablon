from plone import api


def resolve_plone_uid(annotation_dict, request):
    """safely resolve a shared uid annotation dictionary to a plone object uid"""
    if not annotation_dict:
        return None

    translations = annotation_dict.get("translations", {})
    if not translations:
        return None

    req_lang = request.get("LANGUAGE")
    if not req_lang:
        req_lang = api.portal.get_default_language()

    if req_lang in translations:
        return translations[req_lang]

    # Fallback to the first available language to avoid unnecessary 404s
    return next(iter(translations.values()))
