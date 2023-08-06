from dataclasses import dataclass
from typing import Optional


@dataclass
class Concepto:
    Descripcion: str
    Cantidad: float
    ValorUnitario: float
    Importe: float
    Descuento: float = 0.0
    TrasladosIVA: float = 0.0
    TrasladosIEPS: float = 0.0
    TrasladosISR: float = 0.0
    RetencionesIVA: float = 0.0
    RetencionesIEPS: float = 0.0
    RetencionesISR: float = 0.0
    ClaveProdServ: Optional[str] = None
    ObjetoImp: Optional[str] = None
