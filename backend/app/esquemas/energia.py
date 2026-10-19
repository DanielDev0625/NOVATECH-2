# · Esquemas de eficiencia energética: consumos y tarifas eléctricas.
from typing import Optional

from pydantic import BaseModel


class ConsumoIn(BaseModel):
    maquina: str
    proceso: str
    lote_codigo: Optional[str] = None
    kwh: float
    tarifa_kwh: float


class TarifaIn(BaseModel):
    # · Franja horaria con su precio por kWh.
    nombre: str
    hora_inicio: int
    hora_fin: int
    valor_kwh: float
