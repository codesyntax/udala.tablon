from plone.base.utils import safe_text

import base64
import requests


def get_file_contents(url):
    """download the url and return the contents in a base64 encoded string"""
    if url:
        try:
            data = requests.get(url, verify=False, timeout=60)  # noqa: S501
            if data.ok:
                return safe_text(base64.urlsafe_b64encode(data.content))
        except Exception as e:
            from logging import getLogger

            log = getLogger(__name__)
            log.info(e)
    return ""
