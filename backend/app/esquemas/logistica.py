# · Esquemas de logística: transportistas, vehículos, pedidos y rutas.
from typing import List, Optional

from pydantic import BaseModel


class TransportistaIn(BaseModel):
    nombre: str
    telefono: str = ""
    valoracion: float = 4.0
    costo_km: float


class VehiculoIn(BaseModel):
    transportista_id: int
    placa: str
    tipo: str = "Camión"
    modelo: str = ""
    capacidad_kg: float


class PedidoIn(BaseModel):
    # · lote_codigo, transportista_id y vehiculo_id son opcionales.
    lote_codigo: Optional[str] = None
    cliente: str
    origen: str
    destino: str
    peso_kg: float = 0
    transportista_id: Optional[int] = None
    vehiculo_id: Optional[int] = None


class EstadoIn(BaseModel):
    # · Nuevo estado de un pedido (debe estar en ESTADOS_PEDIDO).
    estado: str


class RutaIn(BaseModel):
    # · Origen y lista de destinos a visitar.
    origen: str
    destinos: List[str]
