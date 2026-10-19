# · Generación de alertas: etapas vencidas y consumos de energía fuera de lo normal.
from sqlalchemy.orm import Session

from app.modelos_db import ConsumoEnergia, EtapaLote, ahora
from app.modelos_poo.alerta import Alerta


def alertas_lotes(db: Session) -> list:
    # · Etapas sin completar cuya fecha límite ya pasó.
    vencidas = (db.query(EtapaLote)
                .filter(EtapaLote.completada.is_(False), EtapaLote.fecha_limite < ahora()).all())
    return [Alerta("Retraso",
                   f"Lote {e.lote.codigo}: etapa '{e.nombre}' vencida el {e.fecha_limite:%d/%m/%Y}").a_dict()
            for e in vencidas]


def alertas_consumo(db: Session) -> list:
    # · Alerta si un consumo supera en más de 30 % el promedio previo de la misma máquina y proceso.
    # · Se necesitan al menos 3 registros anteriores para tener un promedio.
    out, hist = [], {}
    for c in db.query(ConsumoEnergia).order_by(ConsumoEnergia.fecha).all():
        prev = hist.setdefault((c.maquina, c.proceso), [])
        if len(prev) >= 3:
            prom = sum(prev) / len(prev)
            if c.kwh > 1.3 * prom:
                out.append(Alerta("Consumo elevado",
                                  f"{c.maquina} / {c.proceso}: {c.kwh:.1f} kWh frente a un promedio de "
                                  f"{prom:.1f} kWh ({c.fecha:%d/%m/%Y})").a_dict())
        prev.append(c.kwh)
    # · Solo las 20 más recientes.
    return out[-20:]
