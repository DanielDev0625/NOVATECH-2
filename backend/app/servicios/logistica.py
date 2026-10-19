# · Lógica de negocio de logística: distancias, sugerencias de transporte, rutas y pedidos.
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.configuracion import CIUDADES, COMISION, ESTADOS_PEDIDO
from app.esquemas.logistica import EstadoIn, PedidoIn, RutaIn, VehiculoIn
from app.modelos_db import Pedido, Transportista, Vehiculo, ahora
from app.modelos_poo.ciudad import CatalogoCiudades
from app.modelos_poo.ruta import PlanificadorRuta
from app.servicios.lotes import lote_por_codigo

# · Catálogo de ciudades construido una sola vez con la configuración.
catalogo = CatalogoCiudades(CIUDADES)


def distancia_km(origen: str, destino: str) -> float:
    if not (catalogo.existe(origen) and catalogo.existe(destino)):
        raise HTTPException(400, "Ciudad no reconocida")
    return catalogo.obtener(origen).distancia_a(catalogo.obtener(destino))


# · El planificador usa la función distancia_km de arriba.
planificador = PlanificadorRuta(distancia_km)


def optimizar_ruta(d: RutaIn) -> dict:
    return planificador.vecino_mas_cercano(d.origen, d.destinos)


def crear_vehiculo(db: Session, d: VehiculoIn) -> Vehiculo:
    if not db.get(Transportista, d.transportista_id):
        raise HTTPException(404, "Transportista no encontrado")
    if db.query(Vehiculo).filter(Vehiculo.placa == d.placa.upper()).first():
        raise HTTPException(400, "La placa ya existe")
    v = Vehiculo(**{**d.model_dump(), "placa": d.placa.upper()})
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def sugerencias(db: Session, origen: str, destino: str, peso_kg: float) -> dict:
    dist = distancia_km(origen, destino)
    opciones = []
    # · Por cada transportista disponible, elige su vehículo más pequeño que aguante el peso.
    for t in db.query(Transportista).filter(Transportista.disponible.is_(True)).all():
        vs = [v for v in t.vehiculos if v.disponible and v.capacidad_kg >= peso_kg]
        if vs:
            v = min(vs, key=lambda x: x.capacidad_kg)
            opciones.append({"transportista_id": t.id, "transportista": t.nombre,
                             "vehiculo_id": v.id, "placa": v.placa,
                             "capacidad_kg": v.capacidad_kg, "valoracion": t.valoracion,
                             "costo": round(dist * t.costo_km)})
    if opciones:
        # · Puntaje: 50 % valoración del transportista + 50 % qué tan barato es frente al más caro.
        mx = max(o["costo"] for o in opciones) or 1
        for o in opciones:
            o["puntaje"] = round(0.5 * o["valoracion"] / 5 + 0.5 * (1 - o["costo"] / mx), 3)
        opciones.sort(key=lambda o: o["puntaje"], reverse=True)
    return {"distancia_km": dist, "opciones": opciones}


def crear_pedido(db: Session, d: PedidoIn) -> Pedido:
    lote = lote_por_codigo(db, d.lote_codigo) if d.lote_codigo else None
    dist = distancia_km(d.origen, d.destino)
    tarifa = 0.0
    if d.transportista_id:
        t = db.get(Transportista, d.transportista_id)
        if not t:
            raise HTTPException(404, "Transportista no encontrado")
        tarifa = round(dist * t.costo_km)
    p = Pedido(lote_id=lote.id if lote else None, cliente=d.cliente, origen=d.origen,
               destino=d.destino, peso_kg=d.peso_kg, distancia_km=dist,
               transportista_id=d.transportista_id, vehiculo_id=d.vehiculo_id,
               tarifa=tarifa, comision=round(tarifa * COMISION))
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def cambiar_estado(db: Session, pedido_id: int, d: EstadoIn) -> None:
    if d.estado not in ESTADOS_PEDIDO:
        raise HTTPException(400, "Estado no válido")
    p = db.get(Pedido, pedido_id)
    if not p:
        raise HTTPException(404, "Pedido no encontrado")
    p.estado = d.estado
    # · Al entregarse se registra la fecha; si se cambia a otro estado, se borra.
    p.entregado_en = ahora() if d.estado == "Entregado" else None
    db.commit()
