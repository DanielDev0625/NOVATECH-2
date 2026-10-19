# · Lógica de negocio de eficiencia energética: tarifas, consumos, resumen y recomendación.
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.esquemas.energia import ConsumoIn, TarifaIn
from app.modelos_db import ConsumoEnergia, TarifaElectrica, ahora
from app.modelos_poo.tarifas import RecomendadorTarifa
from app.servicios.lotes import lote_por_codigo


def crear_tarifa(db: Session, d: TarifaIn) -> TarifaElectrica:
    # · Las horas deben estar entre 0 y 24.
    if not (0 <= d.hora_inicio <= 23 and 1 <= d.hora_fin <= 24):
        raise HTTPException(400, "Horas fuera de rango")
    t = TarifaElectrica(**d.model_dump())
    db.add(t)
    db.commit()
    return t


def crear_consumo(db: Session, d: ConsumoIn) -> ConsumoEnergia:
    lote = lote_por_codigo(db, d.lote_codigo) if d.lote_codigo else None
    c = ConsumoEnergia(maquina=d.maquina, proceso=d.proceso, kwh=d.kwh,
                       tarifa_kwh=d.tarifa_kwh, lote_id=lote.id if lote else None)
    db.add(c)
    db.commit()
    return c


def _redondear(filas) -> list:
    # · Redondea a 2 decimales todos los valores decimales de cada fila.
    return [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in x.items()} for x in filas]


def resumen_energia(db: Session) -> dict:
    # · Agrupa el consumo por proceso (con comparativa de los últimos 30 días contra los 30 anteriores)
    # · y por lote.
    hoy = ahora()
    ini, ini_prev = hoy - timedelta(days=30), hoy - timedelta(days=60)
    por_proceso, por_lote = {}, {}
    for c in db.query(ConsumoEnergia).all():
        costo = c.kwh * c.tarifa_kwh
        p = por_proceso.setdefault(c.proceso, {"proceso": c.proceso, "kwh": 0, "costo": 0,
                                               "kwh_actual": 0, "kwh_previo": 0})
        p["kwh"] += c.kwh
        p["costo"] += costo
        if c.fecha >= ini:
            p["kwh_actual"] += c.kwh
        elif c.fecha >= ini_prev:
            p["kwh_previo"] += c.kwh
        if c.lote:
            l = por_lote.setdefault(c.lote.codigo, {"lote": c.lote.codigo, "kwh": 0, "costo": 0})
            l["kwh"] += c.kwh
            l["costo"] += costo
    return {"por_proceso": _redondear(por_proceso.values()), "por_lote": _redondear(por_lote.values())}


def recomendacion_energia(db: Session) -> dict:
    return RecomendadorTarifa().recomendar(db.query(TarifaElectrica).all())
