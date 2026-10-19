# · Datos del panel general y de los reportes.
from datetime import timedelta

from sqlalchemy.orm import Session

from app.configuracion import FE_KM, FE_KWH
from app.modelos_db import ConsumoEnergia, Lote, Pedido, ahora
from app.modelos_poo.huella import HuellaCarbono
from app.servicios.alertas import alertas_consumo, alertas_lotes
from app.servicios.lotes import estado_lote


def resumen_panel(db: Session) -> dict:
    lotes = db.query(Lote).all()
    en_proceso = sum(1 for l in lotes if estado_lote(l) != "Entregado")
    # · Pedidos activos: los que están pendientes o en ruta.
    activos = db.query(Pedido).filter(Pedido.estado.in_(["Pendiente", "En ruta"])).count()
    # · Energía consumida en los últimos 30 días.
    desde = ahora() - timedelta(days=30)
    kwh = sum(c.kwh for c in db.query(ConsumoEnergia).filter(ConsumoEnergia.fecha >= desde))
    alertas = alertas_lotes(db) + alertas_consumo(db)
    return {"lotes": len(lotes), "lotes_en_proceso": en_proceso, "pedidos_activos": activos,
            "kwh_30d": round(kwh, 1), "alertas": alertas}


def huella_carbono(db: Session) -> dict:
    kwh = sum(c.kwh for c in db.query(ConsumoEnergia).all())
    # · Los pedidos cancelados no cuentan para los km recorridos.
    km = sum(p.distancia_km for p in db.query(Pedido).filter(Pedido.estado != "Cancelado"))
    return HuellaCarbono(FE_KWH, FE_KM).calcular(kwh, km)
