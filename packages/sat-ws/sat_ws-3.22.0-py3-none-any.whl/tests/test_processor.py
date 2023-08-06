from unittest import mock

from mx_edi.core import CFDI
from mx_edi.processors.efos import EFOSProcessor
from mx_edi.processors.static import StaticProcessor


def test_static_processor_with_errors(cfdi_with_errors: CFDI):
    processor = StaticProcessor()
    processor.process(cfdi_with_errors)
    rules = cfdi_with_errors.extras["static_rules"]
    assert rules["TipoDeComprobante_I_MetodoPago_PPD"] is True
    assert rules["TipoDeComprobante_I_MetodoPago_PUE"] is False
    assert rules["TipoDeComprobante_E_MetodoPago_PPD"] is False
    assert rules["TipoDeComprobante_E_CfdiRelacionados_None"] is False


def test_static_processor_no_errors(cfdi_xml_example: CFDI):
    processor = StaticProcessor()
    processor.process(cfdi_xml_example)
    rules = cfdi_xml_example.extras["static_rules"]
    assert rules["TipoDeComprobante_I_MetodoPago_PPD"] is False
    assert rules["TipoDeComprobante_I_MetodoPago_PUE"] is False
    assert rules["TipoDeComprobante_E_MetodoPago_PPD"] is False
    assert rules["TipoDeComprobante_E_CfdiRelacionados_None"] is False


@mock.patch("mx_edi.processors.efos.requests.get")
def test_efos_download(mock_get):
    with open("tests/downloads/efos/presumed.csv", "rb") as f:
        mock_get.return_value.content = f.read()
        processor = EFOSProcessor()
        assert processor._black_list_definitive is not None
        assert processor._black_list_presumed is not None


def test_efos_definitive_processor(
    black_list_definitive, black_list_presumed, cfdi_merge_example: CFDI, rfc_efos_definitive: str
):
    cfdi_merge_example.RfcEmisor = rfc_efos_definitive
    processor = EFOSProcessor(black_list_definitive, black_list_presumed)
    processor.process(cfdi_merge_example)
    assert cfdi_merge_example.extras["efos"]["status"] == "Definitive"


def test_efos_presumed_processor(
    black_list_definitive, black_list_presumed, cfdi_merge_example: CFDI, rfc_efos_presumed: str
):
    cfdi_merge_example.RfcEmisor = rfc_efos_presumed
    processor = EFOSProcessor(black_list_definitive, black_list_presumed)
    processor.process(cfdi_merge_example)
    assert cfdi_merge_example.extras["efos"]["status"] == "Presumed"


def test_efos_ok_processor(black_list_definitive, black_list_presumed, cfdi_merge_example: CFDI):
    processor = EFOSProcessor(black_list_definitive, black_list_presumed)
    processor.process(cfdi_merge_example)
    assert cfdi_merge_example.extras["efos"]["status"] == "Ok"
