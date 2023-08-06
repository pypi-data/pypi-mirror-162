# pylint: disable=redefined-outer-name
from datetime import datetime
from importlib import resources
from typing import Any, Dict

import pytest

from mx_edi.connectors.sat.certificate_handler import CertificateHandler
from mx_edi.connectors.sat.query import DownloadType, Query, RequestType
from mx_edi.connectors.sat.sat_connector import SATConnector
from mx_edi.connectors.sat.sat_login_handler import SATLoginHandler
from mx_edi.core import CFDI, Concepto

from . import fake_fiel

cert = resources.read_binary(fake_fiel, "EKU9003173C9.cer")
key = resources.read_binary(fake_fiel, "EKU9003173C9.key")
password = resources.read_text(fake_fiel, "EKU9003173C9.txt").encode()


@pytest.fixture
def certificate_handler():
    return CertificateHandler(cert, key, password)


@pytest.fixture
def login_handler(certificate_handler) -> SATLoginHandler:
    return SATLoginHandler(certificate_handler)


@pytest.fixture
def sat_connector():
    return SATConnector(cert, key, password)


query_scenarios = [
    (DownloadType.ISSUED, RequestType.CFDI),
    (DownloadType.RECEIVED, RequestType.CFDI),
    (DownloadType.ISSUED, RequestType.METADATA),
    (DownloadType.RECEIVED, RequestType.METADATA),
]


@pytest.fixture(params=query_scenarios)
def query(request):
    start = datetime.fromisoformat("2021-01-01T00:00:00")
    end = datetime.fromisoformat("2021-05-01T00:00:00")
    download_type = request.param[0]
    request_type = request.param[1]
    return Query(download_type, request_type, start=start, end=end)


@pytest.fixture
def zip_cfdi() -> bytes:
    with open("tests/downloads/B2A5BB69-D460-4FAD-8482-6E5E2E81843A_01.zip", "rb") as zipfile:
        return zipfile.read()


@pytest.fixture
def zip_cfdi_40() -> bytes:
    with open("tests/downloads/INV-INV_2022_0002-MX-EDI.zip", "rb") as zipfile:
        return zipfile.read()


@pytest.fixture
def zip_metadata() -> bytes:
    with open("tests/downloads/195B748C-0091-4558-8DE8-9A37CBA3F42A_01.zip", "rb") as zipfile:
        return zipfile.read()


@pytest.fixture
def cfdi_with_errors() -> CFDI:
    return CFDI(
        Version="3.3",
        Sello="FB3aQY2smIYqF3dzhioX8AkitlbPlrZomug/1G2r57yGkHdd+k0TkUm5ymPmphxa8WsWa7vzwNtsO1PqRowUObwmIzBiQhWiwfO/STuLLi9UZlJNdVHjbUWURpr30sz3qpP2/Wtw7AYtfQc9f89Sqx0pkMS86P9nGBoeLcM8AqsSpOaO+KvkUDFcOwBIeW7EzQSMqdUTPlTB9Ult2JwU9M35Yny9DdAoaQWK2LAW3TJK1JHf2SMpHW5G3jRXr+gxDa/LwtWRjwoNN+C1NVz8JS/AmCW2kBKFa5Due34U3i+qYhOzP20eXb/wI1DSV4zC2TO6DxVcvyDBJPlGA4Ng0A==",
        UsoCFDIReceptor="G03",
        RegimenFiscalEmisor="621",
        UUID="2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9",
        CondicionesDePago="30 días",
        Fecha=datetime(2021, 2, 22, 14, 17, 38),
        Total=29000.00,
        CfdiRelacionados=set(),
        Folio="3",
        Serie="INV/2021/",
        NoCertificado="00001000000503989239",
        Certificado="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",
        TipoDeComprobante="I",
        LugarExpedicion="44259",
        FormaPago="03",
        MetodoPago="PPD",
        Moneda="MXN",
        TipoCambio=None,
        SubTotal=25000.00,
        Conceptos=[
            Concepto(
                Descripcion="Desarrollo de Software - Plataforma EzBill",
                Cantidad=1.0,
                ValorUnitario=25000.0,
                Importe=25000.0,
            )
        ],
        xml='\ufeff<?xml version="1.0" encoding="UTF-8"?>\n<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd" Version="3.3" Sello="FB3aQY2smIYqF3dzhioX8AkitlbPlrZomug/1G2r57yGkHdd+k0TkUm5ymPmphxa8WsWa7vzwNtsO1PqRowUObwmIzBiQhWiwfO/STuLLi9UZlJNdVHjbUWURpr30sz3qpP2/Wtw7AYtfQc9f89Sqx0pkMS86P9nGBoeLcM8AqsSpOaO+KvkUDFcOwBIeW7EzQSMqdUTPlTB9Ult2JwU9M35Yny9DdAoaQWK2LAW3TJK1JHf2SMpHW5G3jRXr+gxDa/LwtWRjwoNN+C1NVz8JS/AmCW2kBKFa5Due34U3i+qYhOzP20eXb/wI1DSV4zC2TO6DxVcvyDBJPlGA4Ng0A==" Fecha="2021-02-22T14:17:38" Folio="3" Serie="INV/2021/" FormaPago="03" NoCertificado="00001000000503989239" Certificado="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" CondicionesDePago="30 días" SubTotal="25000.00" Moneda="MXN" Total="29000.00" TipoDeComprobante="I" MetodoPago="PPD" LugarExpedicion="44259"><cfdi:Emisor Rfc="NAPM9608096N8" Nombre="Navarro Presas Moisés Alejandro" RegimenFiscal="621" /><cfdi:Receptor Rfc="PGD1009214W0" Nombre="PLATAFORMA GDL S  DE RL DE CV" UsoCFDI="G03" /><cfdi:Conceptos><cfdi:Concepto ClaveProdServ="81111507" Cantidad="1.000000" ClaveUnidad="H87" Unidad="Unidades" Descripcion="Desarrollo de Software - Plataforma EzBill" ValorUnitario="25000.00" Importe="25000.00"><cfdi:Impuestos><cfdi:Traslados><cfdi:Traslado Base="25000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="4000.00" /></cfdi:Traslados></cfdi:Impuestos></cfdi:Concepto></cfdi:Conceptos><cfdi:Impuestos TotalImpuestosTrasladados="4000.00"><cfdi:Traslados><cfdi:Traslado Importe="4000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" /></cfdi:Traslados></cfdi:Impuestos><cfdi:Complemento><tfd:TimbreFiscalDigital xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigitalv11.xsd" Version="1.1" SelloCFD="FB3aQY2smIYqF3dzhioX8AkitlbPlrZomug/1G2r57yGkHdd+k0TkUm5ymPmphxa8WsWa7vzwNtsO1PqRowUObwmIzBiQhWiwfO/STuLLi9UZlJNdVHjbUWURpr30sz3qpP2/Wtw7AYtfQc9f89Sqx0pkMS86P9nGBoeLcM8AqsSpOaO+KvkUDFcOwBIeW7EzQSMqdUTPlTB9Ult2JwU9M35Yny9DdAoaQWK2LAW3TJK1JHf2SMpHW5G3jRXr+gxDa/LwtWRjwoNN+C1NVz8JS/AmCW2kBKFa5Due34U3i+qYhOzP20eXb/wI1DSV4zC2TO6DxVcvyDBJPlGA4Ng0A==" NoCertificadoSAT="00001000000504204441" RfcProvCertif="CVD110412TF6" UUID="2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9" FechaTimbrado="2021-02-22T14:17:40" SelloSAT="zsW2IBjkFdoc34+v6qed5unlHPVCRbWke+ocXPhATIF+Sih9XcyAV8ucsocHBTE7irUUV7olBRj7mxPaq+uvTyDp0fiO2yy1G8QfgSEqjxAq7ERw9b5M7Wn1461DHc3utdkWWalj1eXiG4APzKwbDODedE08MLx8ynGsIhEk68udDciPmf4IpPMDRRsEcYWxJqc3jWYoy4a0JgKeofL5ekQCfz8Bd3EaUWMchLlIBDh8VP5Q22VkWjR8ig0ERVmw59BGourLXXmqEspWHuCmpuKLmrrUZdXjAoQY0seKuLNAxYO0JYVVgL8UmPqaIaOZWAb5vV7Ni1HRIBYEDKcHaw==" /></cfdi:Complemento></cfdi:Comprobante>',
        RfcEmisor=None,
        NombreEmisor=None,
        RfcReceptor=None,
        NombreReceptor=None,
        RfcPac=None,
        FechaCertificacionSat=None,
        EfectoComprobante=None,
        Estatus=None,
        FechaCancelacion=None,
    )


@pytest.fixture
def cfdi_xml_example() -> CFDI:
    return CFDI(
        Version="3.3",
        Sello="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==",
        UsoCFDIReceptor="G03",
        RegimenFiscalEmisor="621",
        CfdiRelacionados={"2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9"},
        UUID="FB657B83-4C66-4B45-A352-97BBCA9C1130",
        RfcEmisor="NAPM9608096N8",
        NombreEmisor="Navarro Presas Moisés Alejandro",
        RfcReceptor="PGD1009214W0",
        NombreReceptor="PLATAFORMA GDL S  DE RL DE CV",
        Folio="1",
        Serie="RINV/2021/",
        NoCertificado="00001000000503989239",
        Certificado="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",
        TipoDeComprobante="E",
        Fecha=datetime(2021, 2, 23, 15, 51, 25),
        LugarExpedicion="44259",
        FormaPago="03",
        MetodoPago="PUE",
        Moneda="MXN",
        SubTotal=25000.00,
        Total=29000.00,
        TipoCambio=None,
        Conceptos=[
            Concepto(
                Descripcion="Desarrollo de Software - Plataforma EzBill",
                Cantidad=1.00,
                ValorUnitario=25000.00,
                Importe=25000.00,
                TrasladosIVA=4000.00,
            )
        ],
        xml='\ufeff<?xml version="1.0" encoding="UTF-8"?>\n<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd" Version="3.3" Sello="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==" Fecha="2021-02-23T15:51:25" Folio="1" Serie="RINV/2021/" FormaPago="03" NoCertificado="00001000000503989239" Certificado="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" SubTotal="25000.00" Moneda="MXN" Total="29000.00" TipoDeComprobante="E" MetodoPago="PUE" LugarExpedicion="44259"><cfdi:CfdiRelacionados TipoRelacion="01"><cfdi:CfdiRelacionado UUID="2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9" /></cfdi:CfdiRelacionados><cfdi:Emisor Rfc="NAPM9608096N8" Nombre="Navarro Presas Moisés Alejandro" RegimenFiscal="621" /><cfdi:Receptor Rfc="PGD1009214W0" Nombre="PLATAFORMA GDL S  DE RL DE CV" UsoCFDI="G03" /><cfdi:Conceptos><cfdi:Concepto ClaveProdServ="81111507" Cantidad="1.000000" ClaveUnidad="H87" Unidad="Unidades" Descripcion="Desarrollo de Software - Plataforma EzBill" ValorUnitario="25000.00" Importe="25000.00"><cfdi:Impuestos><cfdi:Traslados><cfdi:Traslado Base="25000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="4000.00" /></cfdi:Traslados></cfdi:Impuestos></cfdi:Concepto></cfdi:Conceptos><cfdi:Impuestos TotalImpuestosTrasladados="4000.00"><cfdi:Traslados><cfdi:Traslado Importe="4000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" /></cfdi:Traslados></cfdi:Impuestos><cfdi:Complemento><tfd:TimbreFiscalDigital xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigitalv11.xsd" Version="1.1" SelloCFD="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==" NoCertificadoSAT="00001000000504204441" RfcProvCertif="CVD110412TF6" UUID="FB657B83-4C66-4B45-A352-97BBCA9C1130" FechaTimbrado="2021-02-23T15:51:27" SelloSAT="yx37Ne1EqLmQOT2D0ox9OUhqeBVo0Sr+ew5uIVKQemKT1xgI6TH00EBx14CrcX/871qKCEs17hBD+3E3Vl5v/0SF+nDh0KWHqsc2sGKP0XRDuenEK738DJjaQ2p6JfK3T5v7oOlxqvSMPGOKU9jcO2ZyiiywctoTyuUylzNRxUY9DIcwv0NfCwlKyFoTMvO73M2PAoRmSvPsvUKKwBXMktzGCYozBMn5CrxN2912YUQ8f9dbM/p2JhTcwD+g5c+ekePRaFPjbZS92K80UvT8CXTRSZXcyOPrVcQFOHy4ISve0CZh1XdCt3tzvyv0ChI6zsM1zbapSAojJJ2/Fk6Drw==" /></cfdi:Complemento></cfdi:Comprobante>',
    )


@pytest.fixture
def cfdi_xml_example_40() -> CFDI:
    return CFDI(
        Version="4.0",
        Sello="ZhrjSeu1zzZ169fKP0PXuMZp8emFZjSxw01JtR0Z90qciK6GXmnv5ZsMsy7qw46H/gZStdOUQuzqoy8Eh/js61Y/g+YOOQgkdxL7US/DP62nSOsEs72Sjbmp5sgvnlg1ON+usimOvVrWlyfc2sMGQ0D0a/AFyZbvoD7fXM5WwKuol85cSQnlioCTjwbVazc07xgYDlrRYl2epIeky+4qZJL0DiK404fQx+MKYUgcaX0prqkMuLESdNY7asOw1nR7YGeuNK44AS9VFn/AAqTlptiMwdYi8mG9sMrFKzx1FA6gfQRUzsBBTkp+zkwUKLR/jBZt7Ye61IZYXu9o87ichw==",
        UsoCFDIReceptor="G01",
        RegimenFiscalEmisor="621",
        UUID="6fdcadd2-668f-4770-9c87-177498741300",
        RfcEmisor="NAPM9608096N8",
        NombreEmisor="MOISES ALEJANDRO NAVARRO PRESAS",
        RfcReceptor="CACX7605101P8",
        NombreReceptor="XOCHILT CASAS CHAVEZ",
        NoCertificado="00001000000502778985",
        Certificado="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",
        TipoDeComprobante="I",
        Fecha=datetime.fromisoformat("2022-01-31T12:47:10"),
        LugarExpedicion="44259",
        Moneda="MXN",
        SubTotal=847.40,
        Total=982.98,
        Exportacion="03",
        Conceptos=[
            Concepto(
                Cantidad=1.0,
                ClaveProdServ="44111502",
                Descripcion="[DESK0004] Escritorio personalizable (CONFIG) (Aluminio, Negro) 160x80cm, con patas grandes.",
                Importe=800.4,
                ObjetoImp="02",
                TrasladosIVA=128.06,
                ValorUnitario=800.4,
            ),
            Concepto(
                Cantidad=1.0,
                ClaveProdServ="10101501",
                Descripcion="[E-COM10] Cubo de pedal",
                Importe=47.0,
                ObjetoImp="02",
                TrasladosIVA=7.52,
                ValorUnitario=47.0,
            ),
        ],
        xml='<?xml version="1.0" encoding="utf-8"?><cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Fecha="2022-01-31T12:47:10" Sello="ZhrjSeu1zzZ169fKP0PXuMZp8emFZjSxw01JtR0Z90qciK6GXmnv5ZsMsy7qw46H/gZStdOUQuzqoy8Eh/js61Y/g+YOOQgkdxL7US/DP62nSOsEs72Sjbmp5sgvnlg1ON+usimOvVrWlyfc2sMGQ0D0a/AFyZbvoD7fXM5WwKuol85cSQnlioCTjwbVazc07xgYDlrRYl2epIeky+4qZJL0DiK404fQx+MKYUgcaX0prqkMuLESdNY7asOw1nR7YGeuNK44AS9VFn/AAqTlptiMwdYi8mG9sMrFKzx1FA6gfQRUzsBBTkp+zkwUKLR/jBZt7Ye61IZYXu9o87ichw==" NoCertificado="00001000000502778985" Certificado="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" SubTotal="847.4" Moneda="MXN" Total="982.98" TipoDeComprobante="I" Exportacion="03" LugarExpedicion="44259"><cfdi:Emisor Rfc="NAPM9608096N8" Nombre="MOISES ALEJANDRO NAVARRO PRESAS" RegimenFiscal="621" /><cfdi:Receptor Rfc="CACX7605101P8" Nombre="XOCHILT CASAS CHAVEZ" DomicilioFiscalReceptor="10740" RegimenFiscalReceptor="621" UsoCFDI="G01" /><cfdi:Conceptos><cfdi:Concepto ClaveProdServ="44111502" Cantidad="1.0" ClaveUnidad="H87" Descripcion="[DESK0004] Escritorio personalizable (CONFIG) (Aluminio, Negro) 160x80cm, con patas grandes." ValorUnitario="800.4" Importe="800.4" ObjetoImp="02" NoIdentificacion="DESK0004"><cfdi:Impuestos><cfdi:Traslados><cfdi:Traslado Base="800.4" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.16" Importe="128.06" /></cfdi:Traslados></cfdi:Impuestos></cfdi:Concepto><cfdi:Concepto ClaveProdServ="10101501" Cantidad="1.0" ClaveUnidad="H87" Descripcion="[E-COM10] Cubo de pedal" ValorUnitario="47.0" Importe="47.0" ObjetoImp="02" NoIdentificacion="E-COM10"><cfdi:Impuestos><cfdi:Traslados><cfdi:Traslado Base="47.0" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.16" Importe="7.52" /></cfdi:Traslados></cfdi:Impuestos></cfdi:Concepto></cfdi:Conceptos><cfdi:Impuestos TotalImpuestosTrasladados="135.58"><cfdi:Traslados><cfdi:Traslado Base="847.4" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.16" Importe="135.58" /></cfdi:Traslados></cfdi:Impuestos><cfdi:Complemento><tfd:TimbreFiscalDigital xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigitalv11.xsd" Version="1.1" UUID="6fdcadd2-668f-4770-9c87-177498741300" FechaTimbrado="2022-01-31T12:47:12" RfcProvCertif="SPR190613I52" SelloCFD="ZhrjSeu1zzZ169fKP0PXuMZp8emFZjSxw01JtR0Z90qciK6GXmnv5ZsMsy7qw46H/gZStdOUQuzqoy8Eh/js61Y/g+YOOQgkdxL7US/DP62nSOsEs72Sjbmp5sgvnlg1ON+usimOvVrWlyfc2sMGQ0D0a/AFyZbvoD7fXM5WwKuol85cSQnlioCTjwbVazc07xgYDlrRYl2epIeky+4qZJL0DiK404fQx+MKYUgcaX0prqkMuLESdNY7asOw1nR7YGeuNK44AS9VFn/AAqTlptiMwdYi8mG9sMrFKzx1FA6gfQRUzsBBTkp+zkwUKLR/jBZt7Ye61IZYXu9o87ichw==" NoCertificadoSAT="30001000000400002495" SelloSAT="AG1J6lQDwNEx41Ej/ckUOotBk4kQlCGPPy+kPcngNZ3+GbqlapKtPWaAWyHHxu4CzvC/bmZPGmAdObG+WuVKSwrX5vbX7WkH7KCou+7zp8yW14vidpzXwW96UMWGlbjymwODS7etHHFMNoTAFAGmrv528S5IuY3CSrRa1KuP9Gq/FH0vCgwloxxSXuxkapy72WJTgY0Pkw99Vsm3aZmeW3MOoNV0ZV1l8c6Fp+EAaJ+YekxKvbKz0xJ6exsddyi4zspBGtsaPyIZjKmGZrkojm6tlfghiYtQ8QyGv5aDLnO9Jc/nf1rLx+7pko7+TpbxMTQh1dnBiMWvrfAKSkXz2w==" xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" /></cfdi:Complemento></cfdi:Comprobante>',
    )


@pytest.fixture
def cfdi_metadata_example() -> CFDI:
    return CFDI(
        UUID="FB657B83-4C66-4B45-A352-97BBCA9C1130",
        Fecha=datetime(2021, 2, 23, 15, 51, 25),
        Total=29000,
        RfcEmisor="NAPM9608096N8",
        NombreEmisor="Navarro Presas Moisés Alejandro",
        RfcReceptor="PGD1009214W0",
        NombreReceptor="PLATAFORMA GDL S  DE RL DE CV",
        RfcPac="CVD110412TF6",
        FechaCertificacionSat=datetime(2021, 2, 23, 15, 51, 27),
        EfectoComprobante="E",
        Estatus="0",
        FechaCancelacion=datetime(2021, 2, 24, 21, 4, 42),
    )


@pytest.fixture
def cfdi_merge_example() -> CFDI:
    return CFDI(
        Version="3.3",
        Sello="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==",
        UsoCFDIReceptor="G03",
        RegimenFiscalEmisor="621",
        CondicionesDePago=None,
        CfdiRelacionados={"2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9"},
        UUID="FB657B83-4C66-4B45-A352-97BBCA9C1130",
        Folio="1",
        Serie="RINV/2021/",
        NoCertificado="00001000000503989239",
        Certificado="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",
        TipoDeComprobante="E",
        Fecha=datetime(2021, 2, 23, 15, 51, 25),
        LugarExpedicion="44259",
        FormaPago="03",
        MetodoPago="PUE",
        Moneda="MXN",
        SubTotal=25000.00,
        Total=29000.00,
        RfcEmisor="NAPM9608096N8",
        NombreEmisor="Navarro Presas Moisés Alejandro",
        RfcReceptor="PGD1009214W0",
        NombreReceptor="PLATAFORMA GDL S  DE RL DE CV",
        RfcPac="CVD110412TF6",
        FechaCertificacionSat=datetime(2021, 2, 23, 15, 51, 27),
        EfectoComprobante="E",
        Estatus="0",
        FechaCancelacion=datetime(2021, 2, 24, 21, 4, 42),
        TipoCambio=None,
        Conceptos=[
            Concepto(
                Descripcion="Desarrollo de Software - Plataforma EzBill",
                Cantidad=1,
                ValorUnitario=25000,
                Importe=25000,
                Descuento=0,
                TrasladosIVA=4000,
                TrasladosIEPS=0,
                TrasladosISR=0,
                RetencionesIVA=0,
                RetencionesIEPS=0,
                RetencionesISR=0,
            ),
        ],
        xml='\ufeff<?xml version="1.0" encoding="UTF-8"?>\n<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd" Version="3.3" Sello="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==" Fecha="2021-02-23T15:51:25" Folio="1" Serie="RINV/2021/" FormaPago="03" NoCertificado="00001000000503989239" Certificado="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" SubTotal="25000.00" Moneda="MXN" Total="29000.00" TipoDeComprobante="E" MetodoPago="PUE" LugarExpedicion="44259"><cfdi:CfdiRelacionados TipoRelacion="01"><cfdi:CfdiRelacionado UUID="2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9" /></cfdi:CfdiRelacionados><cfdi:Emisor Rfc="NAPM9608096N8" Nombre="Navarro Presas Moisés Alejandro" RegimenFiscal="621" /><cfdi:Receptor Rfc="PGD1009214W0" Nombre="PLATAFORMA GDL S  DE RL DE CV" UsoCFDI="G03" /><cfdi:Conceptos><cfdi:Concepto ClaveProdServ="81111507" Cantidad="1.000000" ClaveUnidad="H87" Unidad="Unidades" Descripcion="Desarrollo de Software - Plataforma EzBill" ValorUnitario="25000.00" Importe="25000.00"><cfdi:Impuestos><cfdi:Traslados><cfdi:Traslado Base="25000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="4000.00" /></cfdi:Traslados></cfdi:Impuestos></cfdi:Concepto></cfdi:Conceptos><cfdi:Impuestos TotalImpuestosTrasladados="4000.00"><cfdi:Traslados><cfdi:Traslado Importe="4000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" /></cfdi:Traslados></cfdi:Impuestos><cfdi:Complemento><tfd:TimbreFiscalDigital xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigitalv11.xsd" Version="1.1" SelloCFD="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==" NoCertificadoSAT="00001000000504204441" RfcProvCertif="CVD110412TF6" UUID="FB657B83-4C66-4B45-A352-97BBCA9C1130" FechaTimbrado="2021-02-23T15:51:27" SelloSAT="yx37Ne1EqLmQOT2D0ox9OUhqeBVo0Sr+ew5uIVKQemKT1xgI6TH00EBx14CrcX/871qKCEs17hBD+3E3Vl5v/0SF+nDh0KWHqsc2sGKP0XRDuenEK738DJjaQ2p6JfK3T5v7oOlxqvSMPGOKU9jcO2ZyiiywctoTyuUylzNRxUY9DIcwv0NfCwlKyFoTMvO73M2PAoRmSvPsvUKKwBXMktzGCYozBMn5CrxN2912YUQ8f9dbM/p2JhTcwD+g5c+ekePRaFPjbZS92K80UvT8CXTRSZXcyOPrVcQFOHy4ISve0CZh1XdCt3tzvyv0ChI6zsM1zbapSAojJJ2/Fk6Drw==" /></cfdi:Complemento></cfdi:Comprobante>',
    )


@pytest.fixture
def cfdi_example_dict() -> Dict[str, Any]:
    return {
        "Version": "3.3",
        "Sello": "fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==",
        "UsoCFDIReceptor": "G03",
        "RegimenFiscalEmisor": "621",
        "CfdiRelacionados": {"2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9"},
        "UUID": "FB657B83-4C66-4B45-A352-97BBCA9C1130",
        "Folio": "1",
        "Serie": "RINV/2021/",
        "NoCertificado": "00001000000503989239",
        "Certificado": "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",
        "TipoDeComprobante": "E",
        "Fecha": datetime(2021, 2, 23, 15, 51, 25),
        "LugarExpedicion": "44259",
        "FormaPago": "03",
        "MetodoPago": "PUE",
        "Moneda": "MXN",
        "SubTotal": 25000.00,
        "Total": 29000.00,
        "RfcEmisor": "NAPM9608096N8",
        "NombreEmisor": "Navarro Presas Moisés Alejandro",
        "RfcReceptor": "PGD1009214W0",
        "NombreReceptor": "PLATAFORMA GDL S  DE RL DE CV",
        "RfcPac": "CVD110412TF6",
        "FechaCertificacionSat": datetime(2021, 2, 23, 15, 51, 27),
        "EfectoComprobante": "E",
        "Estatus": "0",
        "FechaCancelacion": datetime(2021, 2, 24, 21, 4, 42),
        "Conceptos": [
            {
                "Cantidad": 1.00,
                "Descripcion": "Desarrollo de Software - Plataforma EzBill",
                "ValorUnitario": 25000.00,
                "Importe": 25000.00,
                "TrasladosIVA": 4000.00,
            },
        ],
        "xml": '\ufeff<?xml version="1.0" encoding="UTF-8"?>\n<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd" Version="3.3" Sello="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==" Fecha="2021-02-23T15:51:25" Folio="1" Serie="RINV/2021/" FormaPago="03" NoCertificado="00001000000503989239" Certificado="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" SubTotal="25000.00" Moneda="MXN" Total="29000.00" TipoDeComprobante="E" MetodoPago="PUE" LugarExpedicion="44259"><cfdi:CfdiRelacionados TipoRelacion="01"><cfdi:CfdiRelacionado UUID="2BBAD813-2ADE-4F2C-B171-7F0EAEFBEFA9" /></cfdi:CfdiRelacionados><cfdi:Emisor Rfc="NAPM9608096N8" Nombre="Navarro Presas Moisés Alejandro" RegimenFiscal="621" /><cfdi:Receptor Rfc="PGD1009214W0" Nombre="PLATAFORMA GDL S  DE RL DE CV" UsoCFDI="G03" /><cfdi:Conceptos><cfdi:Concepto ClaveProdServ="81111507" Cantidad="1.000000" ClaveUnidad="H87" Unidad="Unidades" Descripcion="Desarrollo de Software - Plataforma EzBill" ValorUnitario="25000.00" Importe="25000.00"><cfdi:Impuestos><cfdi:Traslados><cfdi:Traslado Base="25000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="4000.00" /></cfdi:Traslados></cfdi:Impuestos></cfdi:Concepto></cfdi:Conceptos><cfdi:Impuestos TotalImpuestosTrasladados="4000.00"><cfdi:Traslados><cfdi:Traslado Importe="4000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" /></cfdi:Traslados></cfdi:Impuestos><cfdi:Complemento><tfd:TimbreFiscalDigital xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigitalv11.xsd" Version="1.1" SelloCFD="fAixaFxS9Y7snLVXzC39FdjLqy7vuLHEsuBPTPxT/aLdaXoHPy2UdAoNgSc4X6MBjmNCCIXmpyPrMG7e2aQgymUs2IyuHIBPciwTA6vjRN6P/W0OUzFtM7hXI5l+96JmYa23rizE0Gn49Hhc4CbP8M0l1atzNVzTRkO8MZ1bIRfB09S025l+OzO3XEa4k1JXVPLmq+2yaktcThIbX4IR/4d8L+ic9I4NhjGIN8lm7cQ6qsNGChHXNQcnBey/58w+ePmYV4/pHQMHPFYR6sjAplVBu1nGrEdMOqkHgF9m98dvenTI/vPkxBFA21g7rUvOO/kz5dVn4Rl6tsXxLHIrRA==" NoCertificadoSAT="00001000000504204441" RfcProvCertif="CVD110412TF6" UUID="FB657B83-4C66-4B45-A352-97BBCA9C1130" FechaTimbrado="2021-02-23T15:51:27" SelloSAT="yx37Ne1EqLmQOT2D0ox9OUhqeBVo0Sr+ew5uIVKQemKT1xgI6TH00EBx14CrcX/871qKCEs17hBD+3E3Vl5v/0SF+nDh0KWHqsc2sGKP0XRDuenEK738DJjaQ2p6JfK3T5v7oOlxqvSMPGOKU9jcO2ZyiiywctoTyuUylzNRxUY9DIcwv0NfCwlKyFoTMvO73M2PAoRmSvPsvUKKwBXMktzGCYozBMn5CrxN2912YUQ8f9dbM/p2JhTcwD+g5c+ekePRaFPjbZS92K80UvT8CXTRSZXcyOPrVcQFOHy4ISve0CZh1XdCt3tzvyv0ChI6zsM1zbapSAojJJ2/Fk6Drw==" /></cfdi:Complemento></cfdi:Comprobante>',
    }


@pytest.fixture
def rfc_efos_definitive() -> str:
    return "AAA120730823"


@pytest.fixture
def rfc_efos_presumed() -> str:
    return "AABR711124971"


@pytest.fixture
def black_list_definitive():
    return {
        "AAA120730823": {
            "no": "1",
            "rfc": "AAA120730823",
            "contributor_name": "ASESORES Y ADMINISTRADORES AGRICOLAS, S. DE R.L. DE C.V.",
        },
        "AAA121206EV5": {
            "no": "2",
            "rfc": "AAA121206EV5",
            "contributor_name": "AMÉRICA ADMINISTRATIVA ARROLLO, S.A. DE CV.",
        },
        "AAA140116926": {
            "no": "3",
            "rfc": "AAA140116926",
            "contributor_name": "AVALOS & ASOCIADOS CONSULTORIA INTEGRAL, S.C.",
        },
        "AAA151209DYA": {
            "no": "4",
            "rfc": "AAA151209DYA",
            "contributor_name": "AYC ADMINISTRACION Y ASESORIA COMERCIAL, S.A. DE C.V.",
        },
        "AAAA620217U54": {
            "no": "5",
            "rfc": "AAAA620217U54",
            "contributor_name": "AMADOR AQUINO JOSÉ AVENAMAR",
        },
        "AAAE910314EJ7": {
            "no": "6",
            "rfc": "AAAE910314EJ7",
            "contributor_name": "ALVARADO ALMARAZ ESTEBAN JACOB",
        },
        "AAAG7012036UA": {
            "no": "7",
            "rfc": "AAAG7012036UA",
            "contributor_name": "ARAGÓN AYALA GRICELDA",
        },
        "AAAJ830204PA9": {
            "no": "8",
            "rfc": "AAAJ830204PA9",
            "contributor_name": "ARAIZA ARAMBULA JUAN CARLOS",
        },
        "AAAL440727T22": {
            "no": "9",
            "rfc": "AAAL440727T22",
            "contributor_name": "ALMANZA ALONZO JOSÉ LUIS",
        },
        "AAAM930220954": {
            "no": "10",
            "rfc": "AAAM930220954",
            "contributor_name": "AMADO ACOSTA MARCOS",
        },
        "AAAT930326EY6": {
            "no": "11",
            "rfc": "AAAT930326EY6",
            "contributor_name": "AMADO AMADO TRINIDAD",
        },
        "AAAV920808B1A": {
            "no": "12",
            "rfc": "AAAV920808B1A",
            "contributor_name": "ADAME ANTONIO VICTOR ALFONSO",
        },
        "AAB1011024L8": {
            "no": "13",
            "rfc": "AAB1011024L8",
            "contributor_name": "ASESORES ADMINISTRATIVOS BAIK S.A. DE C.V.",
        },
        "AABJ650718RI4": {
            "no": "14",
            "rfc": "AABJ650718RI4",
            "contributor_name": "ALCALA BECERRA JUAN MANUEL",
        },
    }


@pytest.fixture
def black_list_presumed():
    return {
        "AABR711124971": {
            "no": "1",
            "rfc": "AABR711124971",
            "contributor_name": "ALMANZA BRAVO ROCIO AMERICA",
        },
        "AABV7103171I6": {
            "no": "2",
            "rfc": "AABV7103171I6",
            "contributor_name": "ALMAGUER BARRIOS VERONICA PATRICIA",
        },
        "AAGN900909G80": {
            "no": "3",
            "rfc": "AAGN900909G80",
            "contributor_name": "AYALA GARCIA NELIDA GABRIELA",
        },
        "AAHV580710NF0": {
            "no": "4",
            "rfc": "AAHV580710NF0",
            "contributor_name": "ARANZABAL HERNANDEZ VICTOR ALFONSO",
        },
        "AAMR7312046L3": {
            "no": "5",
            "rfc": "AAMR7312046L3",
            "contributor_name": "ANASTASIO MEJIA MARIA DEL ROCIO",
        },
        "AAN150226EL2": {
            "no": "6",
            "rfc": "AAN150226EL2",
            "contributor_name": "ADMINISTRADORA ANKARA, S.A. DE C.V.",
        },
        "AAR110929STA": {
            "no": "7",
            "rfc": "AAR110929STA",
            "contributor_name": "AKENBA Y ARAMENI, S.A. DE C.V.",
        },
        "AAS150310NT8": {
            "no": "8",
            "rfc": "AAS150310NT8",
            "contributor_name": "ARRILLE ASOCIADOS, S.A. DE C.V.",
        },
        "AAU070208LB4": {
            "no": "9",
            "rfc": "AAU070208LB4",
            "contributor_name": "AGRUPACIÓN AGRÍCOLA UNIDOS RÍO TONTO, S.C. DE R.L. DE C.V.",
        },
        "AAV040427V27": {
            "no": "10",
            "rfc": "AAV040427V27",
            "contributor_name": "AUTOMOTOR AVANZATO, S.A. DE C.V.",
        },
        "ABA170831PSA": {
            "no": "11",
            "rfc": "ABA170831PSA",
            "contributor_name": "ARRENDADORA BALDER, S.A.P.I. DE C.V.",
        },
        "ABI170928H83": {
            "no": "12",
            "rfc": "ABI170928H83",
            "contributor_name": "E ABILITY, S.A. DE C.V.",
        },
        "ACA0604119X3": {
            "no": "13",
            "rfc": "ACA0604119X3",
            "contributor_name": "AGROEXPORT DE CAMPECHE, S.P.R. DE R.L.",
        },
        "ACI120209FE8": {
            "no": "14",
            "rfc": "ACI120209FE8",
            "contributor_name": "ANÁLISIS CULTURAL E INTELECTUAL DE PERSONAL, S.A. DE C.V.",
        },
    }
