from dataclasses import asdict
from typing import Any, Dict

from mx_edi.connectors.sat.package_parsers import XML2CFDI, Metadata2CFDI
from mx_edi.core import CFDI


def test_xml2cfdi(zip_cfdi: bytes, cfdi_xml_example: CFDI):
    cfdis = XML2CFDI.from_binary(zip_cfdi)
    assert len(cfdis) == 9
    cfdis[0].clean_extras()
    c1 = asdict(cfdis[0].Conceptos[0])
    c2 = asdict(cfdi_xml_example.Conceptos[0])
    assert c1 == c2
    assert cfdis[0].to_dict() == cfdi_xml_example.to_dict()


def test_xml2cfdi_40(zip_cfdi_40: bytes, cfdi_xml_example_40: CFDI):
    cfdis = XML2CFDI.from_binary(zip_cfdi_40)
    assert len(cfdis) == 1
    c1 = asdict(cfdis[0].Conceptos[0])
    c2 = asdict(cfdi_xml_example_40.Conceptos[0])
    assert c1 == c2
    c1 = asdict(cfdis[0].Conceptos[1])
    c2 = asdict(cfdi_xml_example_40.Conceptos[1])
    assert c1 == c2
    cfdis[0].clean_extras()
    assert cfdis[0].to_dict() == cfdi_xml_example_40.to_dict()


def test_metadata2cfdi(zip_metadata: bytes, cfdi_metadata_example: CFDI):
    cfdis = Metadata2CFDI.from_binary(zip_metadata)
    assert len(cfdis) == 9
    cfdi = cfdis[3]
    assert cfdi.to_dict() == cfdi_metadata_example.to_dict()


def test_merge(cfdi_xml_example: CFDI, cfdi_metadata_example: CFDI, cfdi_merge_example: CFDI):
    cfdi_xml_example.merge(cfdi_metadata_example)
    assert cfdi_xml_example == cfdi_merge_example


def test_convert_to_dict(cfdi_merge_example: CFDI, cfdi_example_dict: Dict[str, Any]):
    dict_repr = cfdi_merge_example.to_dict()
    c1 = dict_repr.pop("Conceptos")[0]
    c2 = cfdi_example_dict.pop("Conceptos")[0]
    assert c1 == c2
    assert dict_repr == cfdi_example_dict
