# · Rutas de logística: transportistas, vehículos, sugerencias, rutas y pedidos.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.esquemas.logistica import (EstadoIn, PedidoIn, RutaIn, TransportistaIn,
                                    VehiculoIn)
from app.modelos_db import Pedido, Transportista, Vehiculo, get_db
from app.servicios import logistica as servicio
from app.servicios.seguridad import usuario_actual

router = APIRouter(prefix="/api", dependencies=[Depends(usuario_actual)])


@router.get("/logistica/ciudades")
def ciudades():
    return servicio.catalogo.nombres()


@router.post("/logistica/transportistas")
def crear_transportista(d: TransportistaIn, db: Session = Depends(get_db)):
    t = Transportista(**d.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id}


@router.get("/logistica/transportistas")
def listar_transportistas(db: Session = Depends(get_db)):
    return [{"id": t.id, "nombre": t.nombre, "telefono": t.telefono,
             "valoracion": t.valoracion, "costo_km": t.costo_km,
             "vehiculos": len(t.vehiculos)} for t in db.query(Transportista).all()]


@router.post("/logistica/vehiculos")
def crear_vehiculo(d: VehiculoIn, db: Session = Depends(get_db)):
    return {"id": servicio.crear_vehiculo(db, d).id}


@router.get("/logistica/vehiculos")
def listar_vehiculos(db: Session = Depends(get_db)):
    return [{"id": v.id, "placa": v.placa, "tipo": v.tipo, "modelo": v.modelo,
             "capacidad_kg": v.capacidad_kg, "transportista_id": v.transportista_id,
             "transportista": v.transportista.nombre} for v in db.query(Vehiculo).all()]


@router.get("/logistica/sugerencias")
def sugerencias(origen: str, destino: str, peso_kg: float = 0, db: Session = Depends(get_db)):
    return servicio.sugerencias(db, origen, destino, peso_kg)


@router.post("/logistica/ruta")
def optimizar_ruta(d: RutaIn):
    return servicio.optimizar_ruta(d)


@router.post("/logistica/pedidos")
def crear_pedido(d: PedidoIn, db: Session = Depends(get_db)):
    return {"id": servicio.crear_pedido(db, d).id}


@router.get("/logistica/pedidos")
def listar_pedidos(db: Session = Depends(get_db)):
    return [{"id": p.id, "lote": p.lote.codigo if p.lote else "", "cliente": p.cliente,
             "origen": p.origen, "destino": p.destino, "distancia_km": p.distancia_km,
             "transportista": p.transportista.nombre if p.transportista else "",
             "placa": p.vehiculo.placa if p.vehiculo else "", "estado": p.estado,
             "tarifa": p.tarifa, "comision": p.comision, "creado_en": p.creado_en}
            for p in db.query(Pedido).order_by(Pedido.id.desc()).all()]


@router.patch("/logistica/pedidos/{pedido_id}/estado")
def cambiar_estado(pedido_id: int, d: EstadoIn, db: Session = Depends(get_db)):
    servicio.cambiar_estado(db, pedido_id, d)
    return {"ok": True}
