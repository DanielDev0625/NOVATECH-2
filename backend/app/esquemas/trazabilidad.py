# · Esquemas de trazabilidad: lotes y sus etapas.
from typing import Optional

from pydantic import BaseModel


class LoteIn(BaseModel):
    # · Datos para registrar un lote nuevo.
    producto: str
    cantidad: float
    unidad: str = "unidades"
    responsable: str = ""


class EtapaIn(BaseModel):
    # · Campos que se pueden actualizar de una etapa; todos son opcionales.
    responsable: Optional[str] = None
    control_calidad: Optional[bool] = None
    observaciones: Optional[str] = None
    completada: Optional[bool] = None
