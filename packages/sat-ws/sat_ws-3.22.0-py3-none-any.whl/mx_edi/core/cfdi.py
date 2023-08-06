import logging
from dataclasses import dataclass, field, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .concepto import Concepto


@dataclass
class CFDI:
    UUID: str
    Fecha: datetime
    Total: float
    # XML fields
    Version: Optional[str] = None
    Sello: Optional[str] = None
    UsoCFDIReceptor: Optional[str] = None
    RegimenFiscalEmisor: Optional[str] = None
    CondicionesDePago: Optional[str] = None
    CfdiRelacionados: Set[str] = field(default_factory=set)
    Folio: Optional[str] = None
    Serie: Optional[str] = None
    NoCertificado: Optional[str] = None
    Certificado: Optional[str] = None
    TipoDeComprobante: Optional[str] = None
    LugarExpedicion: Optional[str] = None
    FormaPago: Optional[str] = None
    MetodoPago: Optional[str] = None
    Moneda: Optional[str] = None
    TipoCambio: Optional[float] = None
    SubTotal: Optional[float] = None
    Conceptos: List[Concepto] = field(default_factory=list)
    xml: Optional[str] = None
    Exportacion: str = ""
    Periodicidad: str = ""
    Meses: str = ""
    # CSV Fields
    RfcEmisor: Optional[str] = None
    NombreEmisor: Optional[str] = None
    RfcReceptor: Optional[str] = None
    NombreReceptor: Optional[str] = None
    RfcPac: Optional[str] = None
    FechaCertificacionSat: Optional[datetime] = None
    EfectoComprobante: Optional[str] = None
    Estatus: Optional[str] = None
    FechaCancelacion: Optional[datetime] = None
    # Extras
    _extras: Dict[str, Any] = field(default_factory=dict)
    cfdis_related: Set["CFDI"] = field(default_factory=set)

    @property
    def extras(self) -> Dict[str, Any]:
        return self._extras or {}

    def add_extra(self, key: str, value: Any):
        self._extras[key] = value

    def clean_extras(self):
        self._extras = {}

    def __post_init__(self):
        self.CfdiRelacionados = set(self.CfdiRelacionados or {})
        self.cfdis_related = set()
        self._extras = dict(self._extras or {})
        self.UUID = self.UUID.upper()

    def __bool__(self):
        return bool(self.UUID)

    def merge(self, other: "CFDI"):
        for attrib, value in self.__dict__.items():
            if other_value := getattr(other, attrib):
                if value and value != other_value:
                    logging.debug("Inconsistent Information '%s' != '%s'", value, other_value)
                setattr(self, attrib, other_value)

    def to_dict(self) -> Dict[str, Any]:
        dict_repr: Dict[str, Any] = {}

        def _to_dict(dict_repr, obj):
            for f in obj.__dataclass_fields__.values():
                if not f.init:
                    continue
                value = getattr(obj, f.name)
                if not value:
                    continue
                if isinstance(value, list):
                    dict_repr[f.name] = [_to_dict({}, item) for item in value]
                elif is_dataclass(value):
                    dict_repr[f.name] = _to_dict({}, value)
                else:
                    dict_repr[f.name] = value
            return dict_repr

        _to_dict(dict_repr, self)
        return dict_repr

    @classmethod
    def reduce(cls, cfdis: List["CFDI"]) -> List["CFDI"]:
        by_uuid: Dict[str, List["CFDI"]] = {}
        for cfdi in cfdis:
            if cfdi.UUID not in by_uuid:
                by_uuid[cfdi.UUID] = []
            by_uuid[cfdi.UUID].append(cfdi)
        for cfdis_by_uuid in by_uuid.values():
            while len(cfdis_by_uuid) > 1:
                cfdi = cfdis_by_uuid.pop()
                cfdis_by_uuid[0].merge(cfdi)
        return [cfdi for cfdi_g in by_uuid.values() for cfdi in cfdi_g]

    def __hash__(self):
        return hash(self.UUID)

    def __eq__(self, other):
        return self.UUID == other.UUID

    def add_related(self, cfdfis: Dict[str, "CFDI"]):
        self.__post_init__()
        for uuid in self.CfdiRelacionados:
            if uuid in cfdfis:
                self.cfdis_related.add(cfdfis[uuid])
