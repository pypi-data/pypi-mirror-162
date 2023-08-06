from datetime import datetime
from unittest import mock

import pytest
from aiohttp import request
from lxml import etree
from mx_edi.connectors.sat import query, utils
from mx_edi.connectors.sat.enums import DownloadType, RequestType
from mx_edi.connectors.sat.package import Package
from mx_edi.connectors.sat.query import Query
from mx_edi.connectors.sat.sat_connector import SATConnector
from mx_edi.connectors.sat.sat_login_handler import SATLoginHandler
from mx_edi.connectors.sat.utils import RequestException

from tests.utils import open_test_file


def test_query(query: Query):
    assert query


@pytest.mark.parametrize("download_type", [DownloadType.RECEIVED])
@pytest.mark.parametrize("request_type", [RequestType.CFDI])
@pytest.mark.parametrize("start", [datetime(2020, 1, 1)])  # STATIC DATES
@pytest.mark.parametrize("end", [datetime(2021, 1, 1)])  # STATIC DATES
def test_query_received_cfdi(download_type, request_type, start, end):
    raise NotImplementedError


@mock.patch("mx_edi.connectors.sat.sat_login_handler.SATLoginHandler._token_expired")
@pytest.mark.parametrize("download_type", [DownloadType.RECEIVED])
@pytest.mark.parametrize("request_type", [RequestType.METADATA])
@pytest.mark.parametrize("start", [datetime(2020, 1, 1)])  # STATIC DATES
@pytest.mark.parametrize("end", [datetime(2021, 1, 1)])  # STATIC DATES
def test_query_received_metadata(
    mock_token, download_type, request_type, start, end, sat_connector: SATConnector
):

    sat_connector.login_handler._token = "eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2MjU3OTEyNjMsImV4cCI6MTYyNTc5MTg2MywiaWF0IjoxNjI1NzkxMjYzLCJpc3MiOiJMb2FkU29saWNpdHVkRGVjYXJnYU1hc2l2YVRlcmNlcm9zIiwiYWN0b3J0IjoiMzMzMDMwMzAzMTMwMzAzMDMwMzAzMDM0MzAzMDMwMzAzMjM0MzEzNyJ9.OK15BluJpn4yW9NNuk6QO_DiLVskBgv6-67diyxMsJw%26wrap_subject%3d3330303031303030303030343030303032343137"
    mock_token.return_value = False

    query = Query(download_type, request_type, start=start, end=end)
    xml_generated = query._get_query_xml(sat_connector)
    xml_test = open_test_file("tests/data/request_received_xml.xml")
    assert xml_generated == xml_test


@mock.patch("mx_edi.connectors.sat.utils.requests.post")
@mock.patch("mx_edi.connectors.sat.sat_login_handler.SATLoginHandler._token_expired")
def test_send(mock_token, mock_post, sat_connector: SATConnector):
    start = datetime.fromisoformat("2021-01-01T00:00:00")
    end = datetime.fromisoformat("2021-05-01T00:00:00")
    download_type = DownloadType.ISSUED
    request_type = RequestType.CFDI
    query = Query(download_type, request_type, start=start, end=end)

    sat_connector.login_handler._token = "eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2MjU3OTEyNjMsImV4cCI6MTYyNTc5MTg2MywiaWF0IjoxNjI1NzkxMjYzLCJpc3MiOiJMb2FkU29saWNpdHVkRGVjYXJnYU1hc2l2YVRlcmNlcm9zIiwiYWN0b3J0IjoiMzMzMDMwMzAzMTMwMzAzMDMwMzAzMDM0MzAzMDMwMzAzMjM0MzEzNyJ9.OK15BluJpn4yW9NNuk6QO_DiLVskBgv6-67diyxMsJw%26wrap_subject%3d3330303031303030303030343030303032343137"
    mock_token.return_value = False

    mock_post.return_value.status_code = 200
    mock_post.return_value.content = b'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><SolicitaDescargaResponse xmlns="http://DescargaMasivaTerceros.sat.gob.mx"><SolicitaDescargaResult IdSolicitud="f6434218-0e1f-4c93-996d-54b5fea74cb9" CodEstatus="5000" Mensaje="Solicitud Aceptada"/></SolicitaDescargaResponse></s:Body></s:Envelope>'

    query.send(sat_connector)

    assert query.identifier == "f6434218-0e1f-4c93-996d-54b5fea74cb9"
    assert query.status == 5000


@mock.patch("mx_edi.connectors.sat.utils.requests.post")
@mock.patch("mx_edi.connectors.sat.sat_login_handler.SATLoginHandler._token_expired")
def test_verify(mock_token, mock_post, sat_connector: SATConnector):
    query = Query(
        DownloadType.ISSUED, RequestType.CFDI, identifier="f6434218-0e1f-4c93-996d-54b5fea74cb9"
    )

    sat_connector.login_handler._token = "eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2MjU3OTEyNjMsImV4cCI6MTYyNTc5MTg2MywiaWF0IjoxNjI1NzkxMjYzLCJpc3MiOiJMb2FkU29saWNpdHVkRGVjYXJnYU1hc2l2YVRlcmNlcm9zIiwiYWN0b3J0IjoiMzMzMDMwMzAzMTMwMzAzMDMwMzAzMDM0MzAzMDMwMzAzMjM0MzEzNyJ9.OK15BluJpn4yW9NNuk6QO_DiLVskBgv6-67diyxMsJw%26wrap_subject%3d3330303031303030303030343030303032343137"
    mock_token.return_value = False

    mock_post.return_value.status_code = 200
    mock_post.return_value.content = b'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><VerificaSolicitudDescargaResponse xmlns="http://DescargaMasivaTerceros.sat.gob.mx"><VerificaSolicitudDescargaResult CodEstatus="5000" EstadoSolicitud="3" CodigoEstadoSolicitud="5000" NumeroCFDIs="9" Mensaje="Solicitud Aceptada"><IdsPaquetes>F6434218-0E1F-4C93-996D-54B5FEA74CB9_01</IdsPaquetes></VerificaSolicitudDescargaResult></VerificaSolicitudDescargaResponse></s:Body></s:Envelope>'
    query.verify(sat_connector)
    assert query.query_status == 3
    assert query.message == "Solicitud Aceptada"
    assert query.status_code == 5000
    assert query.cfdi_qty == 9
    assert query.packages[0].identifier == "F6434218-0E1F-4C93-996D-54B5FEA74CB9_01"


@mock.patch("mx_edi.connectors.sat.utils.requests.post")
@mock.patch("mx_edi.connectors.sat.sat_login_handler.SATLoginHandler._token_expired")
def test_download(mock_token, mock_post, sat_connector: SATConnector):
    query = Query(
        DownloadType.ISSUED, RequestType.CFDI, identifier="f6434218-0e1f-4c93-996d-54b5fea74cb9"
    )
    sat_connector.login_handler._token = "eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2MjU3OTEyNjMsImV4cCI6MTYyNTc5MTg2MywiaWF0IjoxNjI1NzkxMjYzLCJpc3MiOiJMb2FkU29saWNpdHVkRGVjYXJnYU1hc2l2YVRlcmNlcm9zIiwiYWN0b3J0IjoiMzMzMDMwMzAzMTMwMzAzMDMwMzAzMDM0MzAzMDMwMzAzMjM0MzEzNyJ9.OK15BluJpn4yW9NNuk6QO_DiLVskBgv6-67diyxMsJw%26wrap_subject%3d3330303031303030303030343030303032343137"
    mock_token.return_value = False

    query.packages = [Package("F6434218-0E1F-4C93-996D-54B5FEA74CB9_01", query.request_type)]
    mock_post.return_value.status_code = 200
    with open("tests/F6434218-0E1F-4C93-996D-54B5FEA74CB9_01.xml", "rb") as f:
        mock_post.return_value.content = f.read()
    query.packages[0].download(sat_connector)
    with open("tests/downloads/F6434218-0E1F-4C93-996D-54B5FEA74CB9_01.zip", "rb") as f:
        assert query.packages[0].binary == f.read()


class FakeLogin:
    created = datetime.fromisoformat("2019-08-01 03:38:19.000")
    expires = datetime.fromisoformat("2019-08-01 03:43:19.000")
    uuid = "uuid-cf6c80fb-00ae-44c0-af56-54ec65decbaa-1"


@mock.patch("mx_edi.connectors.sat.utils.requests.post")
def test_login(mock_post, login_handler: SATLoginHandler):
    mock_post.return_value.status_code = 200
    mock_post.return_value.content = b'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><s:Header><o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><u:Timestamp u:Id="_0"><u:Created>2021-07-09T00:41:03.824Z</u:Created><u:Expires>2021-07-09T00:46:03.824Z</u:Expires></u:Timestamp></o:Security></s:Header><s:Body><AutenticaResponse xmlns="http://DescargaMasivaTerceros.gob.mx"><AutenticaResult>eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2MjU3OTEyNjMsImV4cCI6MTYyNTc5MTg2MywiaWF0IjoxNjI1NzkxMjYzLCJpc3MiOiJMb2FkU29saWNpdHVkRGVjYXJnYU1hc2l2YVRlcmNlcm9zIiwiYWN0b3J0IjoiMzMzMDMwMzAzMTMwMzAzMDMwMzAzMDM0MzAzMDMwMzAzMjM0MzEzNyJ9.OK15BluJpn4yW9NNuk6QO_DiLVskBgv6-67diyxMsJw%26wrap_subject%3d3330303031303030303030343030303032343137</AutenticaResult></AutenticaResponse></s:Body></s:Envelope>'
    login_handler.login(
        created=datetime.fromisoformat("2021-07-09T00:41:03.824000+00:00"),
        expires=datetime.fromisoformat("2021-07-09T00:46:03.824000+00:00"),
        uuid="uuid-25f18c9c-e051-11eb-8030-00d861c7ee71-1",
    )


@mock.patch("mx_edi.connectors.sat.utils.requests.post")
def test_reuse_token(mock_post, login_handler: SATLoginHandler):
    mock_post.return_value.status_code = 200
    mock_post.return_value.content = b'<s:Envelope xmls:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><s:Header><o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><u:Timestamp u:Id="_0"><u:Created>2021-07-09T00:41:03.824Z</u:Created><u:Expires>2021-07-09T00:46:03.824Z</u:Expires></u:Timestamp></o:Security></s:Header><s:Body><AutenticaResponse xmlns="http://DescargaMasivaTerceros.gob.mx"><AutenticaResult>eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2MjU3OTEyNjMsImV4cCI6MTYyNTc5MTg2MywiaWF0IjoxNjI1NzkxMjYzLCJpc3MiOiJMb2FkU29saWNpdHVkRGVjYXJnYU1hc2l2YVRlcmNlcm9zIiwiYWN0b3J0IjoiMzMzMDMwMzAzMTMwMzAzMDMwMzAzMDM0MzAzMDMwMzAzMjM0MzEzNyJ9.OK15BluJpn4yW9NNuk6QO_DiLVskBgv6-67diyxMsJw%26wrap_subject%3d3330303031303030303030343030303032343137</AutenticaResult></AutenticaResponse></s:Body></s:Envelope>'
    login_handler.login(
        created=datetime.fromisoformat("2021-07-09T00:41:03.000000"),
        expires=datetime.fromisoformat("2021-07-09T00:46:03.000000"),
        uuid="uuid-25f18c9c-e051-11eb-8030-00d861c7ee71-1",
    )
    first_token = login_handler.token
    login_handler.login(
        created=datetime.fromisoformat("2021-07-09T00:41:03.000000"),
        expires=datetime.fromisoformat("2021-07-09T00:46:03.000000"),
        uuid="uuid-25f18c9c-e051-11eb-8030-00d861c7ee71-1",
    )
    second_token = login_handler.token
    assert first_token == second_token


@mock.patch("mx_edi.connectors.sat.utils.requests.post")
def test_login_expired(mock_post, login_handler: SATLoginHandler):
    with pytest.raises(RequestException):  # Expired session
        mock_post.return_value.status_code = 300
        login_handler.login(
            created=FakeLogin.created,
            expires=FakeLogin.expires,
            uuid=FakeLogin.uuid,
        )


def test_login2():
    with open("/home/moy/git/sat/tests/data/zeep.xml", "r") as f:
    # with open("/home/moy/git/sat/tests/data/generated.xml", "r") as f:
        f_content = f.read()
        request_content = f_content
    response = utils.consume(
            "http://DescargaMasivaTerceros.gob.mx/IAutenticacion/Autentica",
            "https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/Autenticacion/Autenticacion.svc",
            request_content,
        )
    assert response.status_code == 200
