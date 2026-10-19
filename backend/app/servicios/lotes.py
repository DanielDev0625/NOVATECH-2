# · Lógica de negocio de trazabilidad: lotes y etapas.
import secrets
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.configuracion import ETAPAS_BASE
from app.esquemas.trazabilidad import EtapaIn, LoteIn
from app.modelos_db import EtapaLote, Lote, ahora


def estado_lote(l: Lote) -> str:
    # · El estado es el de la primera etapa que aún no está completada.
    for e in l.etapas:
        if not e.completada:
            return f"En {e.nombre.lower()}"
    return "Entregado" if l.etapas else "Sin etapas"


def etapa_dict(e: EtapaLote) -> dict:
    # · Convierte una etapa a diccionario para la respuesta JSON.
    return {"id": e.id, "nombre": e.nombre, "responsable": e.responsable or "",
            "control_calidad": e.control_calidad, "observaciones": e.observaciones or "",
            "completada": e.completada, "fecha_limite": e.fecha_limite,
            "fecha_real": e.fecha_real}


def lote_dict(l: Lote) -> dict:
    # · Convierte un lote (con sus etapas) a diccionario para la respuesta JSON.
    return {"id": l.id, "codigo": l.codigo, "producto": l.producto,
            "cantidad": l.cantidad, "unidad": l.unidad, "responsable": l.responsable,
            "creado_en": l.creado_en, "estado": estado_lote(l),
            "etapas": [etapa_dict(e) for e in l.etapas]}


def lote_por_codigo(db: Session, codigo: str) -> Lote:
    l = db.query(Lote).filter(Lote.codigo == codigo).first()
    if not l:
        raise HTTPException(404, "Lote no encontrado")
    return l


def crear_lote(db: Session, d: LoteIn) -> Lote:
    # · Código único con la fecha y 6 caracteres aleatorios, por ejemplo LOT-20261019-A1B2C3.
    codigo = f"LOT-{ahora():%Y%m%d}-{secrets.token_hex(3).upper()}"
    l = Lote(codigo=codigo, producto=d.producto, cantidad=d.cantidad,
             unidad=d.unidad, responsable=d.responsable)
    # · Cada lote nace con las etapas base y su fecha límite.
    for i, (nombre, dias) in enumerate(ETAPAS_BASE):
        l.etapas.append(EtapaLote(orden=i, nombre=nombre,
                                  fecha_limite=ahora() + timedelta(days=dias)))
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


def actualizar_etapa(db: Session, etapa_id: int, d: EtapaIn) -> Lote:
    e = db.get(EtapaLote, etapa_id)
    if not e:
        raise HTTPException(404, "Etapa no encontrada")
    # · Solo se modifican los campos que llegaron en la petición.
    for campo in ("responsable", "control_calidad", "observaciones"):
        v = getattr(d, campo)
        if v is not None:
            setattr(e, campo, v)
    if d.completada is not None:
        e.completada = d.completada
        e.fecha_real = ahora() if d.completada else None
    db.commit()
    return e.lote
