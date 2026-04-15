from plone.base.utils import get_installer


def is_pam_enabled(context):
    installer = get_installer(context)
    return installer.is_product_installed("plone.app.multilingual")
