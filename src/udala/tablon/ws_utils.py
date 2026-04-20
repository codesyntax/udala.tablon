from contextlib import contextmanager
from io import BytesIO
from logging import getLogger
from plone import api
from requests_pkcs12 import get as pkcs12_get
from requests_pkcs12 import post as pkcs12_post
from suds.client import Client

import base64
import functools
import os
import requests
import socket
import suds.transport as transport
import tempfile
import traceback


log = getLogger(__name__)


# DEVELOPMENT
# wsdl_url = "https://epublicaciondes.izenpe.com:8445/constancia_publicacion/services/IzenpeConstanciaPub?wsdl"
# PRODUCTION
# wsdl_url = "https://epublicacion.izenpe.com:8445/constancia_publicacion/services/IzenpeConstanciaPub?wsdl"


def handle_errors(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.HTTPError as e:
            buf = BytesIO(e.response.content)
            raise transport.TransportError(
                "Error in requests\n" + traceback.format_exc(),
                e.response.status_code,
                buf,
            ) from e
        except requests.RequestException as e:
            buf = BytesIO(traceback.format_exc().encode("utf-8"))
            raise transport.TransportError(
                "Error in requests\n" + traceback.format_exc(),
                000,
                buf,
            ) from e

    return wrapper


class RequestsTransport(transport.Transport):
    """
    A special transport to be used with requests that handles connection authorization
    using p12 certificate files
    """

    def __init__(self, session=None, pkcs12_file=None, pkcs12_pass=None, verify=False):
        transport.Transport.__init__(self)
        self._session = session or requests.Session()
        self.pkcs12_file = pkcs12_file
        self.pkcs12_pass = pkcs12_pass
        self.verify = verify

    @handle_errors
    def open(self, request):
        if self.pkcs12_file and self.pkcs12_pass:
            resp = pkcs12_get(
                request.url,
                pkcs12_filename=self.pkcs12_file,
                pkcs12_password=self.pkcs12_pass,
                verify=self.verify,
            )
        else:
            resp = self._session.get(request.url, verify=self.verify)
        resp.raise_for_status()
        return BytesIO(resp.content)

    @handle_errors
    def send(self, request):
        if self.pkcs12_file and self.pkcs12_pass:
            resp = pkcs12_post(
                request.url,
                data=request.message,
                pkcs12_filename=self.pkcs12_file,
                pkcs12_password=self.pkcs12_pass,
                headers=request.headers,
                verify=self.verify,
            )
        else:
            resp = self._session.post(
                request.url,
                data=request.message,
                headers=request.headers,
            )
        if resp.headers.get("content-type") not in (
            "text/xml",
            "application/soap+xml",
        ):
            resp.raise_for_status()
        return transport.Reply(
            resp.status_code,
            resp.headers,
            resp.content,
        )


@contextmanager
def get_suds_client():
    """return a suds client prepared to use p12 file based connection.
    this works as a contextmanager so it should be used in a `with`
    statement.

    This way we can provide a simple way to cleanup any temporary
    file we are creating to handle the connection using p12 certificates
    """
    wsdl_url = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.accrediterendpointurl"
    )

    pkcs_12_file_contents_b64 = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.pkcs12_file_content_b64"
    )
    pkcs_12_file_pass = api.portal.get_registry_record(
        "udala.tablon.udala_tablon_control_panel.pkcs12_file_password"
    )

    p12file_contents = base64.b64decode(pkcs_12_file_contents_b64)
    p12file_tempfile_path = create_temporary_file(p12file_contents)

    headers = {"Content-Type": "text/xml;charset=UTF-8", "SOAPAction": ""}
    t = RequestsTransport(
        session=None,
        pkcs12_file=p12file_tempfile_path,
        pkcs12_pass=pkcs_12_file_pass,
        verify=False,
    )
    try:
        yield Client(wsdl_url, headers=headers, transport=t)
    finally:
        os.remove(p12file_tempfile_path)


def create_temporary_file(contents):
    """create a temporary file and return its path"""
    filehandle, filepath = tempfile.mkstemp()
    os.write(filehandle, contents)
    os.close(filehandle)
    return filepath


def post_document_to_izenpe(  # noqa: C901
    url: str,  # url of the document
    title: str,  # title of the document
    revision_date: str,  # final revision date
    extension: str,  # extension of the document
    language: str,  # language
):
    """post the document to be certified to Izenpe"""

    try:
        ip = socket.gethostbyaddr(url.split("/")[2])[2][0]
    except Exception as e:
        log.info(e)
        ip = "127.0.0.1"

    port = (url.startswith("https:") and 443) or 80
    security = url.startswith("https:")

    result = 0
    errormessage = ""
    accredited_url = ""
    with get_suds_client() as client:
        encoded_url = base64.urlsafe_b64encode(url.encode("utf-8"))

        data = client.service.constancia(
            mi_url=encoded_url.decode(),
            mi_ip=ip,
            mi_puerto=port,
            mi_seguridad=security,
            mi_titulo=title,
            mi_fecharevision=revision_date,
            mi_tipo_firma=extension,
        )

        accredited_url = None
        errorcode = None
        errormessage = None

        log.info("Izenpe result: %s", data)

        for item in data.item:
            if item.key == "tipo" and item.value == "error":
                # Handle error
                for item2 in data.item:
                    if (language == "eu" and item2.key == "msjerror_eus") or (
                        language == "es" and item2.key == "msjerror_cas"
                    ):
                        errorcode = item.value
                        errormessage = item2.value
                    elif language not in ["eu", "es"] and item2.key == "coderror":
                        errorcode = item2.value

            elif item.key == "tipo" and item.value == "url":
                for item2 in data.item:
                    if item2.key == "url_pdf":
                        accredited_url = item2.value
                        result = 1

        if errorcode is not None:
            result = errorcode

    to_return = {"status": result, "message": errormessage, "url": accredited_url}

    log.info("Response: %s", to_return)

    return to_return
