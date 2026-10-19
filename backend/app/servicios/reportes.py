# · Datos del panel general y de los reportes.
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.configuracion import FE_KM, FE_KWH, UTC_OFFSET_HORAS
from app.modelos_db import ConsumoEnergia, Lote, Pedido, ahora
from app.modelos_poo.huella import HuellaCarbono
from app.servicios.alertas import alertas_consumo, alertas_lotes
from app.servicios.lotes import estado_lote


DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _inicio_dia(dias_atras: int = 0):
    # · Medianoche (hora local del negocio) de hace N días, expresada en UTC como guarda la base.
    local = ahora() + timedelta(hours=UTC_OFFSET_HORAS)
    medianoche = local.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=dias_atras)
    return medianoche - timedelta(hours=UTC_OFFSET_HORAS)


def _variacion(actual: float, anterior: float):
    # · Cambio porcentual frente al periodo anterior; None si no hay base de comparación.
    if not anterior:
        return None
    return round((actual - anterior) / anterior * 100, 1)


def _produccion(db: Session, desde, hasta) -> float:
    # · Unidades registradas en lotes creados dentro del rango.
    total = (db.query(func.coalesce(func.sum(Lote.cantidad), 0))
             .filter(Lote.creado_en >= desde, Lote.creado_en < hasta).scalar())
    return float(total or 0)


def _costo_operacion(db: Session, desde, hasta) -> float:
    # · Energía consumida (kWh x tarifa) + tarifas de transporte de pedidos no cancelados.
    energia = (db.query(func.coalesce(func.sum(ConsumoEnergia.kwh * ConsumoEnergia.tarifa_kwh), 0))
               .filter(ConsumoEnergia.fecha >= desde, ConsumoEnergia.fecha < hasta).scalar())
    transporte = (db.query(func.coalesce(func.sum(Pedido.tarifa), 0))
                  .filter(Pedido.creado_en >= desde, Pedido.creado_en < hasta,
                          Pedido.estado != "Cancelado").scalar())
    return float(energia or 0) + float(transporte or 0)


def _iso(fecha):
    # · Fecha UTC como texto con "Z" para que el navegador la convierta a la hora local.
    return fecha.isoformat() + "Z" if fecha else None


def _actividad_reciente(db: Session, limite: int = 4) -> list:
    # · Últimos movimientos de pedidos, lotes y consumos, mezclados y ordenados por fecha.
    eventos = []
    for p in db.query(Pedido).order_by(Pedido.creado_en.desc()).limit(limite):
        eventos.append({"tipo": "pedido", "titulo": f"Pedido #{p.id} · {p.cliente}",
                        "detalle": f"{p.origen} → {p.destino} · {p.estado}", "fecha": p.creado_en})
    for l in db.query(Lote).order_by(Lote.creado_en.desc()).limit(limite):
        eventos.append({"tipo": "lote", "titulo": f"Lote {l.codigo} registrado",
                        "detalle": f"{l.producto} · {l.cantidad:g} {l.unidad}", "fecha": l.creado_en})
    for c in db.query(ConsumoEnergia).order_by(ConsumoEnergia.fecha.desc()).limit(limite):
        eventos.append({"tipo": "energia", "titulo": f"Consumo registrado · {c.maquina}",
                        "detalle": f"{c.proceso}: {c.kwh:g} kWh", "fecha": c.fecha})
    eventos = [e for e in eventos if e["fecha"]]
    eventos.sort(key=lambda e: e["fecha"], reverse=True)
    return [{**e, "fecha": _iso(e["fecha"])} for e in eventos[:limite]]


def resumen_panel(db: Session) -> dict:
    lotes = db.query(Lote).all()
    en_proceso = sum(1 for l in lotes if estado_lote(l) != "Entregado")
    # · Pedidos activos: los que están pendientes o en ruta.
    activos = db.query(Pedido).filter(Pedido.estado.in_(["Pendiente", "En ruta"])).count()
    # · Energía consumida en los últimos 30 días.
    desde = ahora() - timedelta(days=30)
    kwh = sum(c.kwh for c in db.query(ConsumoEnergia).filter(ConsumoEnergia.fecha >= desde))
    alertas = alertas_lotes(db) + alertas_consumo(db)

    # · Producción de hoy frente a ayer.
    hoy, ayer = _inicio_dia(0), _inicio_dia(1)
    manana = hoy + timedelta(days=1)
    prod_hoy = _produccion(db, hoy, manana)
    prod_ayer = _produccion(db, ayer, hoy)

    # · Pedidos en ruta, y pedidos creados esta semana frente a la anterior.
    en_transito = db.query(Pedido).filter(Pedido.estado == "En ruta").count()
    sem_actual = db.query(Pedido).filter(Pedido.creado_en >= _inicio_dia(6), Pedido.creado_en < manana).count()
    sem_previa = db.query(Pedido).filter(Pedido.creado_en >= _inicio_dia(13), Pedido.creado_en < _inicio_dia(6)).count()

    # · Costo de operación de los últimos 30 días frente a los 30 anteriores.
    inicio_30, inicio_60 = _inicio_dia(29), _inicio_dia(59)
    costo = _costo_operacion(db, inicio_30, manana)
    costo_previo = _costo_operacion(db, inicio_60, inicio_30)

    # · Producción de los últimos 7 días (una barra por día).
    local_hoy = ahora() + timedelta(hours=UTC_OFFSET_HORAS)
    semana = []
    for i in range(6, -1, -1):
        ini = _inicio_dia(i)
        dia = local_hoy - timedelta(days=i)
        semana.append({"dia": DIAS_SEMANA[dia.weekday()], "valor": _produccion(db, ini, ini + timedelta(days=1))})

    return {"lotes": len(lotes), "lotes_en_proceso": en_proceso, "pedidos_activos": activos,
            "kwh_30d": round(kwh, 1), "alertas": alertas,
            "produccion_hoy": prod_hoy, "produccion_variacion": _variacion(prod_hoy, prod_ayer),
            "ordenes_transito": en_transito, "ordenes_activas": activos,
            "ordenes_variacion": _variacion(sem_actual, sem_previa),
            "costo_operacion": round(costo), "costo_variacion": _variacion(costo, costo_previo),
            "semana": semana, "actividad": _actividad_reciente(db)}


def huella_carbono(db: Session) -> dict:
    kwh = sum(c.kwh for c in db.query(ConsumoEnergia).all())
    # · Los pedidos cancelados no cuentan para los km recorridos.
    km = sum(p.distancia_km for p in db.query(Pedido).filter(Pedido.estado != "Cancelado"))
    return HuellaCarbono(FE_KWH, FE_KM).calcular(kwh, km)
