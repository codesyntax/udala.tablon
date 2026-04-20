"""Init and utils."""

from zope.i18nmessageid import MessageFactory

import logging


_ = MessageFactory("udala.tablon")


__version__ = "1.0.0a0"

PACKAGE_NAME = "udala.tablon"


logger = logging.getLogger(PACKAGE_NAME)
