# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from udala.tablon import _
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


OriginVocabulary = SimpleVocabulary([
    SimpleTerm(value="external", token="external", title=_("External")),  # noqa: S106
    SimpleTerm(value="internal", token="internal", title=_("Internal")),  # noqa: S106
])


class IDocumentoTablon(model.Schema):
    """Marker interface and Dexterity Python Schema for DocumentoTablon"""

    origin = schema.Choice(
        title=_("Origin of the document"),
        vocabulary=OriginVocabulary,
        required=True,
    )

    origin_department = schema.TextLine(
        title=_("Origin department of the document"), required=False
    )

    origin_details = schema.TextLine(
        title=_("Details about the origin of the document"), required=False
    )

    publication_url = schema.TextLine(
        title=_("Document publication URL"),
        description=_(
            "The document can be external, thus you can provide its URL here"
        ),
        required=False,
    )


@implementer(IDocumentoTablon)
class DocumentoTablon(Container):
    """Content-type class for IDocumentoTablon"""
